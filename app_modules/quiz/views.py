import logging
from .repositories import QuizRepository, QuestionRepository
from .factories import QuizFactory
from django.contrib.auth import logout, login
from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Quiz, AnswerOption
from .serializers import UserSerializer, QuizSerializer, QuestionSerializer, AnswerOptionSerializer
from .validators import validate_quiz_integrity

login_log = logging.getLogger('login_log')
user = None


class UserRegistration(APIView):
    def post(self, request):
        global user
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
        global user
        identification_parameter = request.data.get('identification_parameter')
        password = request.data.get('password')

        if not identification_parameter or not password:
            return Response({'error': 'Identification parameter and password required'},
                            status=status.HTTP_400_BAD_REQUEST)

        if identification_parameter.isdigit():
            user = User.objects.filter(phone=identification_parameter).first()
        elif '@' in identification_parameter:
            user = User.objects.filter(email=identification_parameter).first()
        else:
            user = User.objects.filter(username=identification_parameter).first()

        if not user:
            login_log.error(f'Login failed: User with {identification_parameter} does not exist')
            return Response({'error': 'User with this username/email/phone does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                login(request, user)
                if request.user.is_authenticated:
                    login_log.info(f'User logged in with username {user.username} successfully')
                    return render(request, 'main.html')
                else:
                    login_log.error(f'User can not log in for some reason')
                    return Response('User can not log in for some reason', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                login_log.error(f'Login failed: Wrong password for {identification_parameter}')
                return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)

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
        global user
        username = user.username
        logout(request)
        if not request.user.is_authenticated:
            login_log.info(f'User with username {username} logged out successfully')
            return redirect('http://127.0.0.1:8000/login/')
        else:
            login_log.error(f'User with username {username} can not log out for some reason')
            return redirect('http://127.0.0.1:8000/main/')

    def get(self, request):
        return redirect('http://127.0.0.1:8000/main/')


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

        if User.objects.filter(email=email).exists():
            return Response({'email': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'username': 'User with this username already exists'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

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


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizRepository.get_user_quizzes(
            self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()
            if quiz.created_by != request.user:
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

    def destroy(self, request, *args, **kwargs):
        try:
            quiz = self.get_object()
            if quiz.created_by != request.user:
                return Response(
                    {"detail": "У вас нет прав на удаление этого квиза"},
                    status=status.HTTP_403_FORBIDDEN
                )
            quiz.delete()
            return Response(
                {"detail": "Квиз успешно удален"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Квиз не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

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
        quiz = QuizFactory.create_quiz(
            serializer.validated_data,
            self.request.user
        )
        serializer.instance = quiz


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuestionRepository.get_queryset().filter(
            quiz__created_by=self.request.user
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = {
            'text': request.data.get('text', instance.text),
            'order': request.data.get('order', instance.order),
            'timer': request.data.get('timer', instance.timer),
            'points': request.data.get('points', instance.points),
            'question_type': request.data.get('question_type', instance.question_type),
            'quiz': instance.quiz.id,
            'answer_options': []
        }

        for answer in instance.answer_options.all():
            data['answer_options'].append({
                'id': answer.id,
                'text': answer.text,
                'is_correct': answer.is_correct
            })

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class AnswerOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return AnswerOption.objects.filter(
            question__quiz__created_by=user
        ).select_related('question__quiz')


class GetCurrentUserAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_200_OK)