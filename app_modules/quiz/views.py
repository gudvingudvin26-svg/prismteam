import logging
from datetime import datetime, timedelta

import jwt
from django.contrib.auth import logout, login
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from .models import User, Quiz, Question, AnswerOption
from .serializers import UserSerializer, QuizSerializer, QuestionSerializer, AnswerOptionSerializer
from .validators import validate_quiz_integrity

logger = logging.getLogger('reg-log_logger')


# === Auth-модуль ===
class UserRegistration(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if request.data['password'] != '':
                if request.data['phone'].isdigit():
                    if request.data['password'] == request.POST['again_password']:
                        if len(request.data['phone']) >= 10:
                            if not request.data['username'].isdigit():
                                if request.data['username'].count('@') == 0:
                                    user = serializer.save()
                                    user.jwt_token = jwt.encode(
                                        {'sub': user.id, 'exp': datetime.now() + timedelta(hours=1),
                                         'name': user.username, 'email': user.email},
                                        key=settings.SECRET_KEY
                                    )
                                    user.save()
                                    login(request, user)
                                    logger.info(f'User registered with username {user.username} successfully')
                                    return render(request, 'main.html')
                                else:
                                    return Response('Username cannot include "@" to avoid errors', status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response('Username cannot include only numbers to avoid errors', status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response('Phone number is too short', status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response('Fields "Password" and "Repeat password" are not matching', status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response('Phone number can contain only a numbers', status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response('You forgot to create a password', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main.html')
        return render(request, 'registration.html')


class UserLogin(APIView):
    def post(self, request):
        if request.data['identification_parameter'].isdigit():
            user = User.objects.filter(phone=request.data['identification_parameter']).first()
        elif request.data['identification_parameter'].count('@') > 0:
            user = User.objects.filter(email=request.data['identification_parameter']).first()
        else:
            user = User.objects.filter(username=request.data['identification_parameter']).first()

        if not user:
            return Response('User with this username/email/phone does not exist', status=status.HTTP_400_BAD_REQUEST)
        else:
            if user.password == request.data['password']:
                user.jwt_token = jwt.encode(
                    {'sub': user.id, 'exp': datetime.now() + timedelta(hours=1),
                     'name': user.username, 'email': user.email},
                    key=settings.SECRET_KEY
                )
                user.save()
                login(request, user)
                logging.info(f'User logged in with username {user.username} successfully')
                return render(request, 'main.html')
            else:
                return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main.html')
        else:
            return render(request, 'login.html')


class Main(APIView):
    def get(self, request):
        return render(request, 'main.html')


class UserLogout(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.jwt_token = ''
            request.user.save()
        else:
            return redirect('http://127.0.0.1:8000/main/')
        if request.user.jwt_token == '':
            name = request.user.username
            logout(request)
            if request.user.is_authenticated:
                logger.info(f'User can not log out with username {name} successfully')
                return redirect('http://127.0.0.1:8000/main/')
            else:
                logger.info(f'User logged out with username {name} successfully')
        return redirect('http://127.0.0.1:8000/login/')

    def get(self, request):
        return redirect('http://127.0.0.1:8000/main/')


# === Quiz-constructor ViewSets ===
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Quiz.objects.filter(
            created_by=user
        ).prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.select_related('quiz').prefetch_related('answer_options')
            )
        ).select_related('created_by').order_by('-id')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        quiz = self.get_object()
        try:
            validate_quiz_integrity(quiz, use_drf_exception=True)
            return Response({"status": "Квиз успешно прошел валидацию и готов к публикации."},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Question.objects.filter(
            quiz__created_by=user
        ).select_related('quiz').prefetch_related('answer_options')


class AnswerOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return AnswerOption.objects.filter(
            question__quiz__created_by=user
        ).select_related('question__quiz')
