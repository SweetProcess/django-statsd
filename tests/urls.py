from django.conf.urls import include, re_path

urlpatterns = [
    re_path(r"^test_app/$", include("tests.test_app.urls")),
]
