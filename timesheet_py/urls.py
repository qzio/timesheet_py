
from django.conf.urls.defaults import patterns, include, url

from django.contrib.auth.views import *
from timesheet.views import *
from timesheet.forms import *

from common.url_helpers import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'timesheet.views.home', name='home'),
    url(r'^accounts/profile/$', 'timesheet.views.home'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', dict(next_page='/login')),
    url(r'^projects/(?P<project_id>\d+)/start$',   method_splitter, {'POST':  projects_start}, name='projects_start'),
    url(r'^projects/(?P<project_id>\d+)/stop$',    method_splitter, {'POST':  projects_stop}, name='projects_stop'),
    url(r'^projects/(?P<project_id>\d+)/delete$',  method_splitter, {'DELETE':projects_delete}),
    url(r'^projects/(?P<project_id>\d+)/history$', method_splitter, {'GET':   projects_history}),
    url(r'^projects/(?P<project_id>\d+)/archive$', method_splitter, {'POST':   projects_archive}),
    url(r'^projects/(?P<project_id>\d+)/archives$', method_splitter, {'GET':   projects_archive_list}),
    url(r'^projects/(?P<project_id>\d+)/edit$', method_splitter, {'GET':   project_edit, 'PATCH': project_update}),

    url(r'^projectwizard/$', ProjectWizard.as_view([ProjectNameForm, ProjectPriceForm]), name='project_wizard'),
    # Examples:
    # url(r'^$', 'timesheet_py.views.home', name='home'),
    # url(r'^timesheet_py/', include('timesheet_py.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    )
