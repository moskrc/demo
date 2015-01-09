from django.conf.urls import url, patterns

urlpatterns = patterns('regions.views',
    url(r'^get_location_info/(?P<location_id>\d+)/$', 'get_location_info'),
    url(r'^set_city/(?P<city_id>\d+)/$', 'set_city', name='set_city')
)
