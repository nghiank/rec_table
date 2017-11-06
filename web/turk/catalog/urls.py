from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^verify/(?P<id>[0-9a-f-.]+)$', views.verify, name='verify'),
    url(r'^save_expected', views.save_expected_result, name='save_expected'),
]

