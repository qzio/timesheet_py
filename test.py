#!/usr/bin/python
import MySQLdb

# connect
db = MySQLdb.connect(host="localhost", user="root", password="", db="timesheet_py")

cursor = db.cursor()

cursor.execute('select * from projects')

numrows = int(cursor.rowcount)

for x in range(0,numrows):
  row = cursor.fetchone()
  print row[0], " => ", row[1]
