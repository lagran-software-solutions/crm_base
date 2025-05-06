from django.apps import AppConfig


class InserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inservice'

    def ready(self):
        import inservice.signals
