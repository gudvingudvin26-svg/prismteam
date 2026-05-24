import random
import string
import logging
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import QuizSession, ParticipantAnswer
from .serializers import QuizSessionSerializer
from app_modules.quiz.models import Question, AnswerOption

quiz_log = logging.getLogger('quiz_log')


class QuizSessionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSessionSerializer

    def get_permissions(self):
        if self.action in ['join', 'retrieve', 'answer', 'my_result', 'results']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return QuizSession.objects.filter(quiz__created_by=self.request.user)
        return QuizSession.objects.none()

    def create(self, request, *args, **kwargs):
        print("=== CREATE SESSION ===")
        print("Request data:", request.data)
        print("User:", request.user)
        print("User authenticated:", request.user.is_authenticated)

        quiz_id = request.data.get('quiz')
        if not quiz_id:
            return Response({'error': 'quiz_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            from app_modules.quiz.models import Quiz
            quiz = Quiz.objects.get(id=quiz_id, created_by=request.user)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

        code = ''.join(random.choices(string.digits, k=6))

        while QuizSession.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.digits, k=6))

        session = QuizSession.objects.create(
            quiz=quiz,
            code=code,
            status='waiting'
        )

        print(f"Session created: id={session.id}, code={session.code}")

        return Response({
            'id': session.id,
            'code': session.code,
            'quiz': session.quiz.id,
            'status': session.status
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny()], url_path='join')
    def join(self, request):
        code = request.data.get('code')
        nickname = request.data.get('nickname')

        print(f"=== JOIN SESSION ===")
        print(f"Code: {code}")
        print(f"Nickname: {nickname}")

        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not nickname:
            return Response({'error': 'Nickname is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = QuizSession.objects.get(code=code, status='waiting')
            session.participant_name = nickname
            session.save()

            print(f"Session {session.id} updated with name: {nickname}")
            return Response({
                'session_id': session.id,
                'code': session.code,
                'quiz_title': session.quiz.title
            }, status=status.HTTP_200_OK)
        except QuizSession.DoesNotExist:
            print(f"Session with code {code} not found")
            return Response({'error': 'Сессия с таким кодом не найдена'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        session = self.get_object()
        session.status = 'active'
        session.started_at = timezone.now()
        session.save()
        quiz_log.info(f"Session {session.id} started successfully")
        return Response({'status': 'started'})

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        session = self.get_object()
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()
        quiz_log.info(f"Session {session.id} ended successfully")
        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny()])
    def answer(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')

        try:
            question = Question.objects.get(id=question_id)
            answer = AnswerOption.objects.get(id=answer_id) if answer_id and answer_id != -1 else None
            is_correct = answer.is_correct if answer and answer_id != -1 else False

            ParticipantAnswer.objects.create(
                session=session,
                question=question,
                answer=answer,
                is_correct=is_correct
            )

            return Response({
                'status': 'answer received',
                'is_correct': is_correct
            })
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=404)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def my_result(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        answers = ParticipantAnswer.objects.filter(session=session)
        total_questions = session.quiz.questions.count()
        correct_answers = answers.filter(is_correct=True).count()

        all_sessions = QuizSession.objects.filter(quiz=session.quiz)
        all_answers = ParticipantAnswer.objects.filter(session__in=all_sessions)

        from collections import defaultdict
        scores = defaultdict(int)
        for ans in all_answers:
            if ans.is_correct:
                scores[ans.session.id] += 1

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rank = 1
        for i, (sid, score) in enumerate(sorted_scores):
            if sid == session.id:
                rank = i + 1
                break

        return Response({
            'score': correct_answers,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'rank': rank
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def results(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        all_sessions = QuizSession.objects.filter(quiz=session.quiz)

        from collections import defaultdict
        scores = defaultdict(int)
        for s in all_sessions:
            correct = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
            scores[s.id] = correct

        sorted_sessions = sorted(all_sessions, key=lambda x: scores[x.id], reverse=True)

        results = []
        for i, s in enumerate(sorted_sessions):
            display_name = s.participant_name if s.participant_name else f'Участник {s.id}'
            results.append({
                'id': s.id,
                'participant_name': display_name,
                'score': scores[s.id],
                'total_questions': session.quiz.questions.count(),
                'rank': i + 1
            })

        return Response(results)

    def retrieve(self, request, *args, **kwargs):
        try:
            session = self.get_object()
        except:
            if request.user.is_authenticated:
                raise
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated:
            return Response({
                'id': session.id,
                'code': session.code,
                'status': session.status,
                'quiz_title': session.quiz.title
            })

        quiz = session.quiz
        question_index = int(request.GET.get('index', 0))
        questions_list = list(quiz.questions.all())

        if question_index >= len(questions_list):
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
            return Response({'finished': True})

        current_question = questions_list[question_index]

        return Response({
            'id': current_question.id,
            'text': current_question.text,
            'timer': 30,
            'index': question_index,
            'answers': [
                {'id': ans.id, 'text': ans.text}
                for ans in current_question.answer_options.all()
            ]
        })