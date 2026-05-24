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
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from .models import User, Quiz, Question, AnswerOption
from .serializers import UserSerializer, QuizSerializer, QuestionSerializer, AnswerOptionSerializer
from .validators import validate_quiz_integrity

login_log = logging.getLogger('login_log')

class UserRegistration(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        print("DATA:", request.data)

        if not serializer.is_valid():
            print("SERIALIZER ERRORS:", serializer.errors)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        password = request.data.get('password')
        again_password = request.data.get('again_password')
        phone = request.data.get('phone')
        username = request.data.get('username')

        if not password:
            return Response(
                {'error': 'Password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != again_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not phone or not phone.isdigit():
            return Response(
                {'error': 'Phone must contain only numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(phone) < 10:
            return Response(
                {'error': 'Phone number too short'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if username.isdigit():
            return Response(
                {'error': 'Username cannot contain only numbers'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if '@' in username:
            return Response(
                {'error': 'Username cannot contain @'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)

        login(request, user)
        login_log.info(f'User registered successfully with username {user.username}')

        return render(request, 'main.html')

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main.html')
        return render(request, 'registration.html')


class UserLogin(APIView):
    def post(self, request):
        try:
            if request.data['identification_parameter'].isdigit():
                user = User.objects.filter(phone=request.data['identification_parameter']).first()
            elif request.data['identification_parameter'].count('@') > 0:
                user = User.objects.filter(email=request.data['identification_parameter']).first()
            else:
                user = User.objects.filter(username=request.data['identification_parameter']).first()

            if not user:
                return Response('User with this username/email/phone does not exist', status=status.HTTP_400_BAD_REQUEST)
            else:
                if user.check_password(request.data.get('password')):
                    refresh = RefreshToken.for_user(user)
                    login(request, user)
                    if request.user.is_authenticated:
                        login_log.info(f'User logged in with username {user.username} successfully')
                        return render(request, 'main.html')
                    else:
                        login_log.error(f'User can not log in for some reason')
                        return Response('User can not log in for some reason', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            username = request.user.username
            logout(request)
            login_log.info(f'User {username} logged out successfully')
        return redirect('/login/')

    def get(self, request):
        return redirect('http://127.0.0.1:8000/main/')


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
            quiz_log.info(f'user with username {request.user.username} published quiz "{quiz.title}" successfully')
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


class UserRegistrationAPI(APIView):
    def post(self, request):
        print("=== REGISTRATION REQUEST ===")
        print("Request data:", request.data)

        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        again_password = request.data.get('again_password')
        first_name = request.data.get('first_name', '')

        if not username:
            return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'error': 'Password required'}, status=status.HTTP_400_BAD_REQUEST)
        if password != again_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.first_name = first_name
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_200_OK)