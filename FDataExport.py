import sqlite3
import pygsheets
from FDataBase import FDataBase

def FDataExport():

    # === Настройки ===
    DATABASE_PATH = "flsite.db"
    CREDENTIALS_PATH = "ruin-keepers.json"
    SHEET_NAME = "database"

    # === Подключение к БД и Google Sheets ===
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Для работы с dict-подобным выводом
    db = FDataBase(conn)

    gc = pygsheets.authorize(service_file=CREDENTIALS_PATH)

    # === Создание или открытие Google Sheet ===
    try:
        sh = gc.open(SHEET_NAME)
    except pygsheets.SpreadsheetNotFound:
        sh = gc.create(SHEET_NAME)

    # === Функция записи таблицы ===
    def export_table(table_name: str, data: list[sqlite3.Row], worksheet_index: int):
        # Удаляем лист, если существует
        try:
            sh.del_worksheet(sh.worksheet('index', worksheet_index))
        except Exception:
            pass

        # Создаём новый лист
        ws = sh.add_worksheet(table_name, rows=1000, cols=20, index=worksheet_index)

        if not data:
            ws.update_value('A1', f"No data in table '{table_name}'")
            return

        # Подготавливаем заголовки и строки
        headers = list(data[0].keys())
        rows = [headers] + [list(row) for row in data]

        # Обновляем таблицу
        ws.update_values('A1', rows)


    # === Получаем и экспортируем все таблицы ===
    tables = [
        ("events", db.getEvents()),
        ("users", conn.cursor().execute("SELECT * FROM users").fetchall()),
        ("admins", conn.cursor().execute("SELECT * FROM admins").fetchall())
    ]

    for i, (table_name, data) in enumerate(tables):
        export_table(table_name, data, i)

    print("✅ Экспорт завершён!")
if __name__ == "__main__":
    FDataExport()