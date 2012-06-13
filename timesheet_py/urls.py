
from django.conf.urls.defaults import patterns, include, url
from timesheet.views import *
from timesheet.forms import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'timesheet.views.home', name='home'),
    url(r'^projects/(?P<project_id>\d+)/start$', 'timesheet.views.projects_start', name='projects_start'),
    url(r'^projects/(?P<project_id>\d+)/stop$', 'timesheet.views.projects_stop', name='projects_stop'),
    url(r'^projects/(?P<project_id>\d+)/delete$', 'timesheet.views.projects_delete', name='projects_delete'),
    url(r'^projects/(?P<project_id>\d+)/history$', 'timesheet.views.projects_history', name='projects_history'),

    url(r'^projectwizard/$', ProjectWizard.as_view([ProjectNameForm, ProjectPriceForm]), name='project_wizard'),
    # Examples:
    # url(r'^$', 'timesheet_py.views.home', name='home'),
    # url(r'^timesheet_py/', include('timesheet_py.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
