import sqlite3
import os

DB_PATH = os.path.join("resource", "students.db")

class Student:
    def __init__(self, id_, name, surname, patronymic, group, grades):
        self.id = id_
        self.name = name
        self.surname = surname
        self.patronymic = patronymic
        self.group = group
        self.grades = grades

    def average(self):
        return sum(self.grades) / len(self.grades) if self.grades else 0


class StudentDB:
    def __init__(self, db=DB_PATH):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, surname TEXT, patronymic TEXT,
                group_name TEXT, g1 REAL, g2 REAL, g3 REAL, g4 REAL
            )
        """)
        self.conn.commit()

    def add(self, s: Student):
        self.cur.execute(
            "INSERT INTO students (name,surname,patronymic,group_name,g1,g2,g3,g4) VALUES (?,?,?,?,?,?,?,?)",
            (s.name, s.surname, s.patronymic, s.group, *s.grades)
        )
        self.conn.commit()
        print("Студент добавлен")

    def get_all(self):
        self.cur.execute("SELECT * FROM students")
        return [self._row_to_s(r) for r in self.cur.fetchall()]

    def get_by_id(self, sid):
        self.cur.execute("SELECT * FROM students WHERE id=?", (sid,))
        r = self.cur.fetchone()
        return self._row_to_s(r) if r else None

    def update(self, s: Student):
        self.cur.execute(
            "UPDATE students SET name=?,surname=?,patronymic=?,group_name=?,g1=?,g2=?,g3=?,g4=? WHERE id=?",
            (s.name, s.surname, s.patronymic, s.group, *s.grades, s.id)
        )
        self.conn.commit()
        print("Студент обновлён")

    def delete(self, sid):
        self.cur.execute("DELETE FROM students WHERE id=?", (sid,))
        self.conn.commit()
        print("Студент удалён")

    def group_average(self, group):
        self.cur.execute("SELECT * FROM students WHERE group_name=?", (group,))
        rows = self.cur.fetchall()
        if not rows:
            return None
        avgs = [self._row_to_s(r).average for r in rows]
        return sum(avgs) / len(avgs)

    def _row_to_s(self, row):
        return Student(row[0], row[1], row[2], row[3], row[4], [row[5], row[6], row[7], row[8]])

    def close(self):
        self.conn.close()


def input_grades():
    print("Введите 4 оценки:")
    return [float(input(f"  {i+1}: ")) for i in range(4)]


def main():
    db = StudentDB()
    while True:
        print("\n1-Добавить 2-Все 3-Поиск 4-Редактировать 5-Удалить 6-Средний группы 0-Выход")
        c = input("Выбор: ")
        if c == "1":
            s = Student(None, input("Имя: "), input("Фамилия: "), input("Отчество: "),
                       input("Группа: "), input_grades())
            db.add(s)
        elif c == "2":
            for s in db.get_all():
                print(f"{s.id}: {s.surname} {s.name}, гр.{s.group}, ср.балл: {s.average:.2f}")
        elif c == "3":
            sid = int(input("ID: "))
            s = db.get_by_id(sid)
            print(f"{s.surname} {s.name}, оценки: {s.grades}, ср.балл: {s.average:.2f}" if s else "Не найден")
        elif c == "4":
            sid = int(input("ID: "))
            s = db.get_by_id(sid)
            if s:
                s.name = input(f"Имя [{s.name}]: ") or s.name
                s.surname = input(f"Фамилия [{s.surname}]: ") or s.surname
                s.patronymic = input(f"Отчество [{s.patronymic}]: ") or s.patronymic
                s.group = input(f"Группа [{s.group}]: ") or s.group
                print("Оценки:")
                s.grades = [float(input(f"{i+1}: ") or s.grades[i]) for i in range(4)]
                db.update(s)
        elif c == "5":
            db.delete(int(input("ID: ")))
        elif c == "6":
            avg = db.group_average(input("Группа: "))
            print(f"Средний балл: {avg:.2f}" if avg is not None else "Группа не найдена")
        elif c == "0":
            db.close()
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":

    main()
