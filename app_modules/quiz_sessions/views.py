import random
import string
import logging
import time
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import QuizSession, ParticipantAnswer
from .serializers import QuizSessionSerializer
from app_modules.quiz.observer import game_observer

quiz_log = logging.getLogger('quiz_log')


class QuizSessionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSessionSerializer

    def get_permissions(self):
        if self.action in ['join', 'retrieve', 'answer', 'my_result', 'results', 'questions_stats']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return QuizSession.objects.all()

    def create(self, request, *args, **kwargs):
        quiz_id = request.data.get('quiz') or request.data.get('quiz_id')
        if not quiz_id:
            return Response({'error': 'quiz_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            from app_modules.quiz.models import Quiz
            quiz = Quiz.objects.filter(id=quiz_id, created_by=request.user).first()
            if not quiz:
                return Response({'error': 'Квиз не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            timestamp_part = str(int(time.time() * 1000))[-3:]
            random_part = ''.join(random.choices(string.digits, k=3))
            code = timestamp_part + random_part
            if not QuizSession.objects.filter(code=code, status='waiting').exists():
                break

        try:
            session = QuizSession.objects.create(quiz=quiz, code=code, status='waiting')
            return Response({'id': session.id, 'code': code, 'quiz': quiz.id, 'status': session.status},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny()], url_path='join')
    def join(self, request):
        code = request.data.get('code')
        nickname = request.data.get('nickname')

        if not code or not nickname:
            return Response({'error': 'Code and nickname are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            master_session = QuizSession.objects.filter(code=code, participant_name__isnull=True).first()
            if not master_session:
                master_session = QuizSession.objects.filter(code=code).first()

            if not master_session:
                return Response({'error': 'Сессия не найдена'}, status=status.HTTP_404_NOT_FOUND)

            player_session = QuizSession.objects.create(
                quiz=master_session.quiz,
                code=master_session.code,
                participant_name=nickname,
                status='active',
                started_at=timezone.now()
            )

            return Response(
                {'session_id': player_session.id, 'code': player_session.code, 'quiz_title': player_session.quiz.title},
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
            session.status = 'active'
            session.started_at = timezone.now()
            session.save()
            return Response({'status': 'started'})
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
            game_observer.notify('game_finished', session_id=session.id, code=session.code)

            return Response({'status': 'completed'})
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny()])
    def answer(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')

        try:
            from app_modules.quiz.models import Question, AnswerOption
            question = Question.objects.get(id=question_id)
            answer = AnswerOption.objects.get(id=answer_id) if answer_id and answer_id != -1 else None
            is_correct = answer.is_correct if answer and answer_id != -1 else False

            ParticipantAnswer.objects.create(session=session, question=question, answer=answer, is_correct=is_correct)
            return Response({'status': 'answer received', 'is_correct': is_correct})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def my_result(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            answers = ParticipantAnswer.objects.filter(session=session)
            correct_answers = answers.filter(is_correct=True).count()
            total_questions = session.quiz.questions.count()

            all_sessions = QuizSession.objects.filter(code=session.code)
            scores = {}
            for s in all_sessions:
                score = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
                name = s.participant_name if s.participant_name else (s.quiz.created_by.username if s.quiz.created_by else "Организатор")
                scores[name] = score

            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            current_name = session.participant_name if session.participant_name else (session.quiz.created_by.username if session.quiz.created_by else "Организатор")

            rank = 1
            for i, (name, score) in enumerate(sorted_scores):
                if name == current_name:
                    rank = i + 1
                    break

            return Response({
                'score': correct_answers,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'rank': rank
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def results(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        try:
            all_sessions = QuizSession.objects.filter(code=session.code)
            players_summary = {}

            for s in all_sessions:
                name = s.participant_name if s.participant_name else (s.quiz.created_by.username if s.quiz.created_by else "Организатор")
                score = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()

                if name == "Организатор" and score == 0 and all_sessions.exclude(participant_name__isnull=True).exists():
                    continue

                if name not in players_summary or score > players_summary[name]:
                    players_summary[name] = score

            leaderboard = []
            for name, score in players_summary.items():
                leaderboard.append({
                    'participant_name': name,
                    'score': score,
                    'id': 0
                })

            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            for i, item in enumerate(leaderboard):
                item['rank'] = i + 1

            return Response(leaderboard)
        except Exception as e:
            return Response([], status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def questions_stats(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response([])

        try:
            questions = session.quiz.questions.all()
            stats = []
            related_sessions = QuizSession.objects.filter(code=session.code)

            for q in questions:
                total_answers = ParticipantAnswer.objects.filter(session__in=related_sessions, question=q).count()
                correct_count = ParticipantAnswer.objects.filter(session__in=related_sessions, question=q,
                                                                 is_correct=True).count()
                correct_percent = int((correct_count / total_answers * 100)) if total_answers > 0 else 0

                stats.append({
                    'question_id': q.id,
                    'question_text': q.text,
                    'total_answers': total_answers,
                    'correct_count': correct_count,
                    'correct_percent': correct_percent
                })
            return Response(stats)
        except Exception:
            return Response([])

    def retrieve(self, request, *args, **kwargs):
        try:
            session = QuizSession.objects.get(id=kwargs.get('pk'))
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_authenticated or session.quiz.created_by != request.user:
            return Response(
                {'id': session.id, 'code': session.code, 'status': session.status, 'quiz_title': session.quiz.title})

        try:
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
                'answers': [{'id': ans.id, 'text': ans.text} for ans in current_question.answer_options.all()]
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)