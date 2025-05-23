import sqlite3

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()

    def __del__(self):
        self.__db.close()

    def addEvent(self, name, description, date, time, photoPath, place, cost: int, lunchCost=-1, tpe="event"):
        sql = """INSERT INTO events (name, description, photoPath, place, cost, date, time, lunchCost, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (name, description.replace("\n", "<br>"), photoPath, place, cost, date, time, lunchCost, tpe))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add event to database:", str(e))

    def removeEventByID(self, id):

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

    def getEventsByMonth(self, month):
        sql = f"""SELECT * FROM events WHERE (date >= '{month}-01') AND (date < '{month}-31')"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get events by month:", str(e))
        return []

    def getEventByID(self, id):
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

    def updateEvent(self, eventID, name, description=None, date=None, time=None, photoPath=None, place=None, cost: int=None,  lunchCost=None, tpe="event"):
        """None values will not be updated"""
        ev = self.getEventByID(eventID)

        #type is reserved Python word

        name = ev['name'] if name is None else name
        description = ev['description'] if description is None else description
        date = ev['date'] if date is None else date
        time = ev['time'] if time is None else time
        photoPath = ev['photoPath'] if photoPath is None else photoPath
        place = ev['place'] if place is None else place
        cost = ev['cost'] if cost is None else cost
        tpe = ev['type'] if tpe is None else tpe
        lunchCost = ev["lunchCost"] if lunchCost is None else lunchCost

        sql = f"""UPDATE events SET name='{name}', description='{description}', date='{date}', time='{time}', photoPath='{photoPath}',
                                    place='{place}', cost='{cost}', lunchCost='{lunchCost}', type='{tpe}' WHERE id='{eventID}'"""

        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to update event by id:", str(e))

    def addUser(self, eventID, name, telegram, phone, birth, lunch: int):
        #if (telegram)
        sql = """INSERT INTO users (eventID, name, phone, birth, telegram, lunch) VALUES (?, ?, ?, ?, ?, ?)"""
        #else:
            #sql = """INSERT INTO users(eventID, name, phone, birth) VALUES (?, ?, ?, ?)"""
        try:
            self.__cur.execute(sql, (eventID, name, phone, birth, telegram, lunch))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add user:", str(e))

    def updateUser(self, userID, name, telegram, phone, birth, lunch):
        #get last record
        usr = self.getUserByID(userID)

        name = usr['name'] if name is None else name
        telegram = usr['telegram'] if telegram is None else telegram
        phone = usr['phone'] if phone is None else phone
        birth = usr['birth'] if birth is None else birth
        lunch = usr["lunch"] if lunch is None else lunch

        sql = f"""UPDATE users SET name='{name}', telegram='{telegram}', phone='{phone}', birth='{birth}', lunch='{lunch}' WHERE id='{userID}'"""
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

    def removeUserByID(self, userID):
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

    def getUserByID(self, id):
        sql = f"""SELECT * FROM users WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get user by id:", str(e))
        return {}
    def getUsers(self):
        sql = """SELECT * FROM users"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Failed to get users:", str(e))
        return []

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
    def getAdmin(self):
        sql = """SELECT * FROM admins"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Failed to get admins:", str(e))
        return []
    def getAdminByID(self, id):
        sql = f"""SELECT * FROM admins WHERE id = '{id}'"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get admin by id:", str(e))
        return {}
    def removeAdminByID(self, AdminID):
        sql = f"""DELETE FROM admins WHERE id='{AdminID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by id:", str(e))
    def updateAdmin(self, adminID, role):
        #get last record
        adm = self.getAdminByID(adminID)
        role = adm['role'] if role is None else role
        
        sql = f"""UPDATE admins SET role='{role}' WHERE id='{adminID}'"""
        try:
            self.__cur.execute(sql)
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to update adm data by id:", str(e))