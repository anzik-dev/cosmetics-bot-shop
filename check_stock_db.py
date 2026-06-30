import sqlite3

# Подключаем базу данных
conn = sqlite3.connect('Бот в тг\local_orders.db')
cursor = conn.cursor()

# Покажем все таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Таблицы в orders.db:", tables)

# Проверим структуру таблицы products
try:
    cursor.execute("PRAGMA table_info(products);")
    columns = cursor.fetchall()
    print("\nСтруктура таблицы products:")
    for col in columns:
        print(col)

    # Покажем первые 5 товаров
    cursor.execute("SELECT * FROM products LIMIT 5;")
    rows = cursor.fetchall()
    print("\nПервые 5 строк:")
    for row in rows:
        print(row)

except sqlite3.Error as e:
    print("\nОшибка при работе с таблицей products:", e)

conn.close()
