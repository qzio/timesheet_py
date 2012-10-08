# -*- coding: utf-8 -*-

import time
from datetime import datetime
import pickle

from dbsimplifiers import *

class Project:
    """
    a class to wrap calls to storage(db)
    filtered by user
    """

    def __init__(self, user_id):
        self.user_id = user_id

    def project_list(self):
        self.__projects = fetchall("select * from projects where user_id = %s", (self.user_id,))
        for i, proj in enumerate(self.__projects):
            self.__projects[i] = dict(proj.items() + {'current_time': (proj['current_time'] / 60 / 60.0)}.items())
        return self.__projects

    def project(self, project_id):
        project = fetchone("select * from projects "
                       "where id = %s and user_id = %s limit 1",
                       (project_id, self.user_id))
        return project

    def started(self):
        if self.__projects == None:
            self.__projects = self.project_list()
        for project in self.__projects:
            if project["started_at"] > 0:
                return project["id"]
        return None


    def create_project(self, data):
        return dbexec("insert into projects (user_id, name, price, started_at) "
            "values (%s, %s, %s, 0)",
            (self.user_id, data["name"], data["price"]))

    def start_tracking(self, project_id):
        current_project = self.project(project_id)
        if current_project == None :
            return 0

        changed_rows = dbexec("update projects set started_at = %s "
                "where id = %s",
                (int(time.time()), project_id))
        return 1 if (changed_rows > 0) else 0

    def stop_tracking(self, project_id):
        current_project = self.project(project_id)
        if current_project == None :
            return 0

        started_at = current_project['started_at']
        stopped_at = int(time.time())
        diff = (stopped_at - started_at)

        old_current_time = current_project['current_time'] if (current_project['current_time'] > 0.0) else 0.0
        new_current_time = (old_current_time + diff)

        updated_project_rows = dbexec("update projects set "
                "started_at = 0, `current_time` = %s where id = %s",
                (new_current_time, project_id))
        if updated_project_rows > 0.0:
            updated_tracked_rows = dbexec("insert into tracked_times "
                    "(project_id, started_at, stopped_at, diff) values "
                    "(%s, %s, %s, %s)",
                    (project_id, started_at, stopped_at, diff))
            if updated_tracked_rows > 0.0:
                return 1
        return 0

    def tracked_times(self, project_id, entries = False):
        project = self.project(project_id)
        if project == None:
            return (None, None, None)
        rows = fetchall("select * from tracked_times where project_id = %s order by stopped_at desc",
                (project_id,))

        # calculate total based on tracked_times; NOT the cached de-normalized value from `projects`
        total = 0.0
        result = {}
        has_result = False
        for row in rows:
            d = datetime.fromtimestamp(row['started_at'])
            iso_tuple = d.isocalendar()
            week = "w%s" % iso_tuple[1]
            if (entries == False or ("{0}".format(row["id"]) in entries)):
                if (week not in result):
                    result[week] = []
                row['hour_diff'] = row['diff'] / 60.0 / 60.0
                result[week].append(row)
                total = total + row['diff']
                has_result = True
        total = total / 60.0 / 60.0

        if has_result:
            return (project, total, result)
        else:
            print "no entries in list"
            return (None, None, None)

    def delete(self, project_id):
        deleted_projects = dbexec("delete from projects where id = %s and user_id = %s",
                (project_id, self.user_id))
        return 1 if deleted_projects > 0 else 0

    def archive_tracked_times(self, project_id, period, entries):
        (project, total, tracked_times)= self.tracked_times(project_id, entries)
        if project == None or len(period) < 1:
            return 0

        total_time = total * 60.0 * 60.0 # better save it in seconds
        total_sum = total * project["price"]

        # collect all the ids of the tracked_times entries
        tt_ids = []
        for k,week in tracked_times.items():
            tt_ids = tt_ids + [row["id"] for row in week]

        if len(tt_ids) <= 0:
            print "not archive any tracked_times rows? {0}, {1}".format(project_id, period)
            return 0

        # insert summurize as one row into archive
        dbexec("insert into archived_history (project_id, period, total_time, total_sum, period_data) VALUES "
                "(%s, %s, %s, %s ,%s)",
                (project_id, period, total_time, total_sum, pickle.dumps(tracked_times)))

        # only delete the specified rows
        sql = "delete from tracked_times where project_id = %s and id in({0})".format(",".join(map(str, tt_ids)))
        dbexec(sql, (project_id,))
        dbexec("update projects set `current_time` = 0 where id = %s", (project_id,))
        return 1

    def archive_list(self, project_id):
        project = self.project(project_id)
        if project == None:
            return []
        return fetchall("select * from archived_history where project_id = %s",
                (int(project['id']),))
