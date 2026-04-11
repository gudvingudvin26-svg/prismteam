import json
from channels.generic.websocket import AsyncWebsocketConsumer


class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope['url_route']['kwargs'].get('quiz_id', 'global')
        self.room_group_name = f'quiz_{self.quiz_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self._get_display_name(),
                'channel': self.channel_name
            }
        )

    async def disconnect(self, code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self._get_display_name(),
                'channel': self.channel_name
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
            event_type = data.get('type', 'message')

            handler_map = {
                'submit_answer': self._handle_answer,
                'get_question': self._handle_get_question,
                'get_leaderboard': self._handle_leaderboard,
                'next_question': self._handle_next_question,
                'start_quiz': self._handle_start_quiz,
                'chat_message': self._handle_chat,
            }

            handler = handler_map.get(event_type, self._handle_unknown)
            await handler(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    def _get_display_name(self) -> str:
        user = self.scope.get('user')
        if user and user.is_authenticated:
            return user.username
        return f'User_{self.channel_name[:8]}'

    async def _handle_answer(self, data: dict):
        answer_id = data.get('answer_id')
        time_taken = data.get('time_taken', 0)
        is_correct = data.get('is_correct', False)
        points = data.get('points', 0) if is_correct else 0

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'answer_submitted',
                'username': self._get_display_name(),
                'answer_id': answer_id,
                'is_correct': is_correct,
                'points': points,
                'channel': self.channel_name
            }
        )

    async def _handle_get_question(self, data: dict):
        question_data = await self._get_question_data(data.get('question_number', 1))
        if question_data:
            await self.send(text_data=json.dumps({
                'type': 'question',
                'question_number': data.get('question_number', 1),
                **question_data
            }))

    async def _handle_leaderboard(self, data: dict):
        scores = await self._get_leaderboard_data()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard',
            'scores': scores
        }))

    async def _handle_next_question(self, data: dict):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'next_question',
                'question_number': data.get('question_number', 1),
                'sender': self.channel_name
            }
        )

    async def _handle_start_quiz(self, data: dict):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'quiz_started',
                'quiz_id': self.quiz_id
            }
        )

    async def _handle_chat(self, data: dict):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': self._get_display_name(),
                'message': data.get('message', '')
            }
        )

    async def _handle_unknown(self, data: dict):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': f"Unknown event type: {data.get('type')}"
        }))

    async def _get_question_data(self, question_number: int) -> dict | None:
        return None

    async def _get_leaderboard_data(self) -> list:
        return []

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username']
        }))

    async def answer_submitted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer_submitted',
            'username': event['username'],
            'answer_id': event['answer_id'],
            'is_correct': event['is_correct'],
            'points': event['points']
        }))

    async def next_question(self, event):
        if event['channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'next_question',
                'question_number': event['question_number']
            }))

    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'quiz_started',
            'quiz_id': event['quiz_id']
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'username': event['username'],
            'message': event['message']
        }))
