from celery import Celery

app = Celery("statsd")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug(self):
    pass
