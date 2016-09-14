from __future__ import absolute_import
from django_statsd import middleware, utils
from django.core.cache import cache

try:
    from celery import signals
    from celery.utils import dispatch

    counter = utils.get_counter('celery.status')

    def increment(signal):
        counter.increment(signal)

        def _increment(**kwargs):
            pass
        return _increment

    for signal in dir(signals):
        instance = getattr(signals, signal)
        if isinstance(instance, dispatch.Signal):
            instance.connect(increment(signal))

    def start(**kwargs):
        timer = cache.get(kwargs.get('task_id'))
        if timer is None:
            middleware.StatsdMiddleware \
                .custom_event_counter('celery', 'queue_timeout',
                                      kwargs.get('task').name)
        else:
            timer.stop('queue_time')
            timer.submit(kwargs.get('task').name)
            cache.delete(kwargs.get('task_id'))
        middleware.StatsdMiddleware.start('celery', kwargs.get('task').name)

    def stop(**kwargs):
        middleware.StatsdMiddleware.stop(kwargs.get('task').name)
        middleware.StatsdMiddleware.scope.timings = None

    def clear(**kwargs):
        middleware.StatsdMiddleware.fail(kwargs.get('task').name)
        middleware.StatsdMiddleware.scope.timings = None

    def sent(**kwargs):
        body = kwargs.get('body')
        middleware.StatsdMiddleware\
            .custom_event_counter('celery', 'sent', body.get('task'))
        cache.set(body.get('id'), middleware.
                  StatsdMiddleware.custom_event_timer('celery',
                                                      'queue_time',
                                                      body.get('task')))

    signals.after_task_publish.connect(sent)
    signals.task_prerun.connect(start)
    signals.task_postrun.connect(stop)
    signals.task_failure.connect(clear)

except ImportError:
    pass
