from urllib import request

from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout, login

from config import settings
from .serializers import UserSerializer
import jwt
from datetime import datetime, timedelta
import logging

from .models import User

logger = logging.getLogger('reg-log_logger')

class UserRegistration(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(): # проверка на валидность всех параметров
            if request.data['password'] != '':
                if request.data['phone'].isdigit():
                    if request.data['password'] == request.POST['again_password']:
                        if len(request.data['phone']) >= 10:
                            if not request.data['username'].isdigit():
                                if request.data['username'].count('@') == 0:
                                    user = serializer.save()
                                    user.jwt_token = jwt.encode({'sub': user.id, 'exp': datetime.now() + timedelta(hours=1), 'name': user.username, 'email': user.email}, key = settings.SECRET_KEY) #Присвоение юзеру jwt-токен
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

            if request.data['identification_parameter'].isdigit(): # Поиск юзера с заданным именем/почтой/номером телефона
                user = User.objects.filter(phone=request.data['identification_parameter']).first()
            elif request.data['identification_parameter'].count('@') >0:
                user = User.objects.filter(email=request.data['identification_parameter']).first()
            else:
                user = User.objects.filter(username=request.data['identification_parameter']).first()

            if not user: #Проверка на наличие пользователя с такими данными и выдача ему jwt-токена
                return Response('User with this username/email/phone does not exist', status=status.HTTP_400_BAD_REQUEST)
            else:
                if user.password == request.data['password']:
                    user.jwt_token = jwt.encode({'sub': user.id, 'exp': datetime.now() + timedelta(hours=1), 'name': user.username, 'email': user.email}, key = settings.SECRET_KEY)
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