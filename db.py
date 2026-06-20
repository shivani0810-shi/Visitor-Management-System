import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8060$Shi",
    database="VisitorManagementSystem"
)

cursor = db.cursor(dictionary=True)

print("Connected Successfully!")
