import telebot
from telebot import types
import sqlite3
import os
import time
import threading
import json
from pathlib import Path
from dotenv import load_dotenv
#Удаление надписи после задержки
def delete_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# ==================== Настройки ====================
TOKEN = 'BOT_TOKEN'
GROUP_CHAT_ID = "CHAT_ID"
ADMIN_ID = "ADMIN_ID"  #Telegram ID администратора

# Путь к базе данных
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent  # Бот в тг
COMMON_DB_DIR = BASE_DIR.parent / "Общая БД"  # папка с основной базой

DB_NAME = os.getenv("DB_NAME", "local_orders.db")

# Выбираем путь в зависимости от имени базы
if DB_NAME == "orders.db":
    DB_PATH = COMMON_DB_DIR / DB_NAME
else:
    DB_PATH = BASE_DIR / DB_NAME  # локальная база

print("Подключаемся к базе:", DB_PATH)
print("Файл существует:", DB_PATH.exists())

def get_connection():
    return sqlite3.connect(DB_PATH)


# Инициализация бота
bot = telebot.TeleBot(TOKEN)


# ==================== Функции работы с БД ====================

'''def init_db():
    """Создает таблицы products и orders, если их нет."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Таблица товаров
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        name TEXT,
        stock INTEGER
    )
    """)
    # Таблица заказов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        phone TEXT,
        products_json TEXT,
        total_price REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()'''





def init_stock(products_clean: dict) -> int:
    """Один раз добавляет товары из словаря в таблицу products."""
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0
    for pid, data in products_clean.items():
        cursor.execute(
            "INSERT OR IGNORE INTO products (id, name, stock) VALUES (?, ?, ?)",
            (pid, data['name'], data['stock'])
        )
        if cursor.rowcount:
            inserted += 1
    conn.commit()
    conn.close()
    return inserted


def get_stock_from_db(product_id: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def update_stock_in_db(product_id: str, new_stock: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()


def save_order(user_name: str, user_address: str, user_phone: str,
               cart_items: dict, total_price: float) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (name, address, phone, products_json, total_price) VALUES (?, ?, ?, ?, ?)",
        (user_name, user_address, user_phone, json.dumps(cart_items, ensure_ascii=False), total_price)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

# ==================== Данные о товарах ====================
products_clean = {
    '1': {
        'name': 'ACWELL LICORICE PH BALANCING ESSENCE MIST',
        'short_name': 'ACWELL',
        'short_description':'эссенция-спрей для увлажнения и выравнивания pH',
         'photo':os.path.join("images", "1. ACWELL.JPG"),
        'price': 8900,
        'stock': 10,
        'description': 'Идеален для обладателей чувствительной, обезвоженной, уставшей кожи, кому нужен нежный уход и увлажнение. Подойдёт как ежедневный увлажняющий мист в сухих помещениях или после очищения.'
    },
    '2': {
        'name': 'ACWELL LICORICE PH BALANCING INTENSIVE EYE CREAM',
        'short_name': 'ACWELL',
        'short_description':'крем для кожи вокруг глаз',
        'photo':os.path.join("images", "2. ACWELL eye cream.JPG"),
        'price': 10400,
        'stock': 10,
        'description': 'В подборке лучших корейских кремов для глаз от Glamour ACWELL Licorice pH Balancing Intensive Eye Cream назван одним из лучших для борьбы с тёмными кругами благодаря комбинации солодки, пептидов, кофеина и антиоксидантов.'
    },
    '3': {
        'name': "SAM'U GALACTO PORE 02 TONER",
        'short_name': "SAM'U",
        'short_description': 'тоник для сужения пор',
        'photo': os.path.join("images", "3. GALACTO PORE toner.JPG"),
        'stock': 10,
        'price': 7990,
        'description': 'Это корейский тоник, предназначенный для сужения пор, увлажнения и улучшения текстуры кожи. Он сочетает в себе ферментированные компоненты, кислородные пузырьки и растительные экстракты, что делает его подходящим для жирной, комбинированной и склонной к акне кожи.'
    },
    '4': {
        'name': "SAM'U GALACTO PORE SERUM",
        'short_name': "SAM'U",
        'short_description':'сыворотка для пор и текстуры кожи',
        'photo': os.path.join("images", "4. GALACTO PORE SERUM.JPG"),
        'price': 9990,
        'stock': 10,
        'description': "Предназначенная для сужения пор, улучшения текстуры кожи и увлажнения. Она является частью популярной линии Galacto Pore от бренда SAM'U, известного своими средствами с ферментированными компонентами."
    },
    '5': {
        'name': "SAM'U WATER TO AMPOULE TREATMENT ",
        'short_name': "SAM'U",
        'short_description':'увлажняющая эссенция-тонер',
        'photo': os.path.join("images", "17. SAMU.JPG"),
        'price': 12900,
        'stock': 10,
        'description': 'Это несмываемая ампульная сыворотка для волос, предназначенная для интенсивного увлажнения и восстановления структуры волос'
    },
    '6': {
        'name': "SAM'U PH SENSITIVE AMPOULE",
        'short_name': "SAM'U",
        'short_description':'ампула для чувствительной кожи',
        'photo': os.path.join("images", "6. PH SENSITIVE AMPOULE(сыворотка).JPG"),
        'price': 13200,
        'stock': 10,
        'description': 'Сыворотке-ампуле для чувствительной и сухой кожи: Идеальна для чувствительной, сухой и комбинированной кожи; Придаёт увлажнение и комфорт без липкости; Прекрасно работает как сыворотка после тонера.'
    },
    '7': {
        'name': "SAM'U PH SENSITIVE CREAM",
        'short_name': "SAM'U",
        'short_description':' увлажняющий крем для чувствительной кожи',
        'photo': os.path.join("images", "7. PH SENSITIVE CREAM.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'Это качественный корейский уходовый крем в тюбике, сохраняющий влагу, балансирует pH и подходит для разных типов кожи. Рекомендован, если ищешь нежную текстуру и барьерную защиту.'
    },
    '8': {
        'name': "SAM'U PH SENSITIVE CREAM MIST",
        'short_name': "SAM'U",
        'short_description':'крем-спрей для увлажнения',
        'photo': os.path.join("images", "8. PH SENSITIVE CREAM MIST.JPG"),
        'price': 10590,
        'stock': 10,
        'description': 'Легчайший крем в формате миста. Удобен для применения в любое время дня:\n• используется как основа под макияж,\n• как фиксатор макияжа,\n• как средство для освежения и увлажнения в течение дня.'
    },
    '9': {
        'name': "SAM'U PHSENSITIVE FACIAL TREATMENT",
        'short_name': "SAM'U",
        'short_description':'средство для восстановления кожи',
        'photo': os.path.join("images", "9. PH SENSITIVE FACIAL TREATMENT.JPG"),
        'price': 13590,
        'stock': 10,
        'description': 'Ты ищешь заключительный этап ухода — ампула-лосьон, укрепляющая барьер и удерживающая влагу. Твоя кожа сухая, чувствительная или комбинированная, и нужна лёгкая, но эффективная формула. Ты хочешь удобное базовое средство под макияж с pH балансом.'
    },
    '10': {
        'name': "SAM'U SENSITIVE POCKET SUN STICK",
        'short_name': "SAM'U",
        'short_description':'солнцезащитный стик',
        'photo': os.path.join("images", "10. SENSITIVE POCKET SUN STICK.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'СПФ компактная Удобен для мгновенного нанесения и повторного применения в течение дня, без рук . Текстура не оставляет блеска и не белит, ощущается лёгкая и бархатная.'
    },
    '11': {
        'name': "SAM'U PH SENSITIVE SPOT CREAM",
        'short_name': "SAM'U",
        'short_description':'точечный крем от воспалений',
        'photo': os.path.join("images", "11. PH SENSITIVE SPOT CREAM.JPG"),
        'price': 7990,
        'stock': 10,
        'description': 'Это локальное средство, которое:\n• Наносится точечно на участки покраснений, раздражений, шелушений;\n• Помогает успокоить кожу, особенно если есть высыпания, раздражение, зуд, сухость;\n• Подходит для чувствительной, реактивной, склонной к дерматиту кожи.'
    },
    '12': {
        'name': "SAM'U PH SENSITIVE SUN CREAM",
        'short_name': "SAM'U",
        'short_description':'солнцезащитный крем для чувствительной кожи',
        'photo': os.path.join("images", "12. PH SENSITIVE SUNCREAM.JPG"),
        'price': 8990,
        'stock': 10,
        'description': 'Защита SPF 50+ PA++++ без белого следа; Увлажняющий и барьер защитный эффект — особенно для сухой, комбинированной и чувствительной кожи; Лёгкая текстура, уход под макияж, без липкости.'
    },
    '13': {
        'name': "SAM'U PH SENSITIVE TONER PAD(RENEWAL)",
        'short_name': "SAM'U",
        'short_description':'пэды с успокаивающим тоником',
        'photo': os.path.join("images", "13. PH SENSITIVE TONER PAD.JPG"),
        'price': 10005,
        'stock': 10,
        'description': 'Это мягкие, комфортные тонер-пады с акцентом на увлажнение, pH-баланс и бережное очищение. Отличный выбор в качестве освежающего ухода и экспресс-маски, особенно для чувствительной кожи.'
    },
    '14': {
        'name': "SAM’U BORN PANTHENOL JELLY WASH",
        'short_name': "SAM'U",
        'short_description':'гель для умывания с пантенолом',
        'photo': os.path.join("images", "14. Born Panthenol(JELLY WASH).JPG"),
        'price': 7800,
        'stock': 10,
        'description': 'Это корейское очищающее средство с текстурой желе, предназначенное для увлажнения и успокоения кожи. Подходит для:\n• Сухой и чувствительной кожи, нуждающейся в увлажнении и успокоении.\n• Тех, кто ищет мягкое очищающее средство без агрессивных компонентов'
    },
    '15': {
        'name': "DEW CARE VITAMIN TO- GLOW PACK",
        'short_name': "DEW CARE",
        'short_description':'мини-набор с витаминными средствами',
        'photo': os.path.join("images", "15. BRIGHT SIDE UP.JPG"),
        'price': 13000,
        'stock': 10,
        'description': "🍊 Bright Side Up (серум с витамином C)\n📌 Для чего: Осветляет пигментацию, придаёт коже сияние, защищает от свободных радикалов.\n👤 Кому подойдёт: Для тусклой, усталой, неровной кожи.\n🧪 Активы: Витамин C, ниацинамид, экстракт грейпфрута.\n\n💧 Say You Dew (увлажняющий крем)\n📌 Для чего: Увлажняет и смягчает кожу, улучшает барьер.\n👤 Кому подойдёт: Сухой, комбинированной коже.\n🧪 Формула: Гелевая, освежающая, с витаминами C и E, лимонным экстрактом.\n\n💄 Plush Party (ночная маска для губ)\n📌 Для чего: Питает, восстанавливает губы во время сна.\n🧪 Активы: Масло какао, витамин E, пептиды."
    },
    '16': {
        'name': 'I DEW CARE THIRST THINGS FIRST',
         'short_name': "DEW CARE",
        'short_description':'увлажняющий витаминный мист',
        'photo': os.path.join("images", "16. THIRST THINGS FIRST.JPG"),
        'price': 12500,
        'stock': 10,
        'description': 'Обеспечивают сияние, увлажнение и защиту кожи . Подходит для: сухой, обезвоженной, тусклой кожи; фиксации макияжа; свежести в течение дня; ночной маски-спрея .'
    },
    '17': {
        'name': "I DEW CARE LET'S GET SHEET FACED",
        'short_name': "DEW CARE",
        'short_description':'набор тканевых масок для лица',
        'photo': os.path.join("images", "5. IN THE ZONE.JPG"),
        'price': 19500,
        'stock': 10,
        'description': 'Маска увлажняющая.'
    }
    
}

# ==================== Глобальные переменные ====================
carts = {}              # {user_id: [ {product_id, name, price, quantity, photo}, ... ]}
user_states = {}        # для оформления заказа
last_quantity_prompt = {}  # для удаления сообщения с запросом
catalog_messages_ids = {}
cart_message_ids = {}
admin_product_ids = {}
cart_message_ids = {}
edit_message_ids = {} 
user_cart_messages = {}



# ==================== Клавиатуры ====================

def main_menu_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton('Уходовая косметика 🧴', callback_data='clean'))
    kb.add(types.InlineKeyboardButton('Декоративная косметика 💄', callback_data='makeup'))
    kb.add(types.InlineKeyboardButton('Корзина 🛒', callback_data='cart'))
    kb.add(types.InlineKeyboardButton('Cкидка 💸', callback_data='discount'))
    return kb


def confirm_keyboard(product_id=None):
    kb = types.InlineKeyboardMarkup(row_width=2)
    if product_id:
        kb.add(types.InlineKeyboardButton('✅ Добавить', callback_data=f'add_{product_id}'))
        kb.add(types.InlineKeyboardButton('❌ Отмена', callback_data=f'cancel_{product_id}'))
    else:
        kb.add(types.InlineKeyboardButton('✅ Оформить заказ', callback_data='checkout'))
        kb.add(types.InlineKeyboardButton('✏️ Редактировать корзину', callback_data='edit_cart'))
        kb.add(types.InlineKeyboardButton('🔙 Главное меню', callback_data='main_menu'))
    return kb


def post_add_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton('🛍 Продолжить покупки', callback_data='continue_shopping'))
    kb.add(types.InlineKeyboardButton('🔙 Главное меню', callback_data='main_menu'))
    return kb


def back_to_menu_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('🔙 Главное меню', callback_data='main_menu'))
    return kb

# ==================== Обработчики ====================

@bot.message_handler(commands=['start'])
def start(message):
    text = (
    "Здравствуйте 👋, дорогой покупатель!\n\n"
    "*Добро пожаловать в GLOW&CO COSMETICS* — магазин корейской косметики премиум-качества 💄\n\n"
    "Данный бот поможет вам легко и быстро оформить заказ.\n\n"
    "🏠 Это ваше главное меню. Выберите нужный раздел ниже, чтобы начать покупки!")
    bot.send_message(
        message.chat.id,text,parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(commands=['init_stock'])
def cmd_init_stock(message):
    if message.chat.id != ADMIN_ID:
        return bot.reply_to(message, '❌ Доступ запрещен')
    count = init_stock(products_clean)
    bot.reply_to(message, f'✅ Добавлено товаров: {count}')

@bot.message_handler(commands=['reset_orders'])
def cmd_reset_orders(message):
    if message.chat.id != ADMIN_ID:
        return bot.reply_to(message, '❌ Доступ запрещен')

    conn = get_connection()
    cursor = conn.cursor()

    # Удаляем все заказы
    cursor.execute('DELETE FROM orders')

    # Сбрасываем счётчик AUTOINCREMENT
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="orders"')

    conn.commit()
    conn.close()

    bot.reply_to(message, '✅ История заказов и счётчик сброшены (следующий заказ будет #1)')



# Админ-панель управления stock
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for index, product_id in enumerate(products_clean.keys(), start=1):
        product_data = products_clean[product_id]
        name = product_data['name']

        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        stock = row[0] if row else 0

        text = f"*{index}. {name}* — `{stock}` шт."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✏️ Изменить количество", callback_data=f"set_{product_id}"))

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=markup
        )

    conn.close()


# Обработка запроса на изменение
@bot.callback_query_handler(lambda c: c.data.startswith('set_'))
def ask_set_stock(call):
    pid = call.data.split('_')[1]
    admin_product_ids[call.message.chat.id] = pid
    bot.send_message(call.message.chat.id, f"Введите новое количество для ID {pid}:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_set_stock)

# Обработка ввода нового количества
def process_set_stock(message):
    user_id = message.chat.id
    pid = admin_product_ids.get(user_id)
    try:
        new_stock = int(message.text)
    except:
        return bot.send_message(user_id, "❌ Введите число.")

    update_stock_in_db(pid, new_stock)
    bot.send_message(user_id, f"✅ Обновлено: ID {pid} = {new_stock}")


# Каталог
@bot.callback_query_handler(lambda c: c.data=='clean')
def clean_handler(call):
    user_id = call.from_user.id
    delete_subscribe_message(user_id)
    show_catalog(call)

def show_catalog(call):
    bot.delete_message(call.message.chat.id,call.message.message_id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    for pid,p in products_clean.items():
        kb.add(types.InlineKeyboardButton(f"{p['name']} — {p['short_description']}",callback_data=f'product_{pid}'))
      # Добавляем кнопку "Главное меню" в конец
    kb.add(types.InlineKeyboardButton('🔙 Главное меню', callback_data='main_menu'))   
    sent=bot.send_message(call.message.chat.id,'✨ Наш каталог готов для вас! Выберите товар ниже:',reply_markup=kb)
    catalog_messages_ids[call.message.chat.id]=sent.message_id

@bot.callback_query_handler(lambda c: c.data=='makeup')
def makeup_handler(call):
    user_id = call.from_user.id
    delete_subscribe_message(user_id)
    show_makeup(call)

def show_makeup(call):
    bot.answer_callback_query(call.id)
    sent=bot.send_message(call.message.chat.id,'💄 Раздел *Декоративная косметика* скоро будет доступен!\n\n🔔 Следите за обновлениями!',parse_mode='Markdown')
    time.sleep(3)
    bot.delete_message(call.message.chat.id,sent.message_id)

@bot.callback_query_handler(lambda c: c.data.startswith('product_'))
def show_product(call):
    pid=call.data.split('_')[1]; p=products_clean.get(pid)
    if not p: return bot.answer_callback_query(call.id,'❌ Нет')
    stock=get_stock_from_db(pid)
    price=f"{p['price']:,}".replace(',',' ')
    text=(f"📦 <b>{p['name']}</b>\n\n{p['description']}\n\n"
          f"💰 Цена: {price}₸\n🔢 В наличии: {stock} шт.\n")
    try:
        with open(p['photo'],'rb') as ph:
            bot.send_photo(call.message.chat.id,ph,caption=text,parse_mode='HTML',reply_markup=confirm_keyboard(pid))
    except:
        bot.send_message(call.message.chat.id,text,parse_mode='HTML',reply_markup=confirm_keyboard(pid))
    bot.answer_callback_query(call.id)

#Отмена добавления в корзину
@bot.callback_query_handler(lambda c: c.data.startswith('cancel_'))
def cancel_add(c):
    uid = c.message.chat.id
    prod_id = c.data.split('_', 1)[1]

    # отвечаем, чтобы убрать «крутилку»
    bot.answer_callback_query(c.id)

    # удаляем карточку товара
    try:
        bot.delete_message(uid, c.message.message_id)
    except:
        pass

# Добавление в корзину
@bot.callback_query_handler(lambda c: c.data.startswith('add_'))
def add_to_cart(call):
    uid = call.message.chat.id
    pid = call.data.split('_')[1]
    bot.answer_callback_query(call.id)

    # Получаем остаток
    stock = get_stock_from_db(pid)
    if stock <= 0:
        if stock <= 0:
            try:
                bot.delete_message(uid, call.message.message_id)
            except:
                pass

        no_msg=bot.send_message(uid, "❌ Товара больше нет в наличии.")
        threading.Thread(
            target=delete_after_delay,
            args=(uid, no_msg.message_id, 3)
        ).start()
        return
       


    # Спрашиваем, сколько штук
    msg = bot.send_message(uid, "🔢 Сколько штук вы хотите заказать?")
    last_quantity_prompt[uid] = msg.message_id
    bot.register_next_step_handler(msg, process_quantity, pid, call.message.message_id)


def process_quantity(message, pid, product_msg_id):
    uid = message.chat.id

    # Удаляем запрос о количестве
    try:
        bot.delete_message(uid, last_quantity_prompt.get(uid, 0))
        bot.delete_message(uid, message.message_id)
    except:
        pass

    # Парсим количество
    try:
        qty = int(message.text)
        if qty < 1:
            raise ValueError
    except ValueError:
        error = bot.send_message(uid, "❌ Введите целое число больше нуля:")
        last_quantity_prompt[uid] = error.message_id
        bot.register_next_step_handler(error, process_quantity, pid, product_msg_id)
        return

    # Проверяем остаток
    stock = get_stock_from_db(pid)
    if qty > stock:
        error = bot.send_message(uid, f"⚠️ На складе только {stock} шт. Введите меньшее количество:")
        last_quantity_prompt[uid] = error.message_id
        bot.register_next_step_handler(error, process_quantity, pid, product_msg_id)
        return

    # Уменьшаем остаток в БД
    update_stock_in_db(pid, stock - qty)

    # Добавляем в корзину
    item = next((i for i in carts.get(uid, []) if i['product_id'] == pid), None)
    if item:
        item['quantity'] += qty
    else:
        p = products_clean[pid]
        carts.setdefault(uid, []).append({
            'product_id': pid,
            'name': p['name'],
            'price': p['price'],
            'quantity': qty,
            'photo': p['photo']
        })

    # Удаляем саму карточку товара (фото + текст)
    try:
        bot.delete_message(uid, product_msg_id)
    except:
        pass

    # Подтверждение и кнопки “продолжить/в меню”
    bot.send_message(
        uid,
        f"✅ Добавлено в корзину: {qty}шт. «{products_clean[pid]['name']}»\n\nНажмите на одну из кнопок ниже ⬇️",
        reply_markup=post_add_keyboard()
    )


#Код с разделом скидки
# Словарь для хранения ID сообщений с предложением подписки
subscribe_messages = {}  # Храним ID сообщений с предложением подписки
def delete_subscribe_message(user_id):#Функция как раз таки для удаления сообщения про скидку
    if user_id in subscribe_messages:
        try:
            bot.delete_message(chat_id=user_id, message_id=subscribe_messages[user_id])
        except Exception as e:
            print(f"Ошибка при удалении подписочного сообщения: {e}")
        finally:
            del subscribe_messages[user_id]

@bot.callback_query_handler(lambda c: c.data == 'discount')
def discount_handler(call):
    user_id = call.from_user.id
    delete_subscribe_message(user_id)

    if check_subscription(user_id):
        text = "🎉 Вы уже подписаны на наш канал!\n✅ Скидка 5% активна на все заказы."
        msg = bot.send_message(user_id, text)
        time.sleep(5)
        try:
            bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")
    else:
        text = (
            "💡 Подпишитесь на наш канал и получите скидку 5% на заказ!\n"
            "🔗 Канал: https://t.me/glowandco"
        )

        markup = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton("📲 Перейти в канал", url="https://t.me/glowandco")
        btn_check = types.InlineKeyboardButton("🔄 Проверить подписку", callback_data="check_subscription")
        markup.add(btn_channel)
        markup.add(btn_check)

        msg = bot.send_message(user_id, text, reply_markup=markup)

        # Сохраняем ID этого сообщения, чтобы потом удалить
        subscribe_messages[user_id] = msg.message_id



def delete_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

@bot.callback_query_handler(lambda c: c.data == 'check_subscription')
def check_subscription_handler(call):
    user_id = call.from_user.id

    if check_subscription(user_id):
        # Удаляем сообщение с кнопками
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass

        # Отправляем новое сообщение
        msg = bot.send_message(user_id, "🎉 Подписка подтверждена!\n✅ Скидка 5% активирована на все заказы.")

        # Удаляем через 5 секунд в отдельном потоке
        threading.Thread(target=delete_after_delay, args=(user_id, msg.message_id, 5)).start()
    else:
       msg= bot.send_message(user_id, "❌ Вы пока не подписаны.")
       threading.Thread(target=delete_after_delay, args=(user_id, msg.message_id, 2)).start()


def check_subscription(user_id):
    try:
        member = bot.get_chat_member("@glowandco", user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

@bot.message_handler(commands=['test_sub'])
def test_sub(message):
    try:
        member = bot.get_chat_member("@glowandco", message.from_user.id)
        bot.send_message(message.chat.id, f"Статус: {member.status}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# 1) Просмотр корзины
@bot.callback_query_handler(lambda c: c.data == 'cart')
def cart_handler(call):
    user_id = call.from_user.id
    delete_subscribe_message(user_id)
    show_cart(call)

def show_cart(call):
    uid = call.message.chat.id

    # Удаляем старый просмотр (но не меню удаления)
    for mid in cart_message_ids.get(uid, []):
        try: bot.delete_message(uid, mid)
        except: pass
    cart_message_ids[uid] = []

    # Удаляем только главное меню
    try:
        bot.delete_message(uid, call.message.message_id)
    except: pass

    cart = carts.get(uid, [])
    if not cart:
        sent = bot.send_message(uid, "🛒 Ваша корзина пуста.", reply_markup=back_to_menu_keyboard())
        cart_message_ids[uid].append(sent.message_id)
        return
   
    # Проверяем подписку
    is_subscribed = check_subscription(uid)

    # Строим красивое сообщение
    text = "🧺 *Корзина товаров:*\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    total = 0
    for i, item in enumerate(cart, start=1):
        name = item['name']
        quantity = item['quantity']
        price = item['price']
        subtotal = price * quantity
        total += subtotal

        text += (
            f"🔹 *{i}. {name}*\n"
            f"   📦 Кол-во: {quantity} шт.\n"
            f"   💰 Цена: {price} тг/шт\n"
            f"   🧾 Сумма: {subtotal} тг\n"
            "-------------------------\n"
        )

    # Добавляем финальную часть текста в зависимости от скидки
    if is_subscribed:
        discount_amount = total * 0.05
        discounted_total = total - discount_amount
        text += f"💵 *Общая сумма без скидки:* {total} тг\n"
        text += f"🎁 *Скидка за подписку:* -{discount_amount} тг\n"
        text += f"💳 *Итого со скидкой:* {discounted_total} тг\n"
    else:
        text += f"💵 *Общая сумма:* {total} тг\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    text += "✅ Готовы оформить заказ?"

    sent = bot.send_message(uid, text, parse_mode='Markdown', reply_markup=confirm_keyboard())
    cart_message_ids[uid].append(sent.message_id)

# 2) Меню редактирования (не трогаем просмотр)
@bot.callback_query_handler(lambda c: c.data == 'edit_cart')
def edit_cart(call):
    uid = call.message.chat.id

    # Удаляем старое меню удаления
    if uid in edit_message_ids:
        try: bot.delete_message(uid, edit_message_ids[uid])
        except: pass

    cart = carts.get(uid, [])
    if not cart:
        sent = bot.send_message(uid, "🛒 Ваша корзина пуста.", reply_markup=back_to_menu_keyboard())
        edit_message_ids[uid] = sent.message_id
        return

    kb = types.InlineKeyboardMarkup()
    for idx, it in enumerate(cart):
        kb.add(types.InlineKeyboardButton(
            f"❌ Удалить {it['name']} ({it['quantity']} шт.)",
            callback_data=f'remove_{idx}'
        ))
    kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data='cart'))

    sent = bot.send_message(uid, "Выберите товар для удаления:", reply_markup=kb)
    edit_message_ids[uid] = sent.message_id

# 3) Удаление товара
@bot.callback_query_handler(lambda c: c.data.startswith('remove_'))
def remove_item(call):
    uid = call.message.chat.id
    idx = int(call.data.split('_')[1])
    cart = carts.get(uid, [])

    # Проверка
    if idx < 0 or idx >= len(cart):
        return bot.answer_callback_query(call.id, "❌ Товар не найден")

    # Удаляем товар и возвращаем на склад
    it = cart.pop(idx)
    stock = get_stock_from_db(it['product_id'])
    update_stock_in_db(it['product_id'], stock + it['quantity'])
    bot.answer_callback_query(call.id, "✅ Удалено")

    # Удаляем и просмотр, и меню удаления
    for mid in cart_message_ids.get(uid, []):
        try: bot.delete_message(uid, mid)
        except: pass
    cart_message_ids[uid] = []

    if uid in edit_message_ids:
        try: bot.delete_message(uid, edit_message_ids[uid])
        except: pass
        del edit_message_ids[uid]

    # Показываем обновлённую корзину и сразу меню редактирования
    show_cart(call)
  
@bot.callback_query_handler(func=lambda call: call.data == 'checkout')
def start_checkout(call):
    user_chat_id = call.message.chat.id
    
    if user_chat_id not in carts or not carts[user_chat_id]:
        bot.send_message(user_chat_id, "Ваша корзина пуста!")
        return
    # Удалим сообщение с корзиной
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except Exception as e:
        print("Не удалось удалить сообщение с корзиной:", e)

    
    msg=bot.send_message(user_chat_id, "Введите ваше ФИО:")
    bot.register_next_step_handler(msg, process_name,msg.message_id)

def process_name(message,question_msg_id):
    user_chat_id = message.chat.id
    try:
        bot.delete_message(user_chat_id, question_msg_id)  # удалить "Введите ФИО"
        bot.delete_message(user_chat_id, message.message_id)  # удалить введённый текст
    except:
        pass

    user_states[user_chat_id] = {'name': message.text}
    
    
    
    msg=bot.send_message(user_chat_id, "Введите ваш адрес доставки:")
    bot.register_next_step_handler(message, process_address, msg.message_id)

def process_address(message, question_msg_id):
    user_chat_id = message.chat.id
    try:
        bot.delete_message(user_chat_id, question_msg_id)  # удалить "Введите адрес"
        bot.delete_message(user_chat_id, message.message_id)  # удалить ответ
    except:
        pass
    
    user_states[user_chat_id]['address'] = message.text
    
    msg=bot.send_message(user_chat_id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, process_phone, msg.message_id)


def process_phone(message, question_msg_id):
    user_chat_id = message.chat.id

    try:
        bot.delete_message(user_chat_id, question_msg_id)
        bot.delete_message(user_chat_id, message.message_id)
    except:
        pass

    try:
        phone = message.text
        if not phone.isdigit() or not (7 <= len(phone) <= 15):
            msg = bot.send_message(user_chat_id, "❌ Пожалуйста, введите корректный номер телефона (только цифры).")
            bot.register_next_step_handler(msg, process_phone, msg.message_id)
            return
        user_states[user_chat_id]['phone'] = phone

        name = user_states[user_chat_id]['name']
        address = user_states[user_chat_id]['address']

        cart_items = carts[user_chat_id]
        total = sum(item['price'] * item['quantity'] / 1000 for item in cart_items)

        order_id = save_order(name, address, phone, cart_items, total)

        order_items = []
        for item in cart_items:
            item_total = item['price'] * item['quantity'] / 1000
            order_items.append(
                f"{item['name']} - {item['quantity']} шт. = {item_total:.3f}тг"
            )

        order_text = (
            f"🛒 Новый заказ #{order_id}\n"
            f"👤 Клиент: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🏠 Адрес: {address}\n\n"
            f"📦 Состав заказа:\n" + "\n".join(order_items) + "\n\n"
            f"💵 Итого: {total:.3f}тг"
        )

        bot.send_message(GROUP_CHAT_ID, order_text)

        bot.send_message(
            user_chat_id,
            f"✅ Ваш заказ #{order_id} оформлен!\n"
            f"Мы свяжемся с вами по номеру {phone} для подтверждения.\n\n"
            "Для нового заказа нажмите /start",
            reply_markup=types.ReplyKeyboardRemove()
        )

        del carts[user_chat_id]
        del user_states[user_chat_id]

    except Exception as e:
        bot.send_message(user_chat_id, f"Произошла ошибка: {e}\nПожалуйста, попробуйте ещё раз.")


# Возврат в главное меню
@bot.callback_query_handler(lambda c: c.data == 'main_menu')
def back_to_main(call):
    uid = call.message.chat.id

    # Удаляем текущее сообщение (кнопки «главного меню» или корзины)
    try:
        bot.delete_message(uid, call.message.message_id)
    except:
        pass

    # Удаляем сообщение с каталогом, если оно было сохранено
    if uid in catalog_messages_ids:
        try:
            bot.delete_message(uid, catalog_messages_ids[uid])
        except:
            pass
        del catalog_messages_ids[uid]

    # Отправляем главное меню заново
    bot.send_message(
        uid,
        "🏠 Главное меню:",
        reply_markup=main_menu_keyboard()
    )

#Продолжение покупок
@bot.callback_query_handler(func=lambda call: call.data == 'continue_shopping')
def continue_shopping(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Удаляем кнопку
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

    # Отправляем сообщение
    sent_msg = bot.send_message(chat_id, "🛍 Продолжайте выбирать товары!")

    # Удаляем его через 3 секунды в отдельном потоке
    def delete_later(chat_id, msg_id):
        time.sleep(3)
        try:
            bot.delete_message(chat_id, msg_id)
        except:
            pass

    threading.Thread(target=delete_later, args=(chat_id, sent_msg.message_id)).start()

# ==================== Запуск бота ====================
if __name__ == '__main__':
    if not DB_PATH.exists():
        print(f"⚠️ База не найдена: {DB_PATH}")
    else:
        bot.infinity_polling()
