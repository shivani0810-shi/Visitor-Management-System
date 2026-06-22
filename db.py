import mysql.connector

db = mysql.connector.connect(
    host="vms-database-shishiv0810-3e4a.e.aivencloud.com",
    port=16021,
    user="avnadmin",
    password="AVNS_dNf7ZTVuxQ_5LX2GbJa",
    database="defaultdb",
    ssl_disabled=False
)

cursor = db.cursor(dictionary=True)

print("Connected Successfully!")