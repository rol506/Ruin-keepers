import pygsheets 

class FDataBase:
    def __init__(self, service_account_file):
        self.client:pygsheets.Client = pygsheets.authorize(service_account_file=service_account_file)
        self.spreadsht = self.client.open("database")
        self.worksht = self.spreadsht.worksheet("title", "Sheet1")
    def createDB(self):
        headers = [
        "Who", "Phone", "Source", "Total", "Age", "Children", "XP", "New", "Prepayment", "Destination", "Comment", "Lunch", "Reminder", "Confirmation", "Balance", "Destination", "Nickname", "Feedback"

        ]
        for i in range(len(headers)):
            col_letter = chr(65 + i)
            cell = f"{col_letter}1"
            self.worksht.update_value(cell, headers[i])
    def dropDB(self):
        self.worksht.clear()
if __name__ == "__main__":
    db = FDataBase("ruin-keepers.json")
    db.createDB()
    print(db.client.spreadsheet_titles())
    db.dropDB()
