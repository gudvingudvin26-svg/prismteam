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
                return Response({
                    'error': f'Квиз с ID {quiz_id} не найден или принадлежит другому пользователю.'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error_at_quiz_fetch': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            timestamp_part = str(int(time.time() * 1000))[-3:]
            random_part = ''.join(random.choices(string.digits, k=3))
            code = timestamp_part + random_part
            if not QuizSession.objects.filter(code=code, status='waiting').exists():
                break

        try:
            session = QuizSession.objects.create(
                quiz=quiz,
                code=code,
                status='waiting'
            )
            return Response({
                'id': session.id,
                'code': code,
                'quiz': quiz.id,
                'status': session.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error_at_session_create': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'error': 'Сессия с таким кодом не найдена'}, status=status.HTTP_404_NOT_FOUND)

            player_session = QuizSession.objects.create(
                quiz=master_session.quiz,
                code=master_session.code,
                participant_name=nickname,
                status='active',
                started_at=timezone.now()
            )

            return Response({
                'session_id': player_session.id,
                'code': player_session.code,
                'quiz_title': player_session.quiz.title
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error_during_join': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

            ParticipantAnswer.objects.create(
                session=session,
                question=question,
                answer=answer,
                is_correct=is_correct
            )
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
            total_questions = session.quiz.questions.count()
            correct_answers = answers.filter(is_correct=True).count()

            all_sessions = QuizSession.objects.filter(code=session.code).exclude(participant_name__isnull=True)
            leaderboard_data = []
            for s in all_sessions:
                score = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
                leaderboard_data.append({'session_id': s.id, 'score': score})

            leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
            rank = 1
            for index, item in enumerate(leaderboard_data):
                if item['session_id'] == session.id:
                    rank = index + 1
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
            return Response({'id': int(pk) if pk.isdigit() else 0, 'leaderboard': [], 'error': 'Session not found'}, status=status.HTTP_200_OK)

        try:
            is_owner = False
            if request.user.is_authenticated and session.quiz.created_by == request.user:
                is_owner = True

            all_sessions = QuizSession.objects.filter(code=session.code).exclude(participant_name__isnull=True)

            leaderboard = []
            for s in all_sessions:
                score = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
                leaderboard.append({
                    'name': s.participant_name,
                    'score': score
                })

            leaderboard.sort(key=lambda x: x['score'], reverse=True)

            formatted_leaderboard = []
            current_player_rank = 1
            for index, item in enumerate(leaderboard):
                formatted_leaderboard.append({
                    'position': index + 1,
                    'name': item['name'],
                    'score': item['score']
                })
                if session.participant_name and session.participant_name == item['name']:
                    current_player_rank = index + 1

            current_score = ParticipantAnswer.objects.filter(session=session, is_correct=True).count()
            current_name = session.participant_name if session.participant_name else "Организатор"
            total_questions = session.quiz.questions.count()

            return Response({
                'id': session.id,
                'participant_name': current_name,
                'score': current_score,
                'total_questions': total_questions,
                'is_owner': is_owner,
                'rank': current_player_rank,
                'leaderboard': formatted_leaderboard
            })
        except Exception:
            return Response({
                'id': session.id,
                'participant_name': "Участник",
                'score': 0,
                'total_questions': 0,
                'is_owner': False,
                'rank': 1,
                'leaderboard': []
            })

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
            return Response({
                'id': session.id,
                'code': session.code,
                'status': session.status,
                'quiz_title': session.quiz.title
            })

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
                'answers': [
                    {'id': ans.id, 'text': ans.text}
                    for ans in current_question.answer_options.all()
                ]
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)