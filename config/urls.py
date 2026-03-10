from django.contrib import admin
from django.urls import path
from app_modules.quiz.views import UserRegistration, UserLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
]
