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
  projects = project_fetch_all(connection.cursor())
  c = {'projects':projects,
      'project_started':started_project(projects)}
  c.update(csrf(request)) # is it just or is this just plain stupid; should be handled by the framework.
  print "project_started: %s" % c['project_started']
  return render_to_response('home.html', c)

def projects_start(request, project_id):
  cursor = connection.cursor()
  project = project_fetch(cursor, int(project_id))
  if (project == None):
    return project_not_found(project_id)

  cursor = connection.cursor()
  r = start_track_project(cursor, int(project_id))
  msg = "failed to start project"
  if r > 0:
    msg = "successfully started tracking project"
  return redirect("/?msg=%s" % (msg,))


def projects_stop(request, project_id):
  # is it just me or does it feel wrong to must create a new cursor?
  # gief global db object?!
  cursor = connection.cursor()
  r = stop_track_project(cursor, int(project_id))
  msg = "Failed to stop tracking time"
  if r > 0:
    msg = "successfully stopped tracking time"
  return redirect("/?msg=%s" % msg)

def projects_history(request, project_id):
  project = project_fetch(connection.cursor(), int(project_id))
  (total_diff, history) = project_history(int(project_id))
  c = {
    "project" : project,
    "history" : history,
    "total_diff":total_diff
  }

  return render_to_response('history.html', c)

def projects_delete(request, project_id):
  cursor = connection.cursor()
  msg = "fail"
  pid = int(project_id)
  # transaction.commit_unless_managed() is wat 
  # is it possible to get some kind of results?
  cursor.execute("delete from projects where id = %s", (pid,))
  transaction.commit_unless_managed()

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

    cursor = connection.cursor()
    r = cursor.execute("insert into projects (name, price, started_at) values (%s, %s, 0)", (form_data['name'], form_data['price']))
    tr = transaction.commit_unless_managed()
    return redirect("/?flash=success")

# "private" methods
def project_not_found(project_id):
    return HttpResponse("""
                        Unable to find project with id %s and not already started...
                        """ % (project_id,))
