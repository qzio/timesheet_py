# -*- coding: utf-8 -*-
# Create your views here.
import sqlite3
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib.formtools.wizard.views import SessionWizardView

from sqlitehelpers import *

from django.db import connection, transaction

def home(request):
  projects = project_fetch_all()
  c = {'projects':projects,
      'project_started':started_project(projects)}
  c.update(csrf(request)) # am I doing this wrong? is there a better way?
  print "project_started: %s" % c['project_started']
  return render_to_response('home.html', c)

def projects_start(request, project_id):
  project = project_fetch(int(project_id))
  if (project == None):
    return project_not_found(project_id)

  msg = "failed to start project"
  if start_track_project(int(project_id)) > 0:
    msg = "successfully started tracking project"
  return redirect("/?msg=%s" % (msg,))


def projects_stop(request, project_id):
  project = project_fetch(int(project_id))
  if (project == None):
    return project_not_found(project_id)
  msg = "Failed to stop tracking time"
  
  if stop_track_project(int(project_id)) > 0:
    msg = "successfully stopped tracking time"
  return redirect("/?msg=%s" % msg)

def projects_history(request, project_id):
  project = project_fetch(int(project_id))
  (total_diff, history) = project_history(int(project_id))
  c = {
    "project" : project,
    "history" : history,
    "total_diff":total_diff
  }

  return render_to_response('history.html', c)

def projects_delete(request, project_id):
  msg = "failed to delete"
  if dbexec("delete from projects where id = %s", (int(project_id),)) > 0 :
    msg ="success deleting project"
  return redirect("/?flash=%s" % msg)

# the project wizard
# @todo move sql to another file
class ProjectWizard(SessionWizardView):
  template_name = "project_form_wizard.html"

  def done(self, form_list, **kwargs):
    form_data = {"name":"", "price":0}
    frm_data  = [form.cleaned_data for form in form_list]
    form_data["name"] = frm_data[0]['name'] # projectNameForm
    form_data["price"] = frm_data[1]['price'] #projectPriceForm

    msg = "failed to create project"
    sql = "insert into projects (name, price, started_at) values(%s, %s, 0)"
    params = (form_data['name'], form_data['price'])
    if dbexec(sql,params) > 0:
      msg = "successfully created project"
    return redirect("/?flash=%s" % (msg,))

# "private" methods...?
def project_not_found(project_id):
    return HttpResponse("""
                        Unable to find project with id %s and not already started...
                        """ % (project_id,))
