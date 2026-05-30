"""Кастомная аутентификация JWT через httpOnly cookie для DRF.

Модуль предоставляет класс CookieJWTAuthentication, расширяющий стандартный
JWTAuthentication из rest_framework_simplejwt. Вместо чтения токена из
заголовка Authorization, данный класс извлекает access_token из cookie,
что повышает безопасность (защита от XSS) и упрощает работу с фронтендом.

Особенности:
• Токен читается из httpOnly cookie 'access_token' (недоступен для JS);
• При успешной валидации возвращает кортеж (user, validated_token);
• При ошибке логирует событие и возвращает None для передачи обработки
  другим аутентификаторам в цепочке DRF;
• Совместим с настройками SIMPLE_JWT из settings.py.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
import logging

logger = logging.getLogger('login_log')


class CookieJWTAuthentication(JWTAuthentication):
    """Аутентификация через JWT-токен из httpOnly cookie.

    Наследуется от JWTAuthentication, переопределяет методы authenticate()
    и get_user() для работы с токенами, хранящимися в cookie браузера.
    Рекомендуется использовать в сочетании с настройками:
    • SIMPLE_JWT['AUTH_HEADER_TYPES'] — можно оставить пустым;
    • REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] — добавить данный класс.

    Безопасность:
    • httpOnly cookie защищают токен от кражи через XSS-атаки;
    • Для защиты от CSRF рекомендуется использовать SameSite=Lax/Strict
      и проверять Origin/Referer заголовки на уровне middleware.
    """

    def authenticate(self, request):
        """Извлечение и валидация JWT-токена из cookie запроса.

        Последовательность действий:
        1. Читает значение cookie 'access_token' из запроса.
        2. При отсутствии токена возвращает None (передача обработки дальше).
        3. Пытается валидировать токен через AccessToken().
        4. При успехе — получает пользователя через get_user() и возвращает
           кортеж (user, validated_token) для DRF.
        5. При любой ошибке — логирует событие и возвращает None.

        Args:
            request: Объект запроса DRF с атрибутом COOKIES.

        Returns:
            tuple(User, AccessToken) | None: Кортеж с пользователем и токеном
            при успехе, None при отсутствии токена или ошибке валидации.

        Side effects:
            • Запись в лог 'login_log' при успехе или ошибке аутентификации.
        """
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
        """Получение экземпляра пользователя по ID из валидированного токена.

        Извлекает user_id из payload токена, загружает пользователя из БД
        через кастомную модель User. При отсутствии user_id или ошибке
        загрузки возвращает None для безопасного отказа.

        Примечание:
        • Метод переопределён для явного указания модели User из локального
          модуля .models, что важно при использовании кастомной модели
          пользователя (AUTH_USER_MODEL).

        Args:
            validated_token (AccessToken): Валидированный объект токена.

        Returns:
            User | None: Экземпляр пользователя при успехе, None при ошибке.

        Side effects:
            • Блокирующий запрос к БД (User.objects.get) — допустимо, так как
              вызывается в синхронном контексте аутентификации DRF.
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                return None
            from .models import User
            return User.objects.get(id=user_id)
        except Exception:
            return None