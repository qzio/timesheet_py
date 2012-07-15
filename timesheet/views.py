# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.formtools.wizard.views import SessionWizardView
from django.views.decorators import *

from project import Project

def home(request):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    projects = p.project_list()
    started_projects = p.started()
    ctx = RequestContext(request, {
        "projects":projects,
        "project_started":started_projects})
    return render_to_response('home.html', ctx)

def projects_start(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    msg = "failed to start project"
    if (p.start_tracking(int(project_id))):
        msg = "successfully started tracking project"
    return redirect("/?msg=%s" % (msg,))


def projects_stop(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    msg = "Failed to stop tracking time"
    if (p.stop_tracking(int(project_id))):
        msg = "successfully stopped tracking time"
    return redirect("/?msg=%s" % msg)

def projects_history(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    (project, total_diff, history) = p.tracked_times(int(project_id))
    if project is not None:
        ctx = RequestContext(request, {
                             "project" : project,
                             "history" : history,
                             "total_diff":total_diff
                             })
        return render_to_response('history.html', ctx)
    return project_not_found(project_id)


def projects_delete(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    msg = "failed to delete"
    if p.delete(int(project_id)):
        msg ="success deleting project"

    return redirect("/?flash=%s" % msg)

def projects_archive(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    p.archive_tracked_times(int(project_id), request.POST["period"])
    msg = "Archived tracked time for project %s" % project_id
    return redirect("/?flash=%s" % msg)

def projects_archive_list(request, project_id):
    if (not request.user.is_authenticated()):
        return redirect('/login')
    p = Project(request.user.id)
    archive = p.archive_list(project_id)
    return render_to_response('archive.html', {"archive":archive})

# the project wizard
# @todo move sql to another file
class ProjectWizard(SessionWizardView):
    template_name = "project_form_wizard.html"

    def done(self, form_list, **kwargs):
        print "the kwargs: %s" % kwargs
        print "the self: %s" % self
        form_data = {"name":"", "price":0}
        frm_data  = [form.cleaned_data for form in form_list]
        form_data["name"] = frm_data[0]['name'] # projectNameForm
        form_data["price"] = frm_data[1]['price'] #projectPriceForm

        p = Project(self.request.user.id)
        msg = "failed creating project"
        if p.create_project(form_data):
            msg = "successfully created project"
        return redirect("/?flash=%s" % (msg,))

# "private" methods...?
def project_not_found(project_id):
    return HttpResponse("""
                        Unable to find project with id %s and not already started...
                        """ % (project_id,))
