from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^verify/(?P<id>[0-9a-f-.]+)$', views.verify, name='verify'),
    url(r'^save_expected/(?P<id>[0-9a-f-.]+)$', views.save_expected_result, name='save_expected'),
    url(r'^remove_image/(?P<id>(\/.+)+)$', views.remove_image, name='remove_image'),
    url(r'^train$', views.train, name='train'),
    url(r'^add_training_data$', views.add_training_data, name='add_training_data'),
]

