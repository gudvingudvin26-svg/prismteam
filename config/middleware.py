"""CORS-мидлварь для настройки кросс-доменных запросов к фронтенду."""
import logging

logger = logging.getLogger('ws')


class CORSMiddleware:
    """Middleware для добавления CORS-заголовков к ответам Django.

    Разрешает кросс-доменные запросы с доверенного фронтенда,
    поддерживает preflight (OPTIONS) и передачу учётных данных.
    """

    def __init__(self, get_response):
        """Инициализация: сохранение следующего обработчика в цепочке.

        Args:
            get_response: Callable следующего слоя обработки запроса.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Обработка запроса: добавление CORS-заголовков к ответу.

        Устанавливает заголовки:
        • Access-Control-Allow-Origin — разрешённый домен фронтенда;
        • Access-Control-Allow-Credentials — разрешение на передачу cookies;
        • Access-Control-Allow-Methods — поддерживаемые HTTP-методы;
        • Access-Control-Allow-Headers — разрешённые заголовки запроса.

        Для preflight-запросов (OPTIONS) возвращает статус 200 без тела.

        Args:
            request: Объект запроса Django.

        Returns:
            Response: Ответ с добавленными CORS-заголовками.
        """
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = 'https://prismteam-frontend.onrender.com'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'

        if request.method == 'OPTIONS':
            response.status_code = 200

        return response