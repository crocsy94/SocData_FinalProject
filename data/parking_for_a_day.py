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

# create list of hours
hours = [d.strftime('%m/%d/%Y %I:') for d in pandas.date_range('201602050000','201602052300', freq='H')]
# hours = [d.strftime('%m/%d/%Y %I:') for d in pandas.date_range('201602050000','201602050200', freq='H')]

# open output file
output_file = open('output_parking_hourly.csv', 'w')
output_file.write("unix_time,st_marker_id,count,latitude,longitude\n")

# convert each row coming from the query to coma separated string
def conv2String(row):
  line = ''
  for i,element in enumerate(row):
    # replace is needed because the number are separated after every 3 digit with a coma
    line += str(element).replace(',','') + ','
  return line

pm_am = 'AM'
# for every day in 2016
for i, hour in enumerate(hours):
  if i == 12:
    pm_am = 'PM'
  t = [hour + '.{6}' + pm_am]
  buffer = []

  # get all the datapoint for the specific day
  cursor.execute('SELECT st_marker_id, COUNT(st_marker_id) FROM data WHERE departure_date REGEXP ? GROUP BY st_marker_id', t)
  data_points = [conv2String(row) for row in cursor.fetchall()]

  # to unix time
  timestamp = hour + '00:00 ' + pm_am
  unix_date = time.mktime(datetime.datetime.strptime(timestamp, "%d/%m/%Y %I:%M:%S %p").timetuple())

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
  print(timestamp)

output_file.close()
print("Done")