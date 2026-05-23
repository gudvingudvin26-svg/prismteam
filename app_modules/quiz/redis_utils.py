import redis
import json
from typing import Optional
from django.conf import settings


class RedisTimerManager:
    _instance: Optional['RedisTimerManager'] = None
    _redis: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._redis is None:
            self._redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )

    @property
    def client(self) -> redis.Redis:
        return self._redis

    def start_question_timer(self, quiz_id: str, question_number: int, duration: int = 30) -> int:
        key = f"quiz:{quiz_id}:question:{question_number}:timer"
        start_time = int(self._redis.time()[0])
        end_time = start_time + duration

        pipe = self._redis.pipeline()
        pipe.set(f"{key}:start", start_time)
        pipe.set(f"{key}:end", end_time)
        pipe.set(f"{key}:duration", duration)
        pipe.expire(f"{key}:start", 3600)
        pipe.expire(f"{key}:end", 3600)
        pipe.expire(f"{key}:duration", 3600)
        pipe.execute()

        return end_time

    def get_question_timer(self, quiz_id: str, question_number: int) -> dict:
        key = f"quiz:{quiz_id}:question:{question_number}:timer"

        start_time = self._redis.get(f"{key}:start")
        end_time = self._redis.get(f"{key}:end")
        duration = self._redis.get(f"{key}:duration")

        if start_time is None or end_time is None:
            return {'active': False}

        end_time = int(end_time)
        current_time = int(self._redis.time()[0])
        remaining = max(0, end_time - current_time)

        return {
            'active': True,
            'start_time': int(start_time),
            'end_time': end_time,
            'remaining': remaining,
            'duration': int(duration) if duration else 30
        }

    def stop_question_timer(self, quiz_id: str, question_number: int) -> bool:
        key = f"quiz:{quiz_id}:question:{question_number}:timer"
        keys = [f"{key}:start", f"{key}:end", f"{key}:duration"]
        return bool(self._redis.delete(*keys))

    def is_timer_active(self, quiz_id: str, question_number: int) -> bool:
        key = f"quiz:{quiz_id}:question:{question_number}:timer"
        return self._redis.exists(f"{key}:end") == 1

    def get_time_remaining(self, quiz_id: str, question_number: int) -> int:
        timer = self.get_question_timer(quiz_id, question_number)
        return timer.get('remaining', 0) if timer.get('active') else 0


def get_timer_manager() -> RedisTimerManager:
    return RedisTimerManager()