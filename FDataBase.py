import sqlite3

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()

    def __del__(self):
        self.__db.close()

    def addEvent(self, name, description, date, time, photoPath, place, cost: int, type="event"):
        sql = """INSERT INTO events (name, description, photoPath, place, cost, date, time, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (name, description.replace("\n", "<br>"), photoPath, place, cost, date, time, type))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add event to database:", str(e))

    def removeEventById(self, id):

        #remove associated users
        users = self.getUsersByEvent(id)
        for u in users:
            self.removeUserByID(u["id"])

        #remove the event
        sql = f"""DELETE FROM events WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove event by id:", str(e))

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

    def getEventsByDate(self, date):
        sql = f"""SELECT * FROM events WHERE date = '{date}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get events by day:", str(e))
        return []

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
        """None values will not be updated"""
        #if (telegram)
        sql = """INSERT INTO users (eventID, name, phone, birth, telegram) VALUES (?, ?, ?, ?, ?)"""
        #else:
            #sql = """INSERT INTO users(eventID, name, phone, birth) VALUES (?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (eventID, name, phone, birth, telegram))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add user:", str(e))

    def updateUser(self, userID, name, telegram, phone, birth):
        #get last record
        usr = self.getUserById(userID)

        name = usr['name'] if name is None else name
        telegram = usr['telegram'] if telegram is None else telegram
        phone = usr['phone'] if phone is None else phone
        birth = usr['birth'] if birth is None else birth

        sql = f"""UPDATE users SET name='{name}', telegram='{telegram}', phone='{phone}', birth='{birth}' WHERE id='{userID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to update user data by id:", str(e))

    def removeUserByPhone(self, phone, eventID):
        sql = f"""DELETE FROM users WHERE phone='{phone}' AND eventID='{eventID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove user by phone:", str(e))

    def removeUserByTelegram(self, telegram, eventID):
        sql = f"""DELETE FROM users WHERE telegram='{telegram}' AND eventID='{eventID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove user by telegram:", str(e))

    def removeUserById(self, userID):
        sql = f"""DELETE FROM users WHERE id='{userID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove user by id:", str(e))

    def getUsersByEvent(self, eventID):
        sql = f"""SELECT * FROM users WHERE eventID ='{eventID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get users by event:", str(e))
        return []

    def getTelegramCount(self, telegram, eventID) -> int | None:
        '''Returns None in case of an error'''
        sql = f"""SELECT COUNT(id) AS cnt FROM users WHERE telegram='{telegram}' AND eventID='{eventID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return int(res["cnt"])
        except sqlite3.Error as e:
            print("Failed to get count of telegrams:", str(e))
            return None
        return 0

    def getPhoneCount(self, phone, eventID) -> int | None:
        '''Returns None in case of an error'''
        sql = f"""SELECT COUNT(id) AS cnt FROM users WHERE phone='{phone}' AND eventID='{eventID}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return int(res["cnt"])
        except sqlite3.Error as e:
            print("Failed to get count of phones:", str(e))
            return None
        return 0

    def getUserEventsByPhone(self, phone):
        sql = f"""SELECT eventID FROM user WHERE phone='{phone}'"""
        try:
            self.__cur.execute(sql)
            IDs = self.__cur.fetchall()

            res = []

            for i in IDs:
                sql = f"""SELECT * FROM events WHERE id='{i['eventID']}'"""
                self.__cur.execute(sql)
                res.append(self.__cur.fetchone())

            if res: return res
        except sqlite3.Error as e:
            print("Failed to get events of the user:", str(e))
        return []

    def getUserEventsByTelegram(self, telegram):
        sql = f"""SELECT eventID FROM user WHERE telegram='{telegram}'"""
        try:
            self.__cur.execute(sql)
            IDs = self.__cur.fetchall()

            res = []

            for i in IDs:
                sql = f"""SELECT * FROM events WHERE id='{i['eventID']}'"""
                self.__cur.execute(sql)
                res.append(self.__cur.fetchone())

            if res: return res
            
        except sqlite3.Error as e:
            print("Failed to get events of the user:", str(e))
        return []

    def getUserByPhone(self, phone):
        sql = f"""SELECT * FROM users WHERE phone='{phone}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get user by phone:", str(e))
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

    def addAdmin(self, login, role: bool):
        """if role -> admin role is GreatAdmin else just admin"""
        sql = """INSERT INTO admins (login, role) VALUES (?, ?)"""
        if (bool(role)):
            role = "GreatAdmin"
        else:
            role = "admin"
        try:
            self.__cur.execute(sql, (login, role))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add admin:", str(e))

    def getAdminByLogin(self, login) -> str | None:
        '''Returns admin role or None if not found'''
        sql = f"""SELECT * FROM admins WHERE login='{login}'"""
        try:
            self.__cur.execute(sql);
            res = self.__cur.fetchone()
            if res: return res["role"]
        except sqlite3.Error as e:
            print("Failed to get admin role by login:", str(e))
        return None

    def removeAdminByLogin(self, login):
        '''Removes admin if it's role is not GreatAdmin (other is admin)'''
        sql = f"""DELETE FROM admins WHERE login='{login}' and role='admin'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by login:", str(e))

