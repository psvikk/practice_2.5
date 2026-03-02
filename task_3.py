import requests
import sqlite3
import os

DB_PATH = os.path.join("resource", "currencies.db")


class CurrencyDB:
    def __init__(self, db=DB_PATH):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS group_currencies (gid INTEGER, code TEXT, UNIQUE(gid, code))")
        self.conn.commit()

    def create_group(self, name):
        try:
            self.cur.execute("INSERT INTO groups (name) VALUES (?)", (name,))
            self.conn.commit()
            print("Группа создана")
        except sqlite3.IntegrityError:
            print("Группа уже существует")

    def add_to_group(self, group_name, code):
        self.cur.execute("SELECT id FROM groups WHERE name=?", (group_name,))
        row = self.cur.fetchone()
        if not row:
            print("Группа не найдена")
            return
        try:
            self.cur.execute("INSERT INTO group_currencies VALUES (?,?)", (row[0], code))
            self.conn.commit()
            print("Валюта добавлена в группу")
        except sqlite3.IntegrityError:
            print("Валюта уже в группе")

    def remove_from_group(self, group_name, code):
        self.cur.execute("SELECT id FROM groups WHERE name=?", (group_name,))
        row = self.cur.fetchone()
        if not row:
            print("Группа не найдена")
            return
        self.cur.execute("DELETE FROM group_currencies WHERE gid=? AND code=?", (row[0], code))
        self.conn.commit()
        print("Валюта удалена из группы")

    def show_groups(self):
        self.cur.execute("SELECT name FROM groups")
        groups = self.cur.fetchall()
        if not groups:
            print("Нет созданных групп")
            return
        for (name,) in groups:
            self.cur.execute("""
                SELECT gc.code FROM group_currencies gc 
                JOIN groups g ON gc.gid=g.id WHERE g.name=?
            """, (name,))
            codes = [r[0] for r in self.cur.fetchall()]
            print(f"{name}: {', '.join(codes) if codes else 'пусто'}")

    def save(self):
        self.conn.commit()
        print("Данные сохранены")

    def close(self):
        self.conn.close()

currency_data = None

def fetch_currency_rates():
    global currency_data
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    response.raise_for_status()
    currency_data = response.json()

def show_all_currencies():
    for code, info in currency_data['Valute'].items():
        print(f"{code}: {info['Name']} = {info['Value']} ₽ за {info['Nominal']}")

def show_currency_by_code(code):
    info = currency_data['Valute'].get(code)
    if info:
        print(f"{code}: {info['Name']} = {info['Value']} ₽ за {info['Nominal']}")
    else:
        print("Валюта не найдена")


def main():
    db = CurrencyDB()
    fetch_currency_rates()

    while True:
        print("\n1-Все валюты 2-Поиск по коду 3-Создать группу 4-Группы 5-Добавить в группу 6-Удалить из группы 7-Сохранить 8-Выход")
        choice = input("Выбор: ")

        if choice == '1':
            show_all_currencies()
        elif choice == '2':
            show_currency_by_code(input("Код валюты: "))
        elif choice == '3':
            db.create_group(input("Название группы: "))
        elif choice == '4':
            db.show_groups()
        elif choice == '5':
            db.add_to_group(input("Группа: "), input("Код валюты: "))
        elif choice == '6':
            db.remove_from_group(input("Группа: "), input("Код валюты: "))
        elif choice == '7':
            db.save()
        elif choice == '8':
            db.save()
            db.close()
            break
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()