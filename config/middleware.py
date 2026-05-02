import logging
import json
import time
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.consumer import AsyncConsumer
from config.logging_config import get_logger

logger = get_logger('ws')


class WSReconnectMiddleware(BaseMiddleware):
    MAX_RECONNECTS = 3
    RECONNECT_WINDOW = 60

    async def __call__(self, scope, receive, send):
        client_ip = self._get_client_ip(scope)
        path = scope.get('path', '')
        connection_id = id(scope)

        start_time = time.time()
        reconnect_count = scope.get('reconnect_count', 0)

        logger.info(f"WS_CONNECT: id={connection_id}, ip={client_ip}, path={path}, reconnect={reconnect_count}")

        try:
            return await super().__call__(scope, receive, send)

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"WS_ERROR: id={connection_id}, ip={client_ip}, path={path}, error={e}, duration={duration:.2f}s, reconnect={reconnect_count}")
            raise

    def _get_client_ip(self, scope) -> str:
        x_forwarded_for = dict(scope.get('headers', [])).get(b'x-forwarded-for')
        if x_forwarded_for:
            return x_forwarded_for.decode().split(',')[0]

        client = scope.get('client')
        if client:
            return client[0]
        return 'unknown'


class WSLogMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'websocket':
            return await super().__call__(scope, receive, send)

        client_ip = scope.get('client', ('unknown', 0))[0]
        path = scope.get('path', '')
        connection_id = id(scope)

        logger.info(f"WS_OPEN: id={connection_id}, ip={client_ip}, path={path}")

        async def wrapped_receive():
            message = await receive()
            message_type = message.get('type', '')
            if message_type == 'websocket.disconnect':
                logger.info(f"WS_CLOSE: id={connection_id}, ip={client_ip}, path={path}")
            return message

        async def wrapped_send(message):
            message_type = message.get('type', '')
            if message_type == 'websocket.close':
                code = message.get('code', 1000)
                logger.info(f"WS_SEND_CLOSE: id={connection_id}, ip={client_ip}, code={code}")
            return await send(message)

        return await super().__call__(scope, wrapped_receive, wrapped_send)


async def ws_error_handler(scope, receive, send, exception):
    logger.error(f"WS_UNHANDLED_ERROR: path={scope.get('path')}, error={exception}")
    await send({
        'type': 'websocket.close',
        'code': 1011
    })