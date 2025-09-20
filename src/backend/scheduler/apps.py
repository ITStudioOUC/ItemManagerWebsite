from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    def ready(self):
        # 只有在runserver命令时才启动调度器，避免在migrate等命令时启动 :(
        import sys
        if 'runserver' in sys.argv:
            from . import jobs
            jobs.start_scheduler()
