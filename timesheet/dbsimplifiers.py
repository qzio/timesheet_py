# -*- coding: utf-8 -*-

from django.db import connection, transaction

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

def fetchall(sql, params):
    cursor = connection.cursor()
    cursor.execute(sql, params)
    return dictfetchall(cursor)

def fetchone(sql, params):
    cursor = connection.cursor()
    cursor.execute(sql, params)
    return dictfetchone(cursor)
