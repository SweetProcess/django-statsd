from django.urls import re_path

from .views import index

app_name = "tests.test_app.views"
urlpatterns = [re_path("", index, name="index")]
