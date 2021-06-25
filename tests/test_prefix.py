from __future__ import with_statement
from unittest import TestCase
import mock
from django_statsd import middleware

from tests.test_app.celery import debug


class TestPrefix(TestCase):
    @mock.patch("statsd.Client")
    def test_prefix(self, mock_client):
        from django import test

        def get_keys():
            return set(
                sum(
                    [list(x[0][1].keys()) for x in mock_client._send.call_args_list], []
                )
            )

        middleware.StatsdMiddleware.start()
        middleware.StatsdMiddleware.stop()

        assert get_keys() == set(
            (
                "prefix.view.hit",
                "prefix.view.site.hit",
                "prefix.view.total",
            )
        )

        test.Client().get("/test_app/")
        assert get_keys() == set(
            [
                "prefix.view.get.tests.test_app.views.index.hit",
                "prefix.view.get.tests.test_app.views.index.process_request",
                "prefix.view.get.tests.test_app.views.index.process_response",
                "prefix.view.get.tests.test_app.views.index.process_view",
                "prefix.view.get.tests.test_app.views.index.total",
                "prefix.view.hit",
                "prefix.view.site.hit",
                "prefix.view.total",
            ]
        )


class TestCeleryTasks(TestCase):
    @mock.patch("statsd.Client")
    def test_tasks(self, mock_client):
        def get_keys():
            return set(
                sum(
                    [list(x[0][1].keys()) for x in mock_client._send.call_args_list], []
                )
            )

        debug.delay()

        middleware.StatsdMiddleware.start()
        middleware.StatsdMiddleware.stop()

        assert get_keys() == set(("prefix.debug.hit",))
