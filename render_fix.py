import os
import sys
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    print("=== RUNNING FIX MIGRATIONS SCRIPT ===")

    django.setup()

    from django.db import connection
    from django.core.management import call_command
    from django.db.utils import ProgrammingError

    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM django_migrations WHERE app='quiz_sessions'")
            print(">>> Deleted quiz_sessions migrations from history.")
        except Exception as e:
            print(f">>> Could not delete from django_migrations: {e}")

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'quiz_session')")
            table_exists = cursor.fetchone()[0]
            if table_exists:
                print(">>> Table 'quiz_session' already exists.")
                call_command('migrate', 'quiz_sessions', '0001_initial', fake=True)
                print(">>> Marked quiz_sessions.0001_initial as faked.")
            else:
                print(">>> Table 'quiz_session' does not exist. Will run migrations normally.")
        except Exception as e:
            print(f">>> Could not check table existence: {e}. Attempting fake migrate anyway.")
            try:
                call_command('migrate', 'quiz_sessions', '0001_initial', fake=True)
                print(">>> Forced fake migration of quiz_sessions.0001_initial.")
            except Exception as fake_error:
                print(f">>> Could not fake migrate: {fake_error}")

    print(">>> Running remaining migrations...")
    call_command('migrate', verbosity=3)

    print("=== MIGRATIONS FIX COMPLETED ===")


if __name__ == '__main__':
    main()