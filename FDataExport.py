import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# coding=utf-8

class FDataExport:
    def __init__(self):
        # Подключение к Google Sheets
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("ruin-keepers.json", scope)
        client = gspread.authorize(creds)

        # Открытие таблицы
        spreadsheet_list = client.openall()
        for sheet in spreadsheet_list:
            print(sheet.title)

        spreadsheet = client.open("database")
        sheet = spreadsheet.sheet1

        # Подключение к SQLite
        conn = sqlite3.connect("flsite.db")
        cursor = conn.cursor()

        # Получить все события
        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()

        # Заголовки
        column_names = [description[0] for description in cursor.description]
        sheet.insert_row(column_names, 1)

        # Данные
        for i, row in enumerate(rows, start=2):
            sheet.insert_row(row, i)

        print("Экспорт завершён.")


if __name__ == "__main__":
    FDataExport()
