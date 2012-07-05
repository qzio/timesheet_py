# -*- coding: utf-8 -*-
"""
some basic helpers
for urls
"""

from django.http import *

# need to import all the public view methods here.
from timesheet.views import *

def method_splitter(request, *args, **kwargs):
    get_view   = kwargs.pop('GET', None)
    post_view  = kwargs.pop('POST', None)
    patch_view = kwargs.pop('PATCH', None)
    put_view   = kwargs.pop('PUT', None)
    delete_view = kwargs.pop('DELETE', None)
    options_view = kwargs.pop('OPTIONS', None)

    request_method = request.method

    if (request.method == 'POST' and request.POST.has_key('_method')):
        request_method = request.POST['_method'].upper()
    print "request_method: %s" % request_method

    if (request_method == 'GET' and get_view is not None):
        return get_view(request, *args, **kwargs) 
    elif (request_method == 'POST' and post_view is not None):
        return post_view(request, *args, **kwargs) 
    elif (request_method == 'PATCH' and patch_view is not None):
        return patch_view(request, *args, **kwargs) 
    elif (request_method == 'PUT' and put_view is not None):
        return put_view(request, *args, **kwargs) 
    elif (request_method == 'DELETE' and delete_view is not None):
        print "try to do %s" % delete_view
        return delete_view(request, *args, **kwargs) 
    else:
        return HttpResponse("method not allowed", status=405)

