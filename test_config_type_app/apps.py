from django.apps import AppConfig


class TestConfigTypeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_config_type_app'