from django.conf.urls import include, url

urlpatterns = [
    url(r"^test_app/$", include("tests.test_app.urls")),
]
