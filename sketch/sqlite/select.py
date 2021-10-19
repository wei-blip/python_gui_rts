import sqlite3

db = sqlite3.connect("../../rts.sq")
cursor = db.cursor()

select_req='''SELECT main.sn, main.uut_dev_eui, meas.* FROM meas INNER JOIN main ON  meas.main_sn = main.sn and  main.sn = '123456000' '''
# select_req='''SELECT * FROM main'''

cursor.execute(select_req)
aa = cursor.fetchall()
column_names = [description[0] for description in cursor.description]
print(column_names)
print(aa)

db.close()