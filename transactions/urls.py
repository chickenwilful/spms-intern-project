from django.conf.urls import patterns, url
from transactions import views


urlpatterns = patterns(
    '',
    url(r'^$', views.transaction_list, name='list'),
    url(r'^map/$', views.get_google_map_coordinates, name='map'),
    url(r'^coordinate/$', views.update_coordinate, name='coordinate'),
)