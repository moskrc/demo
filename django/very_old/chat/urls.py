from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("chat.views",
    url("^dashboard/$", "dashboard", name="dashboard"),
    url("^dashboard/tasks/(?P<task_id>\d+)/$", "dashboard_task", name="dashboard_task"),
    url('^dashboard/tasks/(?P<task_id>\d+)/ajax/$', 'update_task_status', name='dashboard_updater'),
)
