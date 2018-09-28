import pymysql
import re

f = open("dict.txt")
db = pymysql.connect("localhost",'root','123456','dictory')

cursor = db.cursor()

for line in f:
    l = re.split(r'\s+',line)
    word = l[0]
    values = ' '.join(l[1:])

    sql = "insert into dictory1 (word, value) \
    values('%s','%s')"%(word,values)

    try:
        cursor.execute(sql)
        db.commit()

    except:
        db.rollback()
f.close()