from django.apps import AppConfig


class BatchAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'batch_app'
    
    def ready(self):
        # Import the models and create the management group
        from .models import create_batch_management_group
        create_batch_management_group()