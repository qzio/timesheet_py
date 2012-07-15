import sqlite3

connection = sqlite3.connect("db.sqlite3")

tables = [
    "CREATE TABLE projects "
    "(id integer primary key, user_id integer, name varchar(255), price integer, started_at integer, current_time integer)",

    " CREATE TABLE tracked_times "
    "(id integer primary key, project_id integer, started_at integer, stopped_at integer, diff integer)",

    "CREATE TABLE archived_history "
    "(project_id integer, period varchar(100), total_time integer, total_sum integer, period_data text)"
    ]


for create_table_sql in tables:
    print "%s" % create_table_sql
    cursor = connection.cursor()
    cursor.execute(create_table_sql)
    connection.commit()
