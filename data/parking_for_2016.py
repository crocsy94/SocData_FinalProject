import sqlite3
import re
from collections import Counter
import time
import datetime
import csv
import pandas

# custom function for regex in SQLite
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# establish connection
conn = sqlite3.connect('parking.db')
conn.create_function("REGEXP", 2, regexp)
cursor = conn.cursor()

# create list of dates
dates = [d.strftime('%m/%d/%Y') for d in pandas.date_range('20160101','20161231')]
# dates = [d.strftime('%m/%d/%Y') for d in pandas.date_range('20160101','20160201')]

# open output file
output_file = open('output_parking.csv', 'w')
output_file.write("unix_time,st_marker_id,count,latitude,longitude\n")

# convert each row coming from the query to coma separated string
def conv2String(row):
  line = ''
  for i,element in enumerate(row):
    # replace is needed because the number are separated after every 3 digit with a coma
    line += str(element).replace(',','') + ','
  return line

# for every day in 2016
for date in dates:
  t = [date + '.*']
  buffer = []

  # get all the datapoint for the specific day
  cursor.execute('SELECT st_marker_id, COUNT(st_marker_id) FROM data WHERE departure_date REGEXP ? GROUP BY st_marker_id', t)
  data_points = [conv2String(row) for row in cursor.fetchall()]

  # to unix time
  unix_date = time.mktime(datetime.datetime.strptime(date, "%m/%d/%Y").timetuple())
      
  # iterate through the dictionary resulted from the counter operation
  for data_point in data_points:
    # lookup location for every st_marker_id
    st_marker_id = data_point.split(',')[0]
    cursor.execute('SELECT lat,lon FROM location WHERE st_marker_id=?', (st_marker_id,))
    location = cursor.fetchall()

    # if location exists
    if len(location) != 0:
      # create output string separated with coma
      data_point += conv2String(location[0])
      data_point = str(unix_date)[:-2] + ',' + data_point[:-1]
      # append to list
      buffer.append(data_point)

  output_file.write("\n".join(buffer) + "\n")
  print(date)

output_file.close()
print("Done")