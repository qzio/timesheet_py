# -*- coding: utf-8 -*-

from django.db import connection, transaction
import time
from datetime import datetime

# sqlite helper methods (not used)
def fetchall(cursor, sql):
  result = []
  cursor.execute(sql)
  rows = cursor.fetchall()
  for row in rows:
    t = {}
    for key in row:
      t[str(key)] = row[str(key)]
    result.append(t)
  return result

def dict_factory(cursor, row):
  d = {}
  for idx,col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def projects_to_dicts(projects):
  rows = []
  for proj in projects:
    rows.append(project_to_dict(proj))
  return rows


def project_to_dict(project_tuple):
  return {"id":project_tuple[0], "name":project_tuple[1], "price":project_tuple[2]}


# actually used

# projects:
# CREATE TABLE projects (id integer primary key, name varchar(255), price integer, started_at integer);
# tracked_times
# CREATE TABLE tracked_times (id integer primary key, project_id integer, started_at integer, stopped_at integer, diff integer);

def dictfetchall(cursor):
  desc = cursor.description
  return [
    dict(zip([col[0] for col in desc], row))
    for row in cursor.fetchall()
  ]

def dictfetchone(cursor):
  desc = cursor.description
  result = [
    dict(zip([col[0] for col in desc], row))
    for row in cursor.fetchall()
  ]
  return result[0] if len(result) > 0 else None

# execute an sql query that will insert/update
def dbexec(sql, params):
  cursor = connection.cursor()
  cursor.execute(sql, params)
  transaction.commit_unless_managed()
  return cursor.rowcount

def project_fetch(project_id):
  cursor = connection.cursor()
  cursor.execute("select * from projects where id = %s limit 1", (project_id,))
  return dictfetchone(cursor)

def project_fetch_all():
  cursor = connection.cursor()
  cursor.execute("select * from projects")
  projects = dictfetchall(cursor)
  return projects

def started_project(projects):
  for project in projects:
    if project['started_at'] > 0 :
      return project['id']
  return None

def start_track_project(project_id):
  if dbexec("update projects set started_at = %s where id = %s", (int(time.time()), project_id)) > 0:
    return 1
  return 0

def stop_track_project(project_id):

  project = project_fetch(project_id)
  if project == None:
    print "no project found..."
    return 0

  started_at = project['started_at']
  stopped_at = time.time()

  cursor = connection.cursor()
  cursor.execute("update projects set started_at = 0 where id = %s",
      (project_id,))
  transaction.commit_unless_managed()
  if cursor.rowcount > 0:
    cursor = connection.cursor()
    cursor.execute("insert into tracked_times "
                   "(project_id, started_at, stopped_at, diff) values "
                   "(%s, %s, %s, %s)", (project_id, started_at, stopped_at, (stopped_at - started_at)))
    transaction.commit_unless_managed()
    if cursor.rowcount > 0:
      return 1
    else:
      print "failed to save into tracked time"
  else:
    print "failed to transaction.commit the first time"

  return 0


def project_total(project_id):
  cursor = connection.cursor()
  cursor.execute("select sum(diff) as total from tracked_times where project_id = %s", (int(project_id,)))
  row = dictfetchone(cursor)
  total_hours = row['total'] / 60.0 / 60.0
  return total_hours

def project_history(project_id):
  cursor = connection.cursor()
  cursor.execute("select * from tracked_times where project_id = %s order by stopped_at desc", (project_id,))
  rows = dictfetchall(cursor)
  total = 0.0
  result = {}
  for row in rows:
    d = datetime.fromtimestamp(row['started_at'])
    iso_tuple = d.isocalendar()
    week = "w%s" % iso_tuple[1]
    if (week not in result):
      result[week] = []
    row['hour_diff'] = row['diff'] / 60 / 60
    result[week].append(row)
    total = total + row['diff']

  print "result: %s" % (result,)
  total = total / 60.0 / 60.0
  return (total, result)
