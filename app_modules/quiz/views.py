from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from .serializers import UserSerializer
import jwt
from datetime import datetime, timedelta

from .models import User

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        return render(request, 'registration.html')



class UserLogin(APIView):

    def post(self, request):
        # serializer = UserSerializer(data=request.data, login =True)
        # if serializer.is_valid():
        #     ghost_user = serializer.save()

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
                    return render(request, 'main.html')
                else:
                    return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        return render(request, 'login.html')