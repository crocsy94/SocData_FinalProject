import sqlite3
import re
from collections import Counter
import time
import datetime
import csv
import numpy as np
import pandas
import itertools

# custom function for regex in SQLite
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# establish connection to pedestrian db
conn_ped = sqlite3.connect('pedestrian.db')
conn_ped.create_function("REGEXP", 2, regexp)
cursor_ped = conn_ped.cursor()

# establish connection to parking db
conn_par = sqlite3.connect('parking.db')
conn_par.create_function("REGEXP", 2, regexp)
cursor_par = conn_par.cursor()

# create list of dates for pedestrian
dates_lower = [d.strftime('%d-%b-%Y') for d in pandas.date_range('20160101','20161231')]
dates_ped = [date.upper() for date in dates_lower]

# create list of dates for parking
dates_par = [d.strftime('%m/%d/%Y') for d in pandas.date_range('20160101','20161231')]

# open output file
output_file = open('output_pedestrian_and_parking_year_sum.csv', 'w')
output_file.write("unix_time,count_pedestrian,count_parking\n")

buffer = []

# for every day in 2016
for i,date in enumerate(dates_ped):
  t_pedestrian = [' ' + date + '.*']
  t_parking = [dates_par[i] + '.*']

  # get all the the PEDESTRIAN sensor counts for a day
  cursor_ped.execute('SELECT SUM(hourly_count) FROM data WHERE date_time REGEXP ?', t_pedestrian)
  count_pedestrian = str(cursor_ped.fetchall()[0][0])

  # get all the the PARKING sensor counts for a day
  cursor_par.execute('SELECT COUNT(st_marker_id) FROM data WHERE departure_date REGEXP ?', t_parking)
  count_parking = str(cursor_par.fetchall()[0][0])

  # convert date to unix time, date is converted to lovercase because %b should be lowercase, but the dates are with uppercase in the db
  unix_date = time.mktime(datetime.datetime.strptime(date.lower(), "%d-%b-%Y").timetuple())

  data_point = str(unix_date)[:-2] + ',' + count_pedestrian + ',' + count_parking
  buffer.append(data_point)
  print(date)

# write buffer to file
output_file.write("\n".join(buffer) + "\n")

output_file.close()
print("Done")