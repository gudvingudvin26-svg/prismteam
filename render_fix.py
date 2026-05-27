import os
import sys
import django


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    print("=== RUNNING FIX MIGRATIONS SCRIPT ===")

    import django
    django.setup()

    from django.db import connection
    from django.core.management import call_command

    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM django_migrations WHERE app='quiz_sessions'")
            print("Deleted quiz_sessions migrations from history")
        except Exception as e:
            print(f"Error deleting: {e}")

    call_command('migrate', verbosity=3)

    print("=== MIGRATIONS FIX COMPLETED ===")


if __name__ == '__main__':
    main()