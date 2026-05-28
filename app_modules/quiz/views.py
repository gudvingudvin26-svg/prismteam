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
from .authentication import CookieJWTAuthentication

login_log = logging.getLogger('login_log')
quiz_log = logging.getLogger('quiz_log')


class UserRegistration(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            login_log.error(f"Ошибка регистрации: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        password = request.data.get('password')
        again_password = request.data.get('again_password')
        username = request.data.get('username')
        email = request.data.get('email')

        if not password:
            return Response(
                {'error': 'Требуется пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != again_password:
            return Response(
                {'error': 'Пароли не совпадают'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not username:
            return Response(
                {'error': 'Требуется имя пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            return Response(
                {'error': 'Требуется email'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if username.isdigit():
            return Response(
                {'error': 'Имя пользователя не может состоять только из цифр'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if '@' in username:
            return Response(
                {'error': 'Имя пользователя не может содержать символ @'},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_user = serializer.save()
        current_user.set_password(password)
        current_user.save()

        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)

        login_log.info(
            f"Пользователь успешно зарегистрирован: {current_user.username}",
            extra={'user_id': current_user.id}
        )

        response = redirect('/dashboard')
        response.set_cookie(
            'access_token',
            str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600 * 24,
            path='/'
        )
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600 * 24 * 7,
            path='/'
        )
        return response

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard')
        return render(request, 'registration.html')


class UserLogin(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        identification_parameter = request.data.get('identification_parameter')
        password = request.data.get('password')

        if not identification_parameter or not password:
            return Response(
                {'error': 'Требуется идентификатор и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if '@' in identification_parameter:
            current_user = User.objects.filter(email=identification_parameter).first()
        else:
            current_user = User.objects.filter(username=identification_parameter).first()

        if not current_user:
            login_log.error(f'Ошибка входа: Пользователь {identification_parameter} не найден')
            return Response(
                {'error': 'Пользователь с таким именем или email не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

        if current_user.check_password(password):
            refresh = RefreshToken.for_user(current_user)
            login(request, current_user)

            login_log.info(
                f"Пользователь вошел: {current_user.username}",
                extra={'user_id': current_user.id}
            )

            response = redirect('/dashboard')
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600 * 24,
                path='/'
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600 * 24 * 7,
                path='/'
            )
            return response
        else:
            login_log.error(f'Ошибка входа: Неверный пароль для {identification_parameter}')
            return Response(
                {'error': 'Неверный пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard')
        return render(request, 'login.html')


class Main(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'main.html')
        return redirect('/')


class UserLogout(APIView):
    def post(self, request):
        username = request.user.username if request.user.is_authenticated else 'Аноним'
        user_id = request.user.id if request.user.is_authenticated else None

        logout(request)

        login_log.info(
            f"Пользователь вышел: {username}",
            extra={'user_id': user_id}
        )

        response = redirect('/')
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        response = redirect('/')
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class UserRegistrationAPI(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
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
            return Response({'username': 'Пользователь с таким именем уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)

        current_user = serializer.save()
        current_user.first_name = first_name
        current_user.set_password(password)
        current_user.save()

        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)

        login_log.info(
            f"API регистрация успешна: {username}",
            extra={'user_id': current_user.id}
        )

        response = Response({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            }
        }, status=status.HTTP_201_CREATED)

        response.set_cookie(
            'access_token',
            str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite='None',
            max_age=3600 * 24,
            path='/'
        )
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=True,
            samesite='None',
            max_age=3600 * 24 * 7,
            path='/'
        )

        return response


class UserLoginAPI(APIView):
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(
                {'error': 'Требуется email и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            current_user = User.objects.get(email=email)
        except User.DoesNotExist:
            login_log.error(f"Ошибка API входа: Пользователь {email} не найден")
            return Response(
                {'detail': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not current_user.check_password(password):
            login_log.error(f"Ошибка API входа: Неверный пароль для {email}")
            return Response(
                {'detail': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(current_user)
        login(request, current_user)
        login_log.info(
            f"API вход успешен: {current_user.username}",
            extra={'user_id': current_user.id}
        )
        response = Response({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'first_name': current_user.first_name,
                'last_name': current_user.last_name
            }
        }, status=status.HTTP_200_OK)
        response.set_cookie(
            'access_token',
            str(refresh.access_token),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600 * 24,
            path='/'
        )
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600 * 24 * 7,
            path='/'
        )
        return response
class TokenRefreshAPI(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {'error': 'Требуется refresh токен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = Response({
                'access': access_token
            }, status=status.HTTP_200_OK)
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600 * 24,
                path='/'
            )
            return response
        except Exception as e:
            login_log.error(f"Ошибка обновления токена: {e}")
            return Response(
                {'error': 'Недействительный refresh токен'},
                status=status.HTTP_401_UNAUTHORIZED
            )
class GetCurrentUserAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_200_OK)
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
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
    def retrieve(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()
            if quiz.created_by != request.user:
                quiz_log.warning(
                    f"Отказано в доступе к квизу {kwargs.get('pk')} для пользователя {request.user.id}",
                    extra={'quiz_id': kwargs.get('pk'), 'user_id': request.user.id}
                )
                return Response(
                    {"detail": "У вас нет доступа к этому квизу"},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Квиз не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
    def create(self, request, *args, **kwargs):
        try:
            quiz_log.info(
                f"Создание квиза пользователем {request.user.id}",
                extra={'user_id': request.user.id}
            )
            return super().create(request, *args, **kwargs)
        except Exception as e:
            quiz_log.error(
                f"Не удалось создать квиз: {str(e)}",
                extra={'user_id': request.user.id}
            )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    def update(self, request, *args, **kwargs):
        quiz_log.info(
            f"Обновление квиза {kwargs.get('pk')}",
            extra={'quiz_id': kwargs.get('pk'), 'user_id': request.user.id}
        )
        return super().update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        quiz_log.info(
            f"Удаление квиза {kwargs.get('pk')}",
            extra={'quiz_id': kwargs.get('pk'), 'user_id': request.user.id}
        )
        return super().destroy(request, *args, **kwargs)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        quiz = self.get_object()
        try:
            validate_quiz_integrity(quiz, use_drf_exception=True)
            quiz_log.info(
                f"Квиз {pk} опубликован",
                extra={'quiz_id': pk, 'user_id': request.user.id}
            )
            return Response(
                {"status": "Квиз успешно прошел валидацию и готов к публикации."},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def perform_create(self, serializer):
        quiz = QuizFactory.create_quiz(serializer.validated_data, self.request.user)
        serializer.instance = quiz
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get_queryset(self):
        user = self.request.user
        return Question.objects.filter(
            quiz__created_by=user
        ).select_related('quiz').prefetch_related('answer_options')
class AnswerOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def get_queryset(self):
        user = self.request.user
        return AnswerOption.objects.filter(
            question__quiz__created_by=user
        ).select_related('question__quiz')