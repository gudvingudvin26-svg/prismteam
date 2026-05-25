import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "app_modules_quiz_sessions_quizsession" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "code" varchar(6) NOT NULL UNIQUE,
            "participant_name" varchar(100) NULL,
            "status" varchar(10) NOT NULL,
            "created_at" datetime NOT NULL,
            "started_at" datetime NULL,
            "ended_at" datetime NULL,
            "quiz_id" bigint NOT NULL
        )
    """)
    print("Table QuizSession created")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "app_modules_quiz_sessions_participantanswer" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "is_correct" bool NOT NULL,
            "answered_at" datetime NOT NULL,
            "answer_id" bigint NULL,
            "question_id" bigint NOT NULL,
            "session_id" bigint NOT NULL
        )
    """)
    print("Table ParticipantAnswer created")

print("Done!")