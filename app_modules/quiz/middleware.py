"""CORS-middleware для обработки кросс-доменных запросов.

Настраивает заголовки Access-Control-Allow-* для безопасного взаимодействия
фронтенда и бэкенда. Поддерживает preflight-запросы (OPTIONS) и передачу
учётных данных (cookies, authorization headers) между доменами.
"""


class CORSMiddleware:
    """Middleware для настройки CORS-политики приложения.

    Добавляет необходимые заголовки к каждому ответу для разрешения
    кросс-доменных запросов с доверенного фронтенд-домена. Обрабатывает
    preflight-запросы метода OPTIONS, возвращая успешный статус без
    выполнения основной бизнес-логики.

    Атрибуты:
        get_response: Callable, следующий слой обработки запроса в стеке Django.
    """

    def __init__(self, get_response):
        """Инициализация middleware с сохранением следующего обработчика.

        Вызывается один раз при старте сервера для настройки цепочки обработки.

        Args:
            get_response: Функция/вью, которая будет обработана после данного middleware.
        """
        self.get_response = get_response

    def __call__(self, request):
        """Основной метод обработки запроса: добавление CORS-заголовков к ответу.

        Последовательность действий:
        1. Выполняет запрос через следующий слой обработки (get_response).
        2. Добавляет заголовки Access-Control-Allow-* для разрешения кросс-доменного доступа.
        3. Для preflight-запросов (OPTIONS) устанавливает статус 200 без тела ответа.
        4. Возвращает модифицированный ответ клиенту.

        Поддерживаемые методы: GET, POST, PUT, DELETE, OPTIONS.
        Разрешённые заголовки: Content-Type, Authorization, X-CSRFToken.
        Учётные данные (cookies) разрешены для передачи между доменами.

        Args:
            request: Объект запроса Django.

        Returns:
            Response: Объект ответа с добавленными CORS-заголовками.
        """
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = 'https://prismteam-frontend.onrender.com'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'

        if request.method == 'OPTIONS':
            response.status_code = 200

        return response