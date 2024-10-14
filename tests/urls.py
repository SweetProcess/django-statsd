from django.urls import include
from django.conf.urls import re_path

urlpatterns = [
    re_path(r"^test_app/$", include("tests.test_app.urls")),
]
