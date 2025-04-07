import sqlite3

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()

    def addEvent(self, name, description, photoPath, place, cost: int):
        sql = """INSERT INTO events (name, description, photoPath, place, cost) VALUES (?, ?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (name, description, photoPath, place, cost))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add event to database:", str(e))

    def getEventByName(self, name):
        sql = f"""SELECT * FROM events WHERE name = '{name}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchon()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get event by name:", str(e))
        return {}

    def getEventById(self, id):
        sql = f"""SELECT * FROM events WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get event by id:", str(e))
        return {}

    def getEvents(self):
        sql = """SELECT * FROM events"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get all events:", str(e))
        return []

    def addUser(self, eventID, name, telegram, phone, birth):
        #if (telegram)
        sql = """INSERT INTO users(eventID, name, phone, birth, telegram) VALUES (?, ?, ?, ?, ?)"""
        #else:
            #sql = """INSERT INTO users(eventID, name, phone, birth) VALUES (?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (eventID, name, phone, birth, telegram))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add user:", str(e))

    def getUserByLogin(self, login):
        sql = f"""SELECT * FROM users WHERE login='{login}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get user by login:", str(e))
        return []

    def getUserById(self, id):
        sql = f"""SELECT * FROM users WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get user by id:", str(e))
        return {}
