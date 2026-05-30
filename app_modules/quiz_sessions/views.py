import random
import string
import logging
import time
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
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

        print(f"=== JOIN SESSION ===")
        print(f"Code: {code}")
        print(f"Nickname: {nickname}")

        if not code or not nickname:
            return Response({'error': 'Code and nickname are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            master_session = QuizSession.objects.filter(
                code=code,
                participant_name__isnull=True
            ).first()
            if not master_session:
                return Response({'error': 'Сессия не найдена'}, status=status.HTTP_404_NOT_FOUND)

            existing_player = QuizSession.objects.filter(code=code, participant_name=nickname).first()
            if existing_player:
                return Response(
                    {'session_id': existing_player.id, 'code': existing_player.code,
                     'quiz_title': existing_player.quiz.title},
                    status=status.HTTP_200_OK)

            player_session = QuizSession.objects.create(
                quiz=master_session.quiz,
                code=master_session.code,
                participant_name=nickname,
                status='waiting',
                started_at=timezone.now()
            )

            print(f"Player session created: id={player_session.id}, name={player_session.participant_name}")

            return Response(
                {'session_id': player_session.id, 'code': player_session.code, 'quiz_title': player_session.quiz.title},
                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error in join: {e}")
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
            print(f"Session {pk} completed successfully")
            game_observer.notify('game_finished', session_id=session.id, code=session.code)
            return Response({'status': 'completed'})
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error ending session: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny()])
    def answer(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        question_id = request.data.get('question_id')
        answer_ids = request.data.get('answer_ids', [])

        if not answer_ids:
            answer_ids = [request.data.get('answer_id')] if request.data.get('answer_id') else []

        try:
            from app_modules.quiz.models import Question, AnswerOption
            question = Question.objects.get(id=question_id)
            points_per_question = question.points if question.points else 100
            existing_answer = ParticipantAnswer.objects.filter(
                session=session,
                question=question
            ).exists()

            if existing_answer:
                return Response({
                    'error': 'Ответ уже отправлен'
                }, status=status.HTTP_400_BAD_REQUEST)
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
                    ParticipantAnswer.objects.create(
                        session=session,
                        question=question,
                        answer=answer,
                        is_correct=answer.is_correct
                    )

                return Response({
                    'status': 'answer received',
                    'is_correct': is_fully_correct,
                    'points_earned': earned_points,
                    'user_correct_count': user_correct_count,
                    'total_correct_count': total_correct_count
                })
            else:
                answer = AnswerOption.objects.get(id=answer_ids[0]) if answer_ids else None
                is_correct = answer.is_correct if answer else False
                earned_points = points_per_question if is_correct else 0

                ParticipantAnswer.objects.create(
                    session=session,
                    question=question,
                    answer=answer,
                    is_correct=is_correct
                )

                return Response({
                    'status': 'answer received',
                    'is_correct': is_correct,
                    'points_earned': earned_points
                })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def my_result(self, request, pk=None):

        try:
            session = QuizSession.objects.get(id=pk)

        except QuizSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            total_points = 0

            correct_questions = 0

            questions = session.quiz.questions.prefetch_related(
                'answer_options'
            ).all()

            detailed_stats = []

            for question in questions:

                correct_option_ids = set(
                    question.answer_options.filter(
                        is_correct=True
                    ).values_list('id', flat=True)
                )

                selected_option_ids = set(
                    ParticipantAnswer.objects.filter(
                        session=session,
                        question=question
                    ).values_list('answer_id', flat=True)
                )

                is_correct = (
                        selected_option_ids == correct_option_ids
                )

                question_points = (
                    question.points
                    if question.points
                    else 100
                )

                earned_points = (
                    question_points
                    if is_correct
                    else 0
                )

                if is_correct:
                    correct_questions += 1
                    total_points += earned_points

                detailed_stats.append({
                    'question_id': question.id,
                    'question_text': question.text,
                    'is_correct': is_correct,
                    'selected_answers': list(selected_option_ids),
                    'correct_answers': list(correct_option_ids),
                    'points': earned_points
                })

            total_questions = questions.count()

            return Response({
                'score': total_points,
                'total_questions': total_questions,
                'correct_answers': correct_questions,
                'details': detailed_stats
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny()])
    def results(self, request, pk=None):
        try:
            session = QuizSession.objects.get(id=pk)
        except QuizSession.DoesNotExist:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        try:
            all_sessions = QuizSession.objects.filter(
                code=session.code,
                participant_name__isnull=False
            )
            players_summary = {}

            for s in all_sessions:
                name = s.participant_name if s.participant_name else (
                    s.quiz.created_by.username if s.quiz.created_by else "Организатор")
                points = 0
                s_answers = ParticipantAnswer.objects.filter(session=s)

                for ans in s_answers:
                    if ans.is_correct:
                        q = ans.question
                        q_points = q.points if q.points else 100

                        if q.question_type == 'multiple':
                            correct_count = q.answer_options.filter(is_correct=True).count()
                            user_correct = ParticipantAnswer.objects.filter(session=s, question=q,
                                                                            is_correct=True).count()
                            if correct_count > 0:
                                points += int((q_points / correct_count) * user_correct)
                        else:
                            points += q_points

                if name == "Организатор" and points == 0 and all_sessions.exclude(
                        participant_name__isnull=True).exists():
                    continue

                if name not in players_summary or points > players_summary[name]:
                    players_summary[name] = points

            leaderboard = []
            for name, points in players_summary.items():
                leaderboard.append({
                    'participant_name': name,
                    'score': points,
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
            session = QuizSession.objects.select_related(
                'quiz'
            ).get(id=pk)

        except QuizSession.DoesNotExist:
            return Response([])

        questions = session.quiz.questions.prefetch_related(
            'answer_options'
        ).all()

        completed_sessions = QuizSession.objects.filter(
            code=session.code,
            status='completed'
        ).exclude(
            participant_name__isnull=True
        ).exclude(
            participant_name=''
        )

        result = []

        for question in questions:

            correct_option_ids = set(
                question.answer_options.filter(
                    is_correct=True
                ).values_list('id', flat=True)
            )

            total_answers = 0
            correct_count = 0

            for participant_session in completed_sessions:

                selected_answers = ParticipantAnswer.objects.filter(
                    session=participant_session,
                    question=question
                ).exclude(
                    answer__isnull=True
                )

                selected_option_ids = set(
                    selected_answers.values_list(
                        'answer_id',
                        flat=True
                    )
                )

                if not selected_option_ids:
                    continue

                total_answers += 1

                if selected_option_ids == correct_option_ids:
                    correct_count += 1

            correct_percent = (
                round((correct_count / total_answers) * 100)
                if total_answers > 0
                else 0
            )

            result.append({
                'question_id': question.id,
                'question_text': question.text,
                'total_answers': total_answers,
                'correct_count': correct_count,
                'correct_percent': correct_percent
            })

        return Response(result)

    def retrieve(self, request, *args, **kwargs):
        try:
            session = QuizSession.objects.get(id=kwargs.get('pk'))
            print(
                f"Retrieve session {kwargs.get('pk')}, status: {session.status}, participant: {session.participant_name}")
        except QuizSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        if session.participant_name:
            try:
                quiz = session.quiz
                question_index = int(request.GET.get('index', 0))
                questions_list = list(quiz.questions.all().order_by('order'))

                print(f"Player session: question index {question_index}, total questions: {len(questions_list)}")

                if question_index >= len(questions_list) or len(questions_list) == 0:
                    session.status = 'completed'
                    session.ended_at = timezone.now()
                    session.save()
                    print(f"Player session {session.id} completed")
                    return Response({'finished': True})

                current_question = questions_list[question_index]
                timer_value = current_question.timer if current_question.timer else (quiz.timer if quiz.timer else 30)

                return Response({
                    'id': current_question.id,
                    'text': current_question.text,
                    'question_type': current_question.question_type,
                    'timer': timer_value,
                    'index': question_index,
                    'answers': [{'id': ans.id, 'text': ans.text} for ans in current_question.answer_options.all()]
                })
            except Exception as e:
                print(f"Error in player retrieve: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or session.quiz.created_by != request.user:
            return Response({
                'id': session.id,
                'code': session.code,
                'status': session.status,
                'quiz_title': session.quiz.title,
                'participant_name': session.participant_name,
                'quiz': {
                    'id': session.quiz.id,
                    'title': session.quiz.title,
                    'created_by': {
                        'id': session.quiz.created_by.id,
                        'username': session.quiz.created_by.username
                    }
                }
            })

        try:
            quiz = session.quiz
            question_index = int(request.GET.get('index', 0))
            questions_list = list(quiz.questions.all().order_by('order'))

            print(f"Creator session: question index {question_index}, total questions: {len(questions_list)}")

            if question_index >= len(questions_list) or len(questions_list) == 0:
                session.status = 'completed'
                session.ended_at = timezone.now()
                session.save()
                print(f"Creator session {session.id} completed")
                return Response({'finished': True})

            current_question = questions_list[question_index]
            timer_value = current_question.timer if current_question.timer else (quiz.timer if quiz.timer else 30)

            return Response({
                'id': current_question.id,
                'text': current_question.text,
                'question_type': current_question.question_type,
                'timer': timer_value,
                'index': question_index,
                'answers': [{'id': ans.id, 'text': ans.text} for ans in current_question.answer_options.all()]
            })
        except Exception as e:
            print(f"Error in creator retrieve: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)