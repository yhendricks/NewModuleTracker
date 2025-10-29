from django.apps import AppConfig


class ModuletrackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moduletrack'
    
    def ready(self):
        import moduletrack.signals  # Import the signals module to connect the signal