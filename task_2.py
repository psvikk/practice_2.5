import sqlite3

conn = sqlite3.connect("resource/drinks.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS ingredients (id INTEGER PRIMARY KEY, name TEXT, stock REAL, cost REAL)")
c.execute(
    "CREATE TABLE IF NOT EXISTS alcohols (id INTEGER PRIMARY KEY, name TEXT, strength REAL, stock REAL, cost REAL)")
c.execute("CREATE TABLE IF NOT EXISTS cocktails (id INTEGER PRIMARY KEY, name TEXT, strength REAL, price REAL)")
c.execute("CREATE TABLE IF NOT EXISTS composition (cid INTEGER, type TEXT, item_id INTEGER, volume REAL)")
conn.commit()

while True:
    print("\n1-Склад 2-Ингредиент 3-Алкоголь 4-Коктейль 5-Продать 6-Пополнить 0-Выход")
    ch = input("> ")

    if ch == "1":
        print("Ингредиенты:")
        for r in c.execute("SELECT * FROM ingredients"): print(r)
        print("Алкоголь:")
        for r in c.execute("SELECT * FROM alcohols"): print(r)
        print("Коктейли:")
        for r in c.execute("SELECT * FROM cocktails"): print(r)

    elif ch == "2":
        c.execute("INSERT INTO ingredients (name,stock,cost) VALUES (?,?,?)",
                  (input("Название: "), float(input("Остаток: ")), float(input("Цена: "))))
        conn.commit()

    elif ch == "3":
        c.execute("INSERT INTO alcohols (name,strength,stock,cost) VALUES (?,?,?,?)",
                  (input("Название: "), float(input("Крепость%: ")), float(input("Остаток: ")), float(input("Цена: "))))
        conn.commit()

    elif ch == "4":
        name = input("Название: ")
        price = float(input("Цена: "))
        comps = []
        print("Состав (тип ing/alc, id, объём).")
        while True:
            line = input("> ")
            if not line: break
            t, iid, vol = line.split()
            comps.append((t, int(iid), float(vol)))

        # Расчёт крепости
        total_vol = sum(v for _, _, v in comps)
        pure_alc = sum(c.execute("SELECT strength FROM alcohols WHERE id=?", (iid,)).fetchone()[0] * v / 100
                       for t, iid, v in comps if t == "alc")
        strength = round(pure_alc / total_vol * 100, 2) if total_vol else 0

        c.execute("INSERT INTO cocktails (name,strength,price) VALUES (?,?,?)", (name, strength, price))
        cid = c.lastrowid
        for t, iid, vol in comps:
            c.execute("INSERT INTO composition VALUES (?,?,?,?)", (cid, t, iid, vol))
        conn.commit()
        print(f"Крепость: {strength}%")

    elif ch == "5":
        cid = int(input("ID коктейля: "))
        qty = int(input("Кол-во: ") or 1)
        for t, iid, vol in c.execute("SELECT type,item_id,volume FROM composition WHERE cid=?", (cid,)):
            tbl = "ingredients" if t == "ing" else "alcohols"
            stock = c.execute(f"SELECT stock FROM {tbl} WHERE id=?", (iid,)).fetchone()[0]
            if stock < vol * qty:
                print("Недостаточно");
                break
            c.execute(f"UPDATE {tbl} SET stock=stock-? WHERE id=?", (vol * qty, iid))
        else:
            conn.commit()
            print("Продано")

    elif ch == "6":
        tbl = "ingredients" if input("Тип (ing/alc): ") == "ing" else "alcohols"
        c.execute(f"UPDATE {tbl} SET stock=stock+? WHERE id=?", (float(input("Объём: ")), int(input("ID: "))))
        conn.commit()
        print("Пополнено")

    elif ch == "0":
        conn.close()

        break
