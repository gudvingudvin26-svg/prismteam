from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
import logging

logger = logging.getLogger('login_log')


class CookieJWTAuthentication(JWTAuthentication):
    """JWT аутентификация через httpOnly cookie"""

    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        try:
            validated_token = AccessToken(access_token)
            user = self.get_user(validated_token)
            logger.info(f"User {user.id} authenticated via cookie")
            return (user, validated_token)
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                return None
            from .models import User
            return User.objects.get(id=user_id)
        except Exception:
            return None