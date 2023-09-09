import pymysql

db = pymysql.connect(host="localhost",user="root",password="root")
cursor = db.cursor()
cursor.execute("select version()")
print(cursor.fetchone())

