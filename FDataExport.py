import sqlite3
import pygsheets

# Подключение к базе SQLite
conn = sqlite3.connect("your_database.db")
cur = conn.cursor()

gc = pygsheets.authorize("ruin-keepers.json")
sh = gc.open("database") 
events_ws = sh.worksheet_by_title("Events")
users_ws = sh.worksheet_by_title("Users")

events_ws.clear()
users_ws.clear()

cur.execute("SELECT * FROM events")
events = cur.fetchall()
event_headers = [description[0] for description in cur.description]
events_ws.update_row(1, event_headers)
if events:
    events_ws.update_values('A2', events)

cur.execute("SELECT * FROM users")
users = cur.fetchall()
user_headers = [description[0] for description in cur.description]
users_ws.update_row(1, user_headers)
if users:
    users_ws.update_values('A2', users)

print("Данные успешно перенесены!")

conn.close()
