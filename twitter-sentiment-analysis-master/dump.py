#!/usr/bin/env python3

import sqlite3
import sys

db = sqlite3.connect(sys.argv[1])

cursor = db.cursor()

cnt = 0
for row in cursor.execute('SELECT tweet_id,airline_sentiment,text FROM Tweets;'):
    if row[1] == 'positive':
        with open('data/0/%d.txt' % row[0], mode='w+') as f:
            f.write(row[2])
    elif row[1] == 'neutral':
        with open('data/1/%d.txt' % row[0], mode='w+') as f:
            f.write(row[2])
    elif row[1] == 'negative':
        with open('data/2/%d.txt' % row[0], mode='w+') as f:
            f.write(row[2])
