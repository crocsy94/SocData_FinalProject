import sqlite3
import re
from collections import Counter
import time
import datetime
import csv
import pandas
import itertools

# custom function for regex in SQLite
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# establish connection
conn = sqlite3.connect('pedestrian.db')
conn.create_function("REGEXP", 2, regexp)
cursor = conn.cursor()

# create list of dates
dates_lower = [d.strftime('%d-%b-%Y') for d in pandas.date_range('20160101','20161231')]
dates = [date.upper() for date in dates_lower]
#dates = ['01-JAN-2016']

# open output file
output_file = open('output_pedestrian_year.csv', 'w')
output_file.write("unix_time,day,sensor_id,count,sensor_description,latitude,longitude\n")

# convert each row coming from the query to coma separated string
def conv2String(row):
  line = ''
  for i,element in enumerate(row):
    # replace is needed because the number are separated after every 3 digit with a coma
    line += str(element).replace(',','') + ','
  return line

# for every day in 2016
for date in dates:
  t = [' ' + date + '.*']
  buffer = []
  # get all the datapoint for the specific day and format them as string, store them in data_points
  cursor.execute('SELECT day, sensor_id, SUM(hourly_count) FROM data WHERE date_time REGEXP ? GROUP BY sensor_id', t)
  data_points = [conv2String(row) for row in cursor.fetchall()]

  for data_point in data_points:
    # find sensor_id, query in the other table for extra data, add them to each string (datapoint)
    sensor_id = data_point.split(',')[1]
    cursor.execute('SELECT description,latitude,longitude FROM location WHERE ID=?', (sensor_id,))
    query = cursor.fetchall()[0]
    data_point += conv2String(query)
    # convert date to unix time, date is converted to lovercase because %b should be lowercase, but the dates are with uppercase in the db
    unix_date = time.mktime(datetime.datetime.strptime(date.lower(), "%d-%b-%Y").timetuple())
    # final formatting and saving to buffer
    data_point = str(unix_date)[:-2] + ',' + data_point[:-1]
    buffer.append(data_point)
    
  # write buffer to file
  output_file.write("\n".join(buffer) + "\n")
  print(date)

output_file.close()
print("Done")