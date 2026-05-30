"""ViewSet для управления сессиями квизов: создание, присоединение, ответы, статистика."""
import random
import string
import logging
import time
from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import QuizSession, ParticipantAnswer
from .serializers import QuizSessionSerializer
from app_modules.quiz.models import Quiz

quiz_log = logging.getLogger('quiz_log')


class QuizSessionViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций с сессиями квизов и обработки игровых действий."""
    serializer_class = QuizSessionSerializer

    def get_permissions(self):
        """Динамическое определение прав: публичный доступ для игровых действий, аутентификация для управления."""
        if self.action in ['join', 'retrieve', 'answer', 'my_result', 'results', 'questions_stats', 'check_completed']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Возврат всех сессий для административных операций."""
        return QuizSession.objects.all()

    def create(self, request, *args, **kwargs):
        """POST create: создание новой сессии для квиза с генерацией уникального кода."""
        logger = logging.getLogger('quiz_log')
        logger.info("=" * 50)
        logger.info("CREATE SESSION CALLED")
        logger.info(f"Request data: {request.data}")
        logger.info(f"User: {request.user}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info("=" * 50)

        quiz_id = request.data.get('quiz_id')
        if not quiz_id:
            quiz_id = request.data.get('quiz')
        if not quiz_id:
            logger.error("No quiz_id in request")
            return Response({'error': 'quiz_id is required'}, status=400)
        if not request.user.is_authenticated:
            logger.error("User not authenticated")
            return Response({'error': 'Authentication required'}, status=401)
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            logger.info(f"Found quiz: {quiz.id} - {quiz.title}")
        except Quiz.DoesNotExist:
            logger.error(f"Quiz {quiz_id} not found")
            return Response({'error': 'Квиз не найден'}, status=404)

        while True:
            timestamp_part = str(int(time.time() * 1000))[-3:]
            random_part = ''.join(random.choices(string.digits, k=3))
            code = timestamp_part + random_part
            if not QuizSession.objects.filter(code=code).exists():
                break

        try:
            session = QuizSession.objects.create(quiz=quiz, code=code, status='waiting')
            logger.info(f"Session created: {session.id} with code {code}")
            return Response({'id': session.id, 'code': code, 'quiz': quiz.id, 'status': session.status}, status=201)
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny()], url_path='join')
    def join(self, request):
        """POST join: присоединение участника к сессии по коду с проверкой дубликатов и завершённых прохождений."""
        code = request.data.get('code')
        nickname = request.data.get('nickname')
        if not code or not nickname:
            return Response({'error': 'Code and nickname are required'}, status=400)
        try:
            master_session = QuizSession.objects.filter(code=code, status__in=['waiting', 'active']).first()
            if not master_session:
                return Response({'error': 'Сессия не найдена или уже завершена'}, status=404)
            existing_completed = QuizSession.objects.filter(quiz=master_session.quiz, participant_name=nickname, is_completed=True).first()
            if existing_completed:
                return Response({'error': 'Вы уже проходили этот квиз'}, status=400)
            if master_session.quiz.created_by.username == nickname:
                existing_creator_completed = QuizSession.objects.filter(quiz=master_session.quiz, participant_name=nickname, is_completed=True).first()
                if existing_creator_completed:
                    return Response({'error': 'Вы уже проходили этот квиз как создатель'}, status=400)
            existing_player = QuizSession.objects.filter(code=code, participant_name=nickname, is_completed=False).first()
            if existing_player:
                return Response({'session_id': existing_player.id, 'code': existing_player.code, 'quiz_title': existing_player.quiz.title}, status=200)
            player_session = QuizSession.objects.create(quiz=master_session.quiz, code=master_session.code, participant_name=nickname, status='waiting')
            return Response({'session_id': player_session.id, 'code': player_session.code, 'quiz_title': player_session.quiz.title}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """POST start: активация сессии и фиксация времени начала."""
        try:
            session = QuizSession.objects.get(id=pk)
            session.status = 'active'
            session.started_at = timezone.now()
            session.save()
            return Response({'status': 'started'})
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """POST end: завершение сессии, установка флага is_completed и времени окончания."""
        try:
            session = QuizSession.objects.get(id=pk)
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.is_completed = True
            session.save()
            return Response({'status': 'completed'})
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def check_completed(self, request, pk=None):
        """GET check_completed: проверка статуса завершения сессии."""
        try:
            session = QuizSession.objects.get(id=pk)
            return Response({'is_completed': session.is_completed})
        except QuizSession.DoesNotExist:
            return Response({'is_completed': False})

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny()])
    def answer(self, request, pk=None):
        """POST answer: приём ответа участника, проверка правильности и начисление баллов."""
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        if session.is_completed:
            return Response({'error': 'Этот квиз уже пройден'}, status=status.HTTP_400_BAD_REQUEST)
        question_id = request.data.get('question_id')
        answer_ids = request.data.get('answer_ids', [])
        if not answer_ids:
            answer_ids = [request.data.get('answer_id')] if request.data.get('answer_id') else []
        try:
            from app_modules.quiz.models import Question, AnswerOption
            question = Question.objects.get(id=question_id)
            points_per_question = question.points if question.points else 100
            if question.question_type == 'multiple':
                selected_answers = AnswerOption.objects.filter(id__in=answer_ids)
                correct_answers = question.answer_options.filter(is_correct=True)
                correct_answers_ids = set(correct_answers.values_list('id', flat=True))
                selected_ids = set(selected_answers.values_list('id', flat=True))
                user_correct_count = len(selected_ids.intersection(correct_answers_ids))
                total_correct_count = len(correct_answers_ids)
                if total_correct_count > 0:
                    points_per_correct = points_per_question / total_correct_count
                    earned_points = int(points_per_correct * user_correct_count)
                else:
                    earned_points = 0
                is_fully_correct = (selected_ids == correct_answers_ids)
                for answer in selected_answers:
                    ParticipantAnswer.objects.create(session=session, question=question, answer=answer, is_correct=answer.is_correct)
                return Response({'status': 'answer received', 'is_correct': is_fully_correct, 'points_earned': earned_points, 'user_correct_count': user_correct_count, 'total_correct_count': total_correct_count})
            else:
                answer = AnswerOption.objects.get(id=answer_ids[0]) if answer_ids else None
                is_correct = answer.is_correct if answer else False
                earned_points = points_per_question if is_correct else 0
                ParticipantAnswer.objects.create(session=session, question=question, answer=answer, is_correct=is_correct)
                return Response({'status': 'answer received', 'is_correct': is_correct, 'points_earned': earned_points})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def my_result(self, request, pk=None):
        """GET my_result: расчёт результата участника — очки, правильные ответы, место в лидерборде."""
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            answers = ParticipantAnswer.objects.filter(session=session)
            total_points = 0
            correct_answers_count = 0
            for ans in answers:
                if ans.is_correct:
                    correct_answers_count += 1
                    question = ans.question
                    points_per_question = question.points if question.points else 100
                    if question.question_type == 'multiple':
                        correct_answers_for_question = question.answer_options.filter(is_correct=True).count()
                        user_correct_for_question = ParticipantAnswer.objects.filter(session=session, question=question, is_correct=True).count()
                        if correct_answers_for_question > 0:
                            points_per_correct = points_per_question / correct_answers_for_question
                            total_points += int(points_per_correct * user_correct_for_question)
                    else:
                        total_points += points_per_question
            total_questions = session.quiz.questions.count()
            all_sessions = QuizSession.objects.filter(code=session.code, is_completed=True)
            scores = {}
            for s in all_sessions:
                points = 0
                s_answers = ParticipantAnswer.objects.filter(session=s)
                for ans in s_answers:
                    if ans.is_correct:
                        q = ans.question
                        q_points = q.points if q.points else 100
                        if q.question_type == 'multiple':
                            correct_count = q.answer_options.filter(is_correct=True).count()
                            user_correct = ParticipantAnswer.objects.filter(session=s, question=q, is_correct=True).count()
                            if correct_count > 0:
                                points += int((q_points / correct_count) * user_correct)
                        else:
                            points += q_points
                name = s.participant_name if s.participant_name else (s.quiz.created_by.username if s.quiz.created_by else "Организатор")
                scores[name] = points
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            current_name = session.participant_name if session.participant_name else (session.quiz.created_by.username if session.quiz.created_by else "Организатор")
            rank = 1
            for i, (name, points) in enumerate(sorted_scores):
                if name == current_name:
                    rank = i + 1
                    break
            return Response({'score': total_points, 'total_questions': total_questions, 'correct_answers': correct_answers_count, 'rank': rank})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def results(self, request, pk=None):
        """GET results: формирование лидерборда по всем завершённым сессиям квиза."""
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response([], status=404)
        try:
            all_sessions = QuizSession.objects.filter(quiz=session.quiz, is_completed=True)
            players_summary = {}
            for s in all_sessions:
                name = s.participant_name if s.participant_name else (s.quiz.created_by.username if s.quiz.created_by else "Организатор")
                points = 0
                s_answers = ParticipantAnswer.objects.filter(session=s)
                for ans in s_answers:
                    if ans.is_correct:
                        q = ans.question
                        q_points = q.points if q.points else 100
                        if q.question_type == 'multiple':
                            correct_count = q.answer_options.filter(is_correct=True).count()
                            user_correct = ParticipantAnswer.objects.filter(session=s, question=q, is_correct=True).count()
                            if correct_count > 0:
                                points += int((q_points / correct_count) * user_correct)
                        else:
                            points += q_points
                if name not in players_summary or points > players_summary[name]:
                    players_summary[name] = points
            leaderboard = []
            for name, points in players_summary.items():
                leaderboard.append({'participant_name': name, 'score': points, 'id': 0})
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            for i, item in enumerate(leaderboard):
                item['rank'] = i + 1
            return Response(leaderboard)
        except Exception as e:
            return Response([], status=400)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def questions_stats(self, request, pk=None):
        """GET questions_stats: статистика по вопросам — количество ответов и процент правильных."""
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response([])
        try:
            questions = session.quiz.questions.all()
            stats = []
            related_sessions = QuizSession.objects.filter(code=session.code, is_completed=True)
            for q in questions:
                total_answers = ParticipantAnswer.objects.filter(session__in=related_sessions, question=q).count()
                correct_count = ParticipantAnswer.objects.filter(session__in=related_sessions, question=q, is_correct=True).count()
                correct_percent = int((correct_count / total_answers * 100)) if total_answers > 0 else 0
                stats.append({'question_id': q.id, 'question_text': q.text, 'total_answers': total_answers, 'correct_count': correct_count, 'correct_percent': correct_percent})
            return Response(stats)
        except Exception:
            return Response([])

    def retrieve(self, request, *args, **kwargs):
        """GET retrieve: получение данных сессии или текущего вопроса для участника/создателя."""
        try:
            session = QuizSession.objects.get(id=kwargs.get('pk'))
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        if session.is_completed:
            return Response({'finished': True, 'is_completed': True})
        if session.participant_name:
            try:
                quiz = session.quiz
                question_index = int(request.GET.get('index', 0))
                questions_list = list(quiz.questions.all().order_by('order'))
                if question_index >= len(questions_list):
                    session.status = 'completed'
                    session.ended_at = timezone.now()
                    session.is_completed = True
                    session.save()
                    return Response({'finished': True, 'is_completed': True})
                current_question = questions_list[question_index]
                timer_value = current_question.timer if current_question.timer else (quiz.timer if quiz.timer else 30)
                return Response({'id': current_question.id, 'text': current_question.text, 'question_type': current_question.question_type, 'timer': timer_value, 'index': question_index, 'answers': [{'id': ans.id, 'text': ans.text} for ans in current_question.answer_options.all()]})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_authenticated or session.quiz.created_by != request.user:
            return Response({'id': session.id, 'code': session.code, 'status': session.status, 'quiz_title': session.quiz.title, 'participant_name': session.participant_name, 'quiz': {'id': session.quiz.id, 'title': session.quiz.title, 'created_by': {'id': session.quiz.created_by.id, 'username': session.quiz.created_by.username}}})
        try:
            quiz = session.quiz
            question_index = int(request.GET.get('index', 0))
            questions_list = list(quiz.questions.all().order_by('order'))
            if question_index >= len(questions_list):
                session.status = 'completed'
                session.ended_at = timezone.now()
                session.is_completed = True
                session.save()
                return Response({'finished': True, 'is_completed': True})
            current_question = questions_list[question_index]
            timer_value = current_question.timer if current_question.timer else (quiz.timer if quiz.timer else 30)
            return Response({'id': current_question.id, 'text': current_question.text, 'question_type': current_question.question_type, 'timer': timer_value, 'index': question_index, 'answers': [{'id': ans.id, 'text': ans.text} for ans in current_question.answer_options.all()]})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)