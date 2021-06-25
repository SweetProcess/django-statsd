from django.urls import path

from .views import index

app_name = "tests.test_app.views"
urlpatterns = [path("", index, name="index")]
