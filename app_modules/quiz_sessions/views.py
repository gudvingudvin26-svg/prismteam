import random
import string
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import QuizSession, ParticipantAnswer
from .serializers import QuizSessionSerializer
from app_modules.quiz.models import Question, AnswerOption


class QuizSessionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizSession.objects.filter(quiz__created_by=self.request.user)

    def perform_create(self, serializer):
        code = ''.join(random.choices(string.digits, k=6))
        serializer.save(code=code)

    @action(detail=False, methods=['post'])
    def join(self, request):
        code = request.data.get('code')
        nickname = request.data.get('nickname')

        print(f"=== JOIN SESSION ===")
        print(f"Code: {code}")
        print(f"Nickname: {nickname}")

        try:
            session = QuizSession.objects.get(code=code)
            session.participant_name = nickname
            session.save()
            print(f"Session {session.id} updated with name: {nickname}")
            return Response({'session_id': session.id, 'code': session.code})
        except QuizSession.DoesNotExist:
            print(f"Session with code {code} not found")
            return Response({'error': 'Session not found'}, status=404)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        session = self.get_object()
        session.status = 'active'
        session.started_at = timezone.now()
        session.save()
        return Response({'status': 'started'})

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        session = self.get_object()
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()
        return Response({'status': 'completed'})

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        session = self.get_object()
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

    @action(detail=True, methods=['get'])
    def my_result(self, request, pk=None):
        session = self.get_object()
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

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        session = self.get_object()
        all_sessions = QuizSession.objects.filter(quiz=session.quiz)

        print("=== RESULTS DEBUG ===")
        for s in all_sessions:
            print(f"Session {s.id}: name='{s.participant_name}', code='{s.code}'")

        from collections import defaultdict
        scores = defaultdict(int)
        for s in all_sessions:
            correct = ParticipantAnswer.objects.filter(session=s, is_correct=True).count()
            scores[s.id] = correct
            print(f"Session {s.id}: score={correct}")

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

        print(f"Results data: {results}")
        return Response(results)

    @action(detail=True, methods=['get'])
    def questions_stats(self, request, pk=None):
        session = self.get_object()
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
        session = self.get_object()
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