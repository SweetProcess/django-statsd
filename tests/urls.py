from django.urls import include, path

urlpatterns = [
    path(r"test_app/", include("tests.test_app.urls")),
]
