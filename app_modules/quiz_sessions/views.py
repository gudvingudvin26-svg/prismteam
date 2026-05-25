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
        if self.action in ['join', 'retrieve', 'answer', 'my_result', 'results', 'questions_stats']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return QuizSession.objects.filter(quiz__created_by=self.request.user)
        return QuizSession.objects.none()

    def create(self, request, *args, **kwargs):
        quiz_id = request.data.get('quiz')
        if not quiz_id:
            return Response({'error': 'quiz_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            from app_modules.quiz.models import Quiz
            quiz = Quiz.objects.get(id=quiz_id, created_by=request.user)
        except Quiz.DoesNotExist:
            return Response({'error': f'Quiz with id {quiz_id} not found for this user'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error_at_quiz_fetch': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        code = ''.join(random.choices(string.digits, k=6))

        try:
            while QuizSession.objects.filter(code=code).exists():
                code = ''.join(random.choices(string.digits, k=6))
        except Exception as e:
            return Response({'error_at_code_check': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            session = QuizSession.objects.create(
                quiz=quiz,
                code=code,
                status='waiting'
            )
            return Response({
                'id': session.id,
                'code': session.code,
                'quiz': session.quiz.id,
                'status': session.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO quiz_sessions_quizsession (quiz_id, code, status, started_at) "
                        "VALUES (%s, %s, %s::quiz_status, NOW()) RETURNING id;",
                        [quiz.id, code, 'waiting']
                    )
                    row = cursor.fetchone()
                    session_id = row[0]

                return Response({
                    'id': session_id,
                    'code': code,
                    'quiz': quiz.id,
                    'status': 'waiting'
                }, status=status.HTTP_201_CREATED)
            except Exception as raw_enum_error:
                return Response({
                    'error_at_session_create': str(e),
                    'fallback_error': str(raw_enum_error),
                    'hint': 'Убедитесь, что значение "waiting" присутствует в вашем ENUM на уровне базы данных.'
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny()], url_path='join')
    def join(self, request):
        code = request.data.get('code')
        nickname = request.data.get('nickname')

        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not nickname:
            return Response({'error': 'Nickname is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = QuizSession.objects.get(code=code, status='waiting')

            return Response({
                'session_id': session.id,
                'code': session.code,
                'quiz_title': session.quiz.title
            }, status=status.HTTP_200_OK)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Сессия с таким кодом не найдена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error_during_join': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        participant_names = defaultdict(str)

        for s in all_sessions:
            correct = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
            scores[s.id] = correct
            if hasattr(s, 'participant_name') and s.participant_name:
                participant_names[s.id] = s.participant_name

        sorted_sessions = sorted(all_sessions, key=lambda x: scores[x.id], reverse=True)

        results = []
        for i, s in enumerate(sorted_sessions):
            display_name = participant_names.get(s.id, f'Участник {s.id}')
            results.append({
                'id': s.id,
                'participant_name': display_name,
                'score': scores[s.id],
                'total_questions': session.quiz.questions.count(),
                'rank': i + 1
            })

        return Response(results)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def questions_stats(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        questions = session.quiz.questions.all()

        stats = []
        for q in questions:
            answers = ParticipantAnswer.objects.filter(session=session, question=q)
            total = answers.count()
            correct = answers.filter(is_correct=True).count()

            stats.append({
                'question_id': q.id,
                'question_text': q.text,
                'total_answers': total,
                'correct_count': correct,
                'correct_percent': round(correct / total * 100, 1) if total > 0 else 0
            })

        return Response(stats)

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