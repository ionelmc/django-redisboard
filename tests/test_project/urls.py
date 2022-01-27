try:
    from django.urls import url
except ImportError:
    from django.urls import re_path as url
from django.contrib import admin

urlpatterns = [
    url(r"^", admin.site.urls),
]
