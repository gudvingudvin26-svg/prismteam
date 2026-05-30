"""WebSocket-консьюмер для интерактивных квизов: аутентификация, события, таймеры, чат."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .redis_utils import get_timer_manager
from .observer import game_observer
import logging

logger = logging.getLogger('ws')


class QuizConsumer(AsyncWebsocketConsumer):
    """Асинхронный консьюмер для квизов: групповые события, таймеры, подсчёт очков."""

    async def connect(self):
        """Подключение: аутентификация по JWT-токену, инициализация группы, подписка на события."""
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model

        token = self.scope['query_string'].decode().split('=')[-1] if '=' in self.scope['query_string'].decode() else None
        if token:
            user = await self.get_user_from_token(token)
            if not user:
                await self.close()
                return
            self.scope['user'] = user
        else:
            await self.close()
            return

        self.quiz_id = self.scope['url_route']['kwargs'].get('quiz_id', 'global')
        self.room_group_name = f'quiz_{self.quiz_id}'
        self.timer_manager = get_timer_manager()
        self.user_scores = {}

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self._on_question_started = lambda **kwargs: self.channel_layer.group_send(
            self.room_group_name, {'type': 'question_started_event', 'question_number': kwargs.get('question_number'), 'timer': kwargs.get('timer')})
        self._on_game_finished = lambda **kwargs: self.channel_layer.group_send(
            self.room_group_name, {'type': 'game_finished_event', 'message': 'Игра завершена!'})
        game_observer.subscribe('question_started', self._on_question_started)
        game_observer.subscribe('game_finished', self._on_game_finished)

        await self.channel_layer.group_send(self.room_group_name, {'type': 'user_joined', 'username': self._get_display_name(), 'channel': self.channel_name})

    async def disconnect(self, code):
        """Отключение: отписка от событий, уведомление группы, удаление из канала."""
        game_observer.unsubscribe('question_started', self._on_question_started)
        game_observer.unsubscribe('game_finished', self._on_game_finished)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'user_left', 'username': self._get_display_name(), 'channel': self.channel_name})
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Приём сообщения: парсинг JSON, маршрутизация по типу события на обработчики."""
        if not text_data:
            return
        try:
            data = json.loads(text_data)
            event_type = data.get('type', 'message')
            handler_map = {
                'submit_answer': self._handle_answer, 'get_question': self._handle_get_question,
                'get_leaderboard': self._handle_leaderboard, 'next_question': self._handle_next_question,
                'start_quiz': self._handle_start_quiz, 'chat_message': self._handle_chat,
            }
            handler = handler_map.get(event_type, self._handle_unknown)
            await handler(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))

    @database_sync_to_async
    def get_user_from_token(self, token):
        """[DB] Валидация JWT-токена и получение пользователя по user_id."""
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            User = get_user_model()
            return User.objects.get(id=user_id)
        except Exception:
            return None

    def _get_display_name(self) -> str:
        """Возврат отображаемого имени: username для авторизованных или 'User_<channel>' для анонимов."""
        user = self.scope.get('user')
        if user and user.is_authenticated:
            return user.username
        return f'User_{self.channel_name[:8]}'

    async def _handle_start_quiz(self, data: dict):
        """Обработчик 'start_quiz': запуск таймера первого вопроса, рассылка 'quiz_started'."""
        duration = await self._get_quiz_timer_duration()
        self.timer_manager.start_question_timer(self.quiz_id, question_number=1, duration=duration)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'quiz_started', 'quiz_id': self.quiz_id})

    async def _handle_get_question(self, data: dict):
        """Обработчик 'get_question': отправка данных вопроса и таймера клиенту."""
        question_number = data.get('question_number', 1)
        question_data = await self._get_question_data(question_number)
        if question_data:
            timer_info = self.timer_manager.get_question_timer(self.quiz_id, question_number)
            await self.send(text_data=json.dumps({
                'type': 'question', 'question_number': question_number, 'timer': timer_info.get('remaining', 30),
                'text': question_data.get('text'),
                'answers': [{'id': ans['id'], 'text': ans['text']} for ans in question_data.get('answer_options', [])]
            }))
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Вопрос не найден или игра завершена.'}))

    async def _handle_answer(self, data: dict):
        """Обработчик 'submit_answer': проверка таймера, валидация ответа, начисление очков, рассылка результата."""
        answer_id = data.get('answer_id')
        question_number = data.get('question_number', 1)
        remaining_time = self.timer_manager.get_time_remaining(self.quiz_id, question_number)
        if remaining_time <= 0:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Время на ответ истекло!'}))
            return
        is_correct, points = await self._verify_answer(answer_id, remaining_time)
        username = self._get_display_name()
        if username not in self.user_scores:
            self.user_scores[username] = 0
        if is_correct:
            self.user_scores[username] += points
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'answer_submitted', 'username': username, 'answer_id': answer_id,
            'is_correct': is_correct, 'points': points, 'total_score': self.user_scores[username], 'channel': self.channel_name
        })

    async def _handle_next_question(self, data: dict):
        """Обработчик 'next_question': запуск таймера нового вопроса, уведомление группы."""
        next_num = data.get('question_number', 1)
        duration = await self._get_quiz_timer_duration()
        self.timer_manager.start_question_timer(self.quiz_id, question_number=next_num, duration=duration)
        game_observer.notify('question_started', question_number=next_num, timer=duration)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'next_question', 'question_number': next_num, 'sender': self.channel_name})

    async def _handle_leaderboard(self, data: dict):
        """Обработчик 'get_leaderboard': отправка топ-10 участников по очкам."""
        scores = self._get_leaderboard_data()
        await self.send(text_data=json.dumps({'type': 'leaderboard', 'scores': scores}))

    async def _handle_chat(self, data: dict):
        """Обработчик 'chat_message': рассылка сообщения чата всей группе."""
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'username': self._get_display_name(), 'message': data.get('message', '')})

    async def _handle_unknown(self, data: dict):
        """Обработчик неизвестных событий: возврат ошибки клиенту."""
        await self.send(text_data=json.dumps({'type': 'error', 'message': f"Unknown event type: {data.get('type')}"}))

    @database_sync_to_async
    def _get_quiz_timer_duration(self) -> int:
        """[DB] Получение длительности таймера из квиза или 30 сек по умолчанию."""
        from .models import Quiz
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            return quiz.timer if quiz.timer else 30
        except ObjectDoesNotExist:
            return 30

    @database_sync_to_async
    def _get_question_data(self, question_number: int) -> dict | None:
        """[DB] Получение сериализованных данных вопроса по номеру (1-индексированный)."""
        from .models import Question
        from .serializers import QuestionSerializer
        try:
            questions = Question.objects.filter(quiz_id=self.quiz_id).order_by('order')
            if question_number <= len(questions):
                question = questions[question_number - 1]
                serializer = QuestionSerializer(question)
                return serializer.data
            return None
        except Exception:
            return None

    @database_sync_to_async
    def _verify_answer(self, answer_id: int, remaining_time: int) -> tuple[bool, int]:
        """[DB] Проверка правильности ответа и расчёт баллов: 100 базовых + 3×секунды бонуса."""
        from .models import AnswerOption
        try:
            option = AnswerOption.objects.get(id=answer_id)
            if option.is_correct:
                return True, (100 + remaining_time * 3)
            return False, 0
        except ObjectDoesNotExist:
            return False, 0

    def _get_leaderboard_data(self) -> list:
        """Формирование топ-10 участников: сортировка по очкам, возврат списка словарей."""
        sorted_scores = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        return [{"participant_name": name, "score": score} for name, score in sorted_scores[:10]]

    # === Обработчики событий от channel_layer (групповая рассылка) ===

    async def user_joined(self, event):
        """Событие 'user_joined': уведомление клиента о подключении участника."""
        await self.send(text_data=json.dumps({'type': 'user_joined', 'username': event['username']}))

    async def user_left(self, event):
        """Событие 'user_left': уведомление клиента об отключении участника."""
        await self.send(text_data=json.dumps({'type': 'user_left', 'username': event['username']}))

    async def answer_submitted(self, event):
        """Событие 'answer_submitted': пересылка результата ответа клиенту."""
        await self.send(text_data=json.dumps({
            'type': 'answer_submitted', 'username': event['username'], 'answer_id': event['answer_id'],
            'is_correct': event['is_correct'], 'points': event['points'], 'total_score': event.get('total_score', 0)
        }))

    async def next_question(self, event):
        """Событие 'next_question': уведомление о переходе (игнорирует свои же сообщения)."""
        if event['sender'] != self.channel_name:
            await self.send(text_data=json.dumps({'type': 'next_question', 'question_number': event['question_number']}))

    async def quiz_started(self, event):
        """Событие 'quiz_started': подтверждение старта квиза клиенту."""
        await self.send(text_data=json.dumps({'type': 'quiz_started', 'quiz_id': event['quiz_id']}))

    async def chat_message(self, event):
        """Событие 'chat_message': пересылка сообщения чата клиенту."""
        await self.send(text_data=json.dumps({'type': 'chat_message', 'username': event['username'], 'message': event['message']}))

    async def question_started_event(self, event):
        """Событие 'question_started_event': уведомление о старте вопроса с таймером."""
        await self.send(text_data=json.dumps({'type': 'question_started', 'question_number': event['question_number'], 'timer': event.get('timer')}))

    async def game_finished_event(self, event):
        """Событие 'game_finished_event': уведомление о завершении квиза."""
        await self.send(text_data=json.dumps({'type': 'game_finished', 'message': event['message']}))