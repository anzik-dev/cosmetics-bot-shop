import sqlite3
from pathlib import Path

# Пути к БД
BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB = BASE_DIR / 'Бот в тг' / 'local_orders.db'
MAIN_DB = BASE_DIR / 'Общая БД' / 'orders.db'

# Подключаемся к локальной базе (источник)
conn_local = sqlite3.connect(LOCAL_DB)
cursor_local = conn_local.cursor()

# Подключаемся к основной базе (назначение)
conn_main = sqlite3.connect(MAIN_DB)
cursor_main = conn_main.cursor()

# Создаем таблицу products, если нет
cursor_main.execute("""
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT,
    stock INTEGER
)
""")

# Очистим старые данные (если нужно)
cursor_main.execute("DELETE FROM products")

# Получаем все товары из локальной базы
cursor_local.execute("SELECT id, name, stock FROM products")
rows = cursor_local.fetchall()

# Вставляем в основную базу
cursor_main.executemany("INSERT INTO products (id, name, stock) VALUES (?, ?, ?)", rows)

# Сохраняем изменения и закрываем соединения
conn_main.commit()
conn_local.close()
conn_main.close()

print(f"✅ Скопировано {len(rows)} товаров из локальной БД в основную.")
