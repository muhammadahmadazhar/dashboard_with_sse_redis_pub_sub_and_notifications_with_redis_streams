from django.apps import AppConfig


class NotifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notify'

    def ready(self):
        # import signals so Django registers them
        import notify.signals
