from __future__ import absolute_import
from django_statsd.middleware import StatsdMiddleware
from django.core.cache import cache

from . import settings


def generate_task_name(original_name, routing_key):
    if routing_key.endswith(".fifo"):
        routing_key = routing_key.split(".")[0]

    return "{}.queue_{}".format(original_name, routing_key)


try:
    from celery import signals

    def start(**kwargs):
        task = kwargs.get("task")
        exec_options = task._get_exec_options()
        queue = exec_options.get("queue", None) or settings.STATSD_DEFAULT_CELERY_QUEUE

        timer = cache.get(kwargs.get("task_id"))
        if timer is None:
            StatsdMiddleware.custom_event_counter(
                "celery", "queue_timeout", generate_task_name(task.name, queue,),
            )
        else:
            timer.stop("queue_time")
            timer.submit(generate_task_name(task.name, queue,))
            cache.delete(kwargs.get("task_id"))
        StatsdMiddleware.start(
            "celery", generate_task_name(task.name, queue,),
        )

    def stop(**kwargs):
        task = kwargs.get("task")
        exec_options = task._get_exec_options()
        queue = exec_options.get("queue", None) or settings.STATSD_DEFAULT_CELERY_QUEUE

        StatsdMiddleware.stop(generate_task_name(task.name, queue,))
        StatsdMiddleware.scope.timings = None

    def clear(**kwargs):
        StatsdMiddleware.fail(kwargs.get("name"))
        StatsdMiddleware.scope.timings = None

    def sent(**kwargs):
        body = kwargs.get("headers")
        StatsdMiddleware.custom_event_counter(
            "celery",
            "sent",
            generate_task_name(
                body.get("task"),
                kwargs.get("routing_key") or settings.STATSD_DEFAULT_CELERY_QUEUE,
            ),
        )
        timer = StatsdMiddleware.custom_event_timer("celery", "queue_time")
        cache.set(body.get("id"), timer, settings.STATSD_CACHE_TIMEOUT)

    signals.before_task_publish.connect(sent)
    signals.task_prerun.connect(start)
    signals.task_postrun.connect(stop)
    signals.task_failure.connect(clear)

except ImportError:
    pass
