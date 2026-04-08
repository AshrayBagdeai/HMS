import sqlite3

conn=sqlite3.connect('hms.db')
curr=conn.cursor()
data=curr.execute('''select * from patients''').fetchall()

print(data)
conn.commit()
curr.close()
conn.close()