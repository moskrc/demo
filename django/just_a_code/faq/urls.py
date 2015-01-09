from django.conf.urls import *


urlpatterns = patterns('faq.views',
                       url(r'^$', 'index', name='faq_index'),
                       url(r'^(?P<chapter_slug>[-\w]+)/$', 'index', name='faq_index'),

)
