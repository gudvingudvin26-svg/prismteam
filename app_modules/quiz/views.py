"""Представления квиз-приложения: аутентификация, CRUD-операции, API-эндпоинты."""
import logging
from datetime import datetime, timedelta
from django.contrib.auth import logout, login
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import User, Quiz, Question, AnswerOption
from .serializers import UserSerializer, QuizSerializer, QuestionSerializer, AnswerOptionSerializer
from .validators import validate_quiz_integrity
from .factories import QuizFactory
from .repositories import *
from .authentication import CookieJWTAuthentication

login_log = logging.getLogger('login_log')
quiz_log = logging.getLogger('quiz_log')


class UserRegistration(APIView):
    """Регистрация пользователя через веб-форму с выдачей JWT-токенов."""
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """POST: валидация данных, создание пользователя, установка токенов в cookie, редирект."""
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            login_log.error(f"Ошибка регистрации: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get('password')
        again_password = request.data.get('again_password')
        username = request.data.get('username')
        email = request.data.get('email')
        if not password:
            return Response({'error': 'Требуется пароль'}, status=status.HTTP_400_BAD_REQUEST)
        if password != again_password:
            return Response({'error': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)
        if not username:
            return Response({'error': 'Требуется имя пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Требуется email'}, status=status.HTTP_400_BAD_REQUEST)
        if username.isdigit():
            return Response({'error': 'Имя пользователя не может состоять только из цифр'}, status=status.HTTP_400_BAD_REQUEST)
        if '@' in username:
            return Response({'error': 'Имя пользователя не может содержать символ @'}, status=status.HTTP_400_BAD_REQUEST)
        current_user = serializer.save()
        current_user.set_password(password)
        current_user.save()
        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)
        login_log.info(f"Пользователь успешно зарегистрирован: {current_user.username}", extra={'user_id': current_user.id})
        response = redirect('/dashboard')
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, secure=False, samesite='Lax', max_age=3600 * 24, path='/')
        response.set_cookie('refresh_token', str(refresh), httponly=True, secure=False, samesite='Lax', max_age=3600 * 24 * 7, path='/')
        return response

    def get(self, request):
        """GET: отображение формы регистрации или редирект для авторизованных."""
        if request.user.is_authenticated:
            return redirect('/dashboard')
        return render(request, 'registration.html')


class UserLogin(APIView):
    """Аутентификация пользователя по username/email через веб-форму."""
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """POST: проверка учётных данных, вход, установка токенов, редирект."""
        identification_parameter = request.data.get('identification_parameter')
        password = request.data.get('password')
        if not identification_parameter or not password:
            return Response({'error': 'Требуется идентификатор и пароль'}, status=status.HTTP_400_BAD_REQUEST)
        if '@' in identification_parameter:
            current_user = User.objects.filter(email=identification_parameter).first()
        else:
            current_user = User.objects.filter(username=identification_parameter).first()
        if not current_user:
            login_log.error(f'Ошибка входа: Пользователь {identification_parameter} не найден')
            return Response({'error': 'Пользователь с таким именем или email не существует'}, status=status.HTTP_404_NOT_FOUND)
        if current_user.check_password(password):
            refresh = RefreshToken.for_user(current_user)
            login(request, current_user)
            login_log.info(f"Пользователь вошел: {current_user.username}", extra={'user_id': current_user.id})
            response = redirect('/dashboard')
            response.set_cookie('access_token', str(refresh.access_token), httponly=True, secure=False, samesite='Lax', max_age=3600 * 24, path='/')
            response.set_cookie('refresh_token', str(refresh), httponly=True, secure=False, samesite='Lax', max_age=3600 * 24 * 7, path='/')
            return response
        else:
            login_log.error(f'Ошибка входа: Неверный пароль для {identification_parameter}')
            return Response({'error': 'Неверный пароль'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        """GET: отображение формы входа или редирект для авторизованных."""
        if request.user.is_authenticated:
            return redirect('/dashboard')
        return render(request, 'login.html')


class Main(APIView):
    """Главная страница: дашборд для авторизованных, редирект для остальных."""
    def get(self, request):
        """GET: возврат шаблона main.html или редирект на корень."""
        if request.user.is_authenticated:
            return render(request, 'main.html')
        return redirect('/')


class UserLogout(APIView):
    """Выход из системы: очистка сессии и JWT-токенов."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """POST: logout, удаление cookie, логирование события выхода."""
        username = request.user.username if request.user.is_authenticated else 'Аноним'
        user_id = request.user.id if request.user.is_authenticated else None
        logout(request)
        login_log.info(f"Пользователь вышел: {username}", extra={'user_id': user_id})
        response = Response({"detail": "Успешно вышли из системы"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        response.delete_cookie('csrftoken', path='/')
        response.delete_cookie('sessionid', path='/')
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    def get(self, request):
        """GET: альтернативный метод выхода с очисткой cookie."""
        if request.user.is_authenticated:
            logout(request)
        response = Response({"detail": "Успешно вышли из системы"}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        response.delete_cookie('csrftoken', path='/')
        response.delete_cookie('sessionid', path='/')
        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class UserRegistrationAPI(APIView):
    """API-регистрация: возврат JSON + токены с CORS-безопасностью."""
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """POST: расширенная валидация, создание пользователя, выдача токенов."""
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            login_log.error(f"Ошибка API регистрации: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        again_password = request.data.get('again_password')
        first_name = request.data.get('first_name', '')
        if not username:
            return Response({'error': 'Требуется имя пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Требуется email'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'error': 'Требуется пароль'}, status=status.HTTP_400_BAD_REQUEST)
        if password != again_password:
            return Response({'error': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 6:
            return Response({'error': 'Пароль должен содержать минимум 6 символов'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'email': 'Пользователь с таким email уже существует'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'username': 'Пользователь с таким именем уже существует'}, status=status.HTTP_400_BAD_REQUEST)
        current_user = serializer.save()
        current_user.first_name = first_name
        current_user.set_password(password)
        current_user.save()
        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)
        login_log.info(f"API регистрация успешна: {username}", extra={'user_id': current_user.id})
        response = Response({'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email, 'first_name': current_user.first_name, 'last_name': current_user.last_name}}, status=status.HTTP_201_CREATED)
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, secure=True, samesite='None', max_age=3600 * 24, path='/')
        response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='None', max_age=3600 * 24 * 7, path='/')
        return response


class UserLoginAPI(APIView):
    """API-аутентификация: вход по email, возврат пользователя + токены."""
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """POST: проверка email/пароля, выдача токенов при успехе."""
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Требуется email и пароль'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            current_user = User.objects.get(email=email)
        except User.DoesNotExist:
            login_log.error(f"Ошибка API входа: Пользователь {email} не найден")
            return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)
        if not current_user.check_password(password):
            login_log.error(f"Ошибка API входа: Неверный пароль для {email}")
            return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)
        login_log.info(f"API вход успешен: {current_user.username}", extra={'user_id': current_user.id})
        response = Response({'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email, 'first_name': current_user.first_name, 'last_name': current_user.last_name}}, status=status.HTTP_200_OK)
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, secure=True, samesite='None', max_age=3600 * 24, path='/')
        response.set_cookie('refresh_token', str(refresh), httponly=True, secure=True, samesite='None', max_age=3600 * 24 * 7, path='/')
        return response


class TokenRefreshAPI(APIView):
    """Обновление access-токена по refresh-токену из cookie."""
    def post(self, request):
        """POST: валидация refresh-токена, выдача нового access-токена."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Требуется refresh токен'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({'access': access_token}, status=status.HTTP_200_OK)
            response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='None', max_age=3600 * 24, path='/')
            return response
        except Exception as e:
            login_log.error(f"Ошибка обновления токена: {e}")
            return Response({'error': 'Недействительный refresh токен'}, status=status.HTTP_401_UNAUTHORIZED)


class GetCurrentUserAPI(APIView):
    """Получение данных текущего аутентифицированного пользователя."""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        """GET: возврат профиля пользователя в JSON."""
        user = request.user
        return Response({'id': user.id, 'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}, status=status.HTTP_200_OK)


class QuizViewSet(viewsets.ModelViewSet):
    """CRUD для квизов: доступ только для создателя, публикация после валидации."""
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """QuerySet квизов текущего пользователя с оптимизированными связями."""
        user = self.request.user
        return Quiz.objects.filter(created_by=user).prefetch_related(Prefetch('questions', queryset=Question.objects.select_related('quiz').prefetch_related('answer_options'))).select_related('created_by').order_by('-id')

    def retrieve(self, request, *args, **kwargs):
        """GET detail: проверка прав доступа, возврат квиза или ошибка."""
        try:
            quiz = self.get_object()
            if quiz.created_by != request.user:
                quiz_log.warning(f"Отказано в доступе к квизу {kwargs.get('pk')}", extra={'quiz_id': kwargs.get('pk'), 'user_id': request.user.id})
                return Response({"detail": "У вас нет доступа к этому квизу"}, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"detail": "Квиз не найден"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """POST create: логирование, создание квиза через базовый метод."""
        try:
            quiz_log.info(f"Создание квиза пользователем {request.user.id}", extra={'user_id': request.user.id})
            return super().create(request, *args, **kwargs)
        except Exception as e:
            quiz_log.error(f"Не удалось создать квиз: {str(e)}", extra={'user_id': request.user.id})
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH: логирование и обновление квиза."""
        quiz_log.info(f"Обновление квиза {kwargs.get('pk')}", extra={'quiz_id': kwargs.get('pk'), 'user_id': request.user.id})
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE: удаление квиза и связанных сессий с проверкой прав."""
        quiz_id = kwargs.get('pk')
        quiz_log.info(f"Удаление квиза {quiz_id} пользователем {request.user.id}")
        try:
            quiz = self.get_queryset().filter(id=quiz_id).first()
            if not quiz:
                return Response({"detail": "Квиз не найден"}, status=status.HTTP_404_NOT_FOUND)
            if quiz.created_by != request.user:
                return Response({"detail": "У вас нет прав на удаление этого квиза"}, status=status.HTTP_403_FORBIDDEN)
            try:
                from app_modules.quiz_sessions.models import QuizSession
                QuizSession.objects.filter(quiz_id=quiz_id).delete()
                quiz_log.info(f"Удалены сессии для квиза {quiz_id}")
            except Exception as e:
                quiz_log.warning(f"Ошибка при удалении сессий: {e}")
            quiz.delete()
            quiz_log.info(f"Квиз {quiz_id} успешно удален")
            return Response({"detail": "Квиз успешно удален"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            quiz_log.error(f"Ошибка удаления квиза {quiz_id}: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        """POST publish: валидация целостности квиза перед публикацией."""
        quiz = self.get_object()
        try:
            validate_quiz_integrity(quiz, use_drf_exception=True)
            quiz_log.info(f"Квиз {pk} опубликован", extra={'quiz_id': pk, 'user_id': request.user.id})
            return Response({"status": "Квиз успешно прошел валидацию и готов к публикации."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Создание квиза через QuizFactory с привязкой к пользователю."""
        quiz = QuizFactory.create_quiz(serializer.validated_data, self.request.user)
        serializer.instance = quiz


class QuestionViewSet(viewsets.ModelViewSet):
    """CRUD для вопросов: доступ по квизам текущего пользователя."""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """QuerySet вопросов с фильтрацией по создателю квиза (через репозиторий)."""
        return QuestionRepository.get_queryset().filter(quiz__created_by=self.request.user)


class AnswerOptionViewSet(viewsets.ModelViewSet):
    """CRUD для вариантов ответов: доступ по вопросам текущего пользователя."""
    serializer_class = AnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """QuerySet вариантов ответов с фильтрацией по пользователю (через репозиторий)."""
        return AnswerOptionRepository.get_user_answers(self.request.user)