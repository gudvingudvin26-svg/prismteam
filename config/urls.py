from django.contrib import admin
from django.urls import path
from app_modules.quiz.views import UserRegistration, UserLogin, UserLogout, Main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('main/', Main.as_view(), name='main'),
    path('logout/', UserLogout.as_view(), name='logout'),
]
