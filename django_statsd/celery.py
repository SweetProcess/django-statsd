from __future__ import absolute_import
from django_statsd.middleware import StatsdMiddleware
from django.core.cache import cache

from . import settings

try:
    from celery import signals

    def start(**kwargs):
        timer = cache.get(kwargs.get('task_id'))
        if timer is None:
            StatsdMiddleware \
                .custom_event_counter('celery', 'queue_timeout',
                                      kwargs.get('task').name)
        else:
            timer.stop('queue_time')
            timer.submit(kwargs.get('task').name)
            cache.delete(kwargs.get('task_id'))
        StatsdMiddleware.start('celery', kwargs.get('task').name)

    def stop(**kwargs):
        StatsdMiddleware.stop(kwargs.get('task').name)
        StatsdMiddleware.scope.timings = None

    def clear(**kwargs):
        StatsdMiddleware.fail(kwargs.get('name'))
        StatsdMiddleware.scope.timings = None

    def sent(**kwargs):
        body = kwargs.get('body')
        StatsdMiddleware.custom_event_counter(
            'celery', 'sent', body.get('task')
        )
        timer = StatsdMiddleware.custom_event_timer(
            'celery', 'queue_time')
        cache.set(
            body.get('id'),
            timer, settings.STATSD_CACHE_TIMEOUT)

    signals.before_task_publish.connect(sent)
    signals.task_prerun.connect(start)
    signals.task_postrun.connect(stop)
    signals.task_failure.connect(clear)

except ImportError:
    pass
