from django.conf.urls import url
from django.contrib import admin
from shoppr_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^getlist', views.get_list),
    url(r'^getmedia/(?P<username>.*)', views.get_media),
]
