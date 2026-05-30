import os
import sys
import django

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    print("=== RUNNING FIX MIGRATIONS SCRIPT ===")
    django.setup()

    from django.db import connection
    from django.core.management import call_command

    with connection.cursor() as cursor:
        # 1. Удаляем старые миграции
        cursor.execute("DELETE FROM django_migrations WHERE app='quiz_sessions'")
        print(">>> Deleted quiz_sessions migrations from history.")

        try:
            cursor.execute("DELETE FROM participant_answer")
            print(">>> Deleted participant_answer data.")
            cursor.execute("DELETE FROM quiz_session")
            print(">>> Deleted quiz_session data.")
        except Exception as e:
            print(f">>> Could not delete data: {e}")

        try:
            cursor.execute("ALTER TABLE quiz_session DROP COLUMN IF EXISTS is_completed CASCADE")
            print(">>> Dropped is_completed column if existed.")
        except Exception as e:
            print(f">>> Could not drop column: {e}")

        try:
            call_command('migrate', 'quiz_sessions', '0001_initial', fake=True)
            print(">>> Marked quiz_sessions.0001_initial as faked.")
        except Exception as e:
            print(f">>> Could not fake migrate: {e}")

    print(">>> Running remaining migrations...")
    call_command('migrate', verbosity=3)
    print("=== MIGRATIONS FIX COMPLETED ===")

if __name__ == '__main__':
    main()