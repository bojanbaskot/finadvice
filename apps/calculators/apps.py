from django.apps import AppConfig


class CalculatorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.calculators'

    def ready(self):
        import os
        # Only start scheduler in the main process (not in migrations, tests, or reloader child)
        if os.environ.get('RUN_MAIN') != 'true' and os.environ.get('DJANGO_SETTINGS_MODULE'):
            try:
                from apps.calculators.scheduler import start
                start()
            except Exception:
                pass
