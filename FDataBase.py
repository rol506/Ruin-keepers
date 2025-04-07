import pygsheets 

class FDataBase:
    def __init__(self, service_account_file):
        self.client:pygsheets.Client = pygsheets.authorize(service_account_file=service_account_file)
        self.spreadsht = self.client.open("database")
        self.worksht = self.spreadsht.worksheet("title", "Sheet1")
        self.lastid=2
    def createDB(self):
        headers = [
        "ID","Who", "Phone", "Source", "Total", "Age", "Children", "XP", "New", "Prepayment", "Destination", "Comment", "Lunch", "Reminder", "Confirmation", "Balance", "Nickname", "Feedback"
        ]
        for i in range(len(headers)):
            col_letter = chr(65 + i)
            cell = f"{col_letter}1"
            self.worksht.update_value(cell, headers[i])
    def dropDB(self):
        self.worksht.clear()
    def insert(self, Who, Phone, Source, Total, Age, Children, XP, New, Prepayment, Comment, Lunch, Reminder, Confirmation, Balance, Destination, Nickname, Feedback):
        Id = self.lastid
        self.lastid+=1
    def find(self):
        Id = self.lastid
        self.lastid+=1
        
if __name__ == "__main__":
    db = FDataBase("ruin-keepers.json")
    db.createDB()
