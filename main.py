import telebot
from telebot import types
import sqlite3
import os
import time
import threading




# Настройки
current_directory = os.path.dirname(os.path.abspath(__file__))
project_directory = os.path.join(current_directory, "albaraka")
db_path = os.path.join(project_directory, "orders.db")
GROUP_CHAT_ID = -4971242631
bot = telebot.TeleBot('7818783609:AAEWOI3xPYr9ajSDLCF6nK9Kn-SSP6Xd2mc')

ADMIN_ID = 779172775  # Замените на ваш ID



# База данных для статуса
def init_status_db():
    conn = sqlite3.connect('bot_status.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS status
                     (maintenance BOOLEAN)''')
    conn.commit()
    conn.close()

def get_status():
    conn = sqlite3.connect('bot_status.db')
    cursor = conn.cursor()
    cursor.execute("SELECT maintenance FROM status LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

def set_status(status):
    conn = sqlite3.connect('bot_status.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM status")
    cursor.execute("INSERT INTO status (maintenance) VALUES (?)", (status,))
    conn.commit()
    conn.close()
def init_stock_table():
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_stock (
            product_id TEXT PRIMARY KEY,
            stock INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def init_orders_db():
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_numbers (
            order_number INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_stock (
            product_id TEXT PRIMARY KEY,
            stock INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def get_stock(product_id):
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM product_stock WHERE product_id = ?', (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def set_stock(product_id, new_stock):
    conn = sqlite3.connect('db/orders.db, check_same_thread=False')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO product_stock (product_id, stock)
        VALUES (?, ?)
        ON CONFLICT(product_id) DO UPDATE SET stock=excluded.stock
    ''', (product_id, new_stock))
    conn.commit()
    conn.close()

def decrease_stock(product_id, amount):
    current = get_stock(product_id)
    set_stock(product_id, max(current - amount, 0))


def get_stock_from_db(product_id):
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT stock FROM product_stock WHERE product_id = ?', (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_stock_in_db(product_id, stock):
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO product_stock (product_id, stock) VALUES (?, ?)', (product_id, stock))
    conn.commit()
    conn.close()


def show_stock_status():
    result_lines = []
    for product_id, product in products_clean.items():
        name = product['name']
        initial_stock = product.get('stock', 0)
        current_stock = get_stock(product_id)
        sold = initial_stock - current_stock

        result_lines.append(
            f"📦 {name}\n— Изначально: {initial_stock} шт.\n— Осталось: {current_stock} шт.\n— Продано: {sold} шт.\n"
        )

    return "\n".join(result_lines)


    
# Инициализация
init_status_db()
init_orders_db()
BOT_MAINTENANCE = get_status()

def load_stock_from_db(products_clean):
    for product_id, product in products_clean.items():
        db_stock = get_stock_from_db(product_id)
        if db_stock is not None:
            product['stock'] = db_stock









# Данные о товарах (замените photo_base64 на реальные данные)
products_clean = {
    '1': {
        'name': 'ACWELL',
        'short_description':'1',
         'photo':os.path.join("images", "1. ACWELL.JPG"),
        'price': 8900,
        'stock': 10,
        'description': 'Идеален для обладателей чувствительной, обезвоженной, уставшей кожи, кому нужен нежный уход и увлажнение. Подойдёт как ежедневный увлажняющий мист в сухих помещениях или после очищения.'
    },
    '2': {
        'name': 'ACWELL eye cream ',
        'short_description':'2',
        'photo':os.path.join("images", "2. ACWELL eye cream.JPG"),
        'price': 10400,
        'stock': 10,
        'description': 'В подборке лучших корейских кремов для глаз от Glamour ACWELL Licorice pH Balancing Intensive Eye Cream назван одним из лучших для борьбы с тёмными кругами благодаря комбинации солодки, пептидов, кофеина и антиоксидантов.'
    },
    '3': {
        'name': 'GALACTO PORE toner',
        'short_description':'3',
        'photo': os.path.join("images", "3. GALACTO PORE toner.JPG"),
        'stock': 10,
        'price': 7990,
        'description': 'Это корейский тоник, предназначенный для сужения пор, увлажнения и улучшения текстуры кожи. Он сочетает в себе ферментированные компоненты, кислородные пузырьки и растительные экстракты, что делает его подходящим для жирной, комбинированной и склонной к акне кожи.'
    },
    '4': {
        'name': 'GALACTO PORE SERUM',
        'short_description':'4',
        'photo': os.path.join("images", "4. GALACTO PORE SERUM.JPG"),
        'price': 9990,
        'stock': 10,
        'description': "Предназначенная для сужения пор, улучшения текстуры кожи и увлажнения. Она является частью популярной линии Galacto Pore от бренда SAM'U, известного своими средствами с ферментированными компонентами."
    },
    '5': {
        'name': 'IN THE ZONE',
        'short_description':'5',
        'photo': os.path.join("images", "5. IN THE ZONE.JPG"),
        'price': 0,
        'stock': 10,
        'description': 'Маска увлажняющая.'
    },
    '6': {
        'name': 'PH SENSITIVE AMPOULE',
        'short_description':'6',
        'photo': os.path.join("images", "6. PH SENSITIVE AMPOULE(сыворотка).JPG"),
        'price': 13200,
        'stock': 10,
        'description': 'Сыворотке-ампуле для чувствительной и сухой кожи: Идеальна для чувствительной, сухой и комбинированной кожи; Придаёт увлажнение и комфорт без липкости; Прекрасно работает как сыворотка после тонера.'
    },
    '7': {
        'name': 'PH SENSITIVE CREAM',
        'short_description':'7',
        'photo': os.path.join("images", "7. PH SENSITIVE CREAM.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'Это качественный корейский уходовый крем в тюбике, сохраняющий влагу, балансирует pH и подходит для разных типов кожи. Рекомендован, если ищешь нежную текстуру и барьерную защиту.'
    },
    '8': {
        'name': 'PH SENSITIVE CREAM MIST',
        'short_description':'8',
        'photo': os.path.join("images", "8. PH SENSITIVE CREAM MIST.JPG"),
        'price': 10590,
        'stock': 10,
        'description': 'Легчайший крем в формате миста. Удобен для применения в любое время дня:\n• используется как основа под макияж,\n• как фиксатор макияжа,\n• как средство для освежения и увлажнения в течение дня.'
    },
    '9': {
        'name': 'PH SENSITIVE FACIAL TREATMENT',
        'short_description':'9',
        'photo': os.path.join("images", "9. PH SENSITIVE FACIAL TREATMENT.JPG"),
        'price': 13590,
        'stock': 10,
        'description': 'Ты ищешь заключительный этап ухода — ампула-лосьон, укрепляющая барьер и удерживающая влагу. Твоя кожа сухая, чувствительная или комбинированная, и нужна лёгкая, но эффективная формула. Ты хочешь удобное базовое средство под макияж с pH балансом.'
    },
    '10': {
        'name': 'SENSITIVE POCKET SUN STICK',
        'short_description':'10',
        'photo': os.path.join("images", "10. SENSITIVE POCKET SUN STICK.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'СПФ компактная Удобен для мгновенного нанесения и повторного применения в течение дня, без рук . Текстура не оставляет блеска и не белит, ощущается лёгкая и бархатная.'
    },
    '11': {
        'name': 'PH SENSITIVE SPOT CREAM',
        'short_description':'11',
        'photo': os.path.join("images", "11. PH SENSITIVE SPOT CREAM.JPG"),
        'price': 7990,
        'stock': 10,
        'description': 'Это локальное средство, которое:\n• Наносится точечно на участки покраснений, раздражений, шелушений;\n• Помогает успокоить кожу, особенно если есть высыпания, раздражение, зуд, сухость;\n• Подходит для чувствительной, реактивной, склонной к дерматиту кожи.'
    },
    '12': {
        'name': 'PH SENSITIVE SUNCREAM',
        'short_description':'12',
        'photo': os.path.join("images", "12. PH SENSITIVE SUNCREAM.JPG"),
        'price': 8990,
        'stock': 10,
        'description': 'Защита SPF 50+ PA++++ без белого следа; Увлажняющий и барьер защитный эффект — особенно для сухой, комбинированной и чувствительной кожи; Лёгкая текстура, уход под макияж, без липкости.'
    },
    '13': {
        'name': 'PH SENSITIVE TONER PAD',
        'short_description':'13',
        'photo': os.path.join("images", "13. PH SENSITIVE TONER PAD.JPG"),
        'price': 10005,
        'stock': 10,
        'description': 'Это мягкие, комфортные тонер-пады с акцентом на увлажнение, pH-баланс и бережное очищение. Отличный выбор в качестве освежающего ухода и экспресс-маски, особенно для чувствительной кожи.'
    },
    '14': {
        'name': 'Born Panthenol(JELLY WASH)',
        'short_description':'14',
        'photo': os.path.join("images", "14. Born Panthenol(JELLY WASH).JPG"),
        'price': 7800,
        'stock': 10,
        'description': 'Это корейское очищающее средство с текстурой желе, предназначенное для увлажнения и успокоения кожи. Подходит для:\n• Сухой и чувствительной кожи, нуждающейся в увлажнении и успокоении./n• Тех, кто ищет мягкое очищающее средство без агрессивных компонентов'
    },
    '15': {
        'name': 'BRIGHT SIDE UP',
        'short_description':'15',
        'photo': os.path.join("images", "15. BRIGHT SIDE UP.JPG"),
        'price': 0,
        'stock': 10,
        'description': "🍊 Bright Side Up (серум с витамином C)\n📌 Для чего: Осветляет пигментацию, придаёт коже сияние, защищает от свободных радикалов.\n👤 Кому подойдёт: Для тусклой, усталой, неровной кожи.\n🧪 Активы: Витамин C, ниацинамид, экстракт грейпфрута.\n\n💧 Say You Dew (увлажняющий крем)\n📌 Для чего: Увлажняет и смягчает кожу, улучшает барьер.\n👤 Кому подойдёт: Сухой, комбинированной коже.\n🧪 Формула: Гелевая, освежающая, с витаминами C и E, лимонным экстрактом.\n\n💄 Plush Party (ночная маска для губ)\n📌 Для чего: Питает, восстанавливает губы во время сна.\n🧪 Активы: Масло какао, витамин E, пептиды."
    },
    '16': {
        'name': 'THIRST THINGS FIRST',
        'short_description':'16',
        'photo': os.path.join("images", "16. THIRST THINGS FIRST.JPG"),
        'price': 0,
        'stock': 10,
        'description': 'Обеспечивают сияние, увлажнение и защиту кожи . Подходит для: сухой, обезвоженной, тусклой кожи; фиксации макияжа; свежести в течение дня; ночной маски-спрея .'
    },
    '17': {
        'name': "SAM'U",
        'short_description':'17',
        'photo': os.path.join("images", "17. SAMU.JPG"),
        'price': 12900,
        'stock': 10,
        'description': 'Это несмываемая ампульная сыворотка для волос, предназначенная для интенсивного увлажнения и восстановления структуры волос'
    }
}
    
init_stock_table()
for product_id, product in products_clean.items():
    update_stock_in_db(product_id, product.get('stock', 0))
load_stock_from_db(products_clean)

# Форматирование цен
for product in products_clean.values():
    product['formatted_price'] = '{:.3f}'.format(product['price'] / 1000) 

# Глобальные переменные
carts = {}
user_states = {}
last_product_messages = {}
cart_photo_messages = {}
cart_message_ids = {}
catalog_messages_ids= {}
last_quantity_prompt = {}

# База данных
def init_db():
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS order_numbers (order_number INTEGER)')
    conn.commit()
    conn.close()

init_db()

def get_order_number():
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT order_number FROM order_numbers')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_order_number(new_number):
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    if get_order_number() == 0:
        cursor.execute('INSERT INTO order_numbers (order_number) VALUES (?)', (new_number,))
    else:
        cursor.execute('UPDATE order_numbers SET order_number = ?', (new_number,))
    conn.commit()
    conn.close()

# Очистка базы данных
def clear_order_number():
    conn = sqlite3.connect('db/orders.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM order_numbers')  # удаляем всё
    conn.commit()
    conn.close()




# Клавиатуры
def main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton('Уходовая косметика 🧴', callback_data='clean'))
    keyboard.add(types.InlineKeyboardButton('Декоративная косметика 💄',callback_data='makeup'))
    keyboard.add(types.InlineKeyboardButton('Корзина 🛒', callback_data='cart'))
    return keyboard

def post_add_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data='main_menu'),
        types.InlineKeyboardButton("🛍 Продолжить покупки", callback_data='continue_shopping')
    )
    return keyboard

def confirm_keyboard(product_id=None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if product_id:
        keyboard.add(
            types.InlineKeyboardButton('✅ Да, добавить', callback_data=f'add_{product_id}'),
            types.InlineKeyboardButton('❌ Нет, спасибо', callback_data='deleting')
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton('✅ Оформить заказ', callback_data='checkout'),
            types.InlineKeyboardButton('✏️ Изменить корзину', callback_data='edit_cart'),
            types.InlineKeyboardButton('❌ Выйти из корзины', callback_data='main_menu')
        )
    return keyboard 


def get_back_to_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data='main_menu'))
    return keyboard




# 1. Обработчик техобслуживания (ПЕРВЫЙ!)
@bot.message_handler(func=lambda m: BOT_MAINTENANCE and not m.text.startswith('/maintenance'))
def maintenance_handler(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Проверить статус", callback_data="check_status"))
    bot.send_message(
        message.chat.id,
        "🔧 Бот на техническом обслуживании\nПопробуйте позже.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: BOT_MAINTENANCE)
def handle_maintenance_callback(call):
    bot.answer_callback_query(call.id, "🔧 Бот на техническом обслуживании", show_alert=True)


# 2. Команда управления режимом
@bot.message_handler(commands=['maintenance'])
def toggle_maintenance(message):
    global BOT_MAINTENANCE
    if message.from_user.id == ADMIN_ID:
        BOT_MAINTENANCE = not BOT_MAINTENANCE
        set_status(BOT_MAINTENANCE)  # Сохраняем в БД
        
        status = "🛑 АКТИВИРОВАН" if BOT_MAINTENANCE else "✅ ОТКЛЮЧЕН"
        bot.reply_to(message, f"Режим обслуживания {status}")
        
        if not BOT_MAINTENANCE:
            bot.send_message(
                message.chat.id,
                "✅ Бот снова доступен для всех пользователей!",
                reply_markup=types.ReplyKeyboardRemove()
            )
    else:
        bot.reply_to(message, "⛔ Недостаточно прав!")

    
# 3. Обработчик кнопки проверки статуса
@bot.callback_query_handler(func=lambda call: call.data == "check_status")
def check_status(call):
    if BOT_MAINTENANCE:
        bot.answer_callback_query(call.id, "🔧 Бот всё ещё на обслуживании")
    else:
        bot.answer_callback_query(call.id, "✅ Бот снова доступен!", show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass



# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    text = (
    "Здравствуйте 👋, дорогой покупатель!\n\n"
    "*Добро пожаловать в GLOW&CO COSMETICS* — магазин корейской косметики премиум-качества 💄\n\n"
    "Данный бот поможет вам легко и быстро оформить заказ.\n\n"
    "🏠 Это ваше главное меню. Выберите нужный раздел ниже, чтобы начать покупки!"
)
    bot.send_message(
        message.chat.id,text,parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
# Главная админ-панель
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for product_id, product in products_clean.items():
        button = types.InlineKeyboardButton(
            text=f"{product['short_description']} | {product['stock']} шт.",
            callback_data=f"admin_edit_{product_id}"
        )
        keyboard.add(button)
    bot.send_message(message.chat.id, "📦 Выберите товар для редактирования:", reply_markup=keyboard)

# Редактирование товара
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_edit_'))
def edit_product(call):
    product_id = call.data.split('_')[-1]
    product = products_clean[product_id]
    stock = get_stock(product_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("➕ Увеличить на 1", callback_data=f"stock_inc1_{product_id}"),
        types.InlineKeyboardButton("➖ Уменьшить на 1", callback_data=f"stock_dec1_{product_id}")
    )
    keyboard.add(
        types.InlineKeyboardButton("✏️ Ввести вручную", callback_data=f"stock_manual_{product_id}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🛍 {product['name']}\nВ наличии: {stock} шт.",
        reply_markup=keyboard
    )

# Обработка увеличения/уменьшения
@bot.callback_query_handler(func=lambda call: call.data.startswith(('stock_inc1_', 'stock_dec1_')))
def update_stock_simple(call):
    product_id = call.data.split('_')[-1]
    change = 1 if 'inc1' in call.data else -1
    current = get_stock(product_id)
    new_stock = max(current + change, 0)
    set_stock(product_id, new_stock)
    products_clean[product_id]['stock'] = new_stock
    edit_product(call)

# Ввод вручную
@bot.callback_query_handler(func=lambda call: call.data.startswith('stock_manual_'))
def ask_manual_stock(call):
    product_id = call.data.split('_')[-1]
    msg = bot.send_message(call.message.chat.id, "Введите новое количество:")
    bot.register_next_step_handler(msg, set_manual_stock, product_id)


def set_manual_stock(message, product_id):
    try:
        stock = int(message.text.strip())
        if stock < 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ Введите корректное число")
        return
    set_stock(product_id, stock)
    products_clean[product_id]['stock'] = stock
    bot.send_message(message.chat.id, f"✅ Количество обновлено: {stock} шт.")
    admin_panel(message)

# Назад
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_admin')
def back_to_admin_panel(call):
    admin_panel(call.message)

@bot.message_handler(commands=['reset_orders'])
def reset_orders(message):
    if message.chat.id == ADMIN_ID:
        clear_order_number()
        bot.send_message(message.chat.id, "✅ Номер заказа успешно сброшен.")
    else:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде.")

# Обработчики callback
@bot.callback_query_handler(func=lambda call: call.data == 'deleting')
def cancel_add_to_cart(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass  # если сообщение уже удалено — не ошибка


@bot.message_handler(commands=['stock'])
def handle_stock_status(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде.")
        return

    status = show_stock_status()
    bot.send_message(message.chat.id, status)


@bot.callback_query_handler(func=lambda call: call.data.startswith('clean'))
def show_catalog(call):
    user_chat_id = call.message.chat.id
    # Удаляем главное меню
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except Exception as e:
        print(f"Не удалось удалить главное меню: {e}")

    markup = types.InlineKeyboardMarkup(row_width=1)
    for product_id, product in products_clean.items():
        short = product.get('short_description', 'Нет описания')
        button = types.InlineKeyboardButton(
            text=f"{product['name']} — {short}",
            callback_data=f"product_{product_id}"
        )
        markup.add(button)
    msg = bot.send_message(call.message.chat.id, "✨ Наш каталог готов для вас! Выберите товар ниже:", reply_markup=markup)
    catalog_messages_ids[user_chat_id] = msg.message_id


@bot.callback_query_handler(func=lambda call: call.data.startswith('makeup'))
def show_all_makeup_products(call):
    bot.answer_callback_query(call.id)  # чтобы убрать "крутилку" загрузки
    sent = bot.send_message(
        call.message.chat.id,
        "💄 Раздел *Декоративная косметика* скоро будет доступен!\n\n🔔 Следите за обновлениями!",
        parse_mode='Markdown'
    )
    time.sleep(5)
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=sent.message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def show_product_card(call):
    product_id = call.data.split("_")[1]
    product = products_clean.get(product_id)
    if not product:
        bot.answer_callback_query(call.id, "Товар не найден.")
        return
    
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # Удаляем предыдущую карточку, если была
    if user_id in last_product_messages:
        try:
            bot.delete_message(chat_id, last_product_messages[user_id])
        except Exception as e:
            print(f"Не удалось удалить старое сообщение: {e}")

    # Подготовка данных
    photo = product['photo']
    name = product['name']
    description = product['description']
    price = product['formatted_price']
    stock = get_stock(product_id)

    text = (
        f"📦 <b>{name}</b>\n\n"
        f"{description}\n\n"
        f"💰 Цена: {price}₸\n"
        f"🔢 В наличии: {stock} шт.\n\n"
        f"Добавить этот товар в корзину?"
    )


    # Отправляем
    with open(photo, 'rb') as photo_file:
        sent_msg = bot.send_photo(
            call.message.chat.id,
            photo_file,
            caption=text,
            parse_mode="HTML",
            reply_markup=confirm_keyboard(product_id)
  
        )

     # Сохраняем ID отправленного сообщения
    last_product_messages[user_id] = sent_msg.message_id
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def return_to_menu(call):
    user_chat_id = call.message.chat.id
    # Удаляем текущее сообщение с кнопками
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except Exception as e:
        print(f"Ошибка удаления текущего сообщения: {e}")

    # Удаляем все карточки каталога
    if user_chat_id in catalog_messages_ids:
        try:
            bot.delete_message(user_chat_id, catalog_messages_ids[user_chat_id])
            del catalog_messages_ids[user_chat_id]
        except Exception as e:
            print(f"Ошибка удаления каталога: {e}")

    # Отправляем главное меню
    bot.send_message(
        user_chat_id,
        "🏠 Главное меню:",
        reply_markup=main_menu_keyboard()
    )


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


   

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart(call):
    chat_id = call.message.chat.id
    product_id = call.data.split('_')[1]
    user_chat_id = call.message.chat.id

    # Получаем товар
    product = products_clean.get(product_id)
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден.")
        return

    current_stock = get_stock(product_id)
    if current_stock <= 0:
        # Удаляем сообщение с кнопками
        try:
            bot.delete_message(user_chat_id, call.message.message_id)
        except:
            pass
        
        # Показываем "нет в наличии"
        sent_msg = bot.send_message(chat_id, "❌ Товара больше нет в наличии.")

        # Удаляем через 3 секунды
        def delete_later(chat_id, msg_id):
            time.sleep(3)
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass

        threading.Thread(target=delete_later, args=(chat_id, sent_msg.message_id)).start()
        
        return  # ⚠️ Важно: тут выходим из функции, чтобы дальше ничего не выполнялось!

    # Если товар есть в наличии — продолжаем
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except:
        pass

    msg = bot.send_message(user_chat_id, "Сколько штук вы хотите заказать? Введите число:")
    last_quantity_prompt[user_chat_id] = msg.message_id
    bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)


def process_quantity(message, product_id, msg_id):
    try:
        user_chat_id = message.chat.id
        quantity = int(message.text)
        
        if quantity <= 0:
            raise ValueError
        
        product = products_clean[product_id]
        current_stock = get_stock(product_id)  # Получаем текущий остаток
        
        # Проверка наличия
        if current_stock < quantity:
            # Удаляем предыдущее сообщение, если есть
            if user_chat_id in last_quantity_prompt:
                try:
                    bot.delete_message(user_chat_id, message.message_id)
                except:
                    pass
                # Удаляем предыдущее сообщение "Введите количество", если есть
                if user_chat_id in last_quantity_prompt:
                    try:
                        bot.delete_message(user_chat_id, last_quantity_prompt[user_chat_id])
                    except:
                        pass
                    last_quantity_prompt.pop(user_chat_id, None)

            msg = bot.send_message(
                user_chat_id,
                f"❌ На складе только {current_stock} шт. товара. Введите меньшее количество:"
            )
            last_quantity_prompt[user_chat_id] = msg.message_id
            bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)
            return
        
        # Удаляем сообщения
        try:
            bot.delete_message(user_chat_id, msg_id)
            bot.delete_message(user_chat_id, message.message_id)
        except:
            pass
        
        # Добавляем в корзину
        if user_chat_id not in carts:
            carts[user_chat_id] = []
        
        # Проверяем, есть ли уже такой товар в корзине
        item_exists = False
        for item in carts[user_chat_id]:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                item_exists = True
                break
        
        if not item_exists:
            carts[user_chat_id].append({
                'photo': product['photo'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'product_id': product_id
            })
        # ⬇️ Уменьшаем остаток
        decrease_stock(product_id, quantity)
        
        bot.send_message(
            user_chat_id,
            f"✅ Добавлено {quantity} шт. {product['name']} в корзину!",
            reply_markup=post_add_keyboard()
        )
        
    except ValueError:
        user_chat_id = message.chat.id
        try:
            bot.delete_message(user_chat_id, message.message_id)
        except:
            pass
         
         # Удаляем предыдущее сообщение, если есть
        if user_chat_id in last_quantity_prompt:
            try:
                bot.delete_message(user_chat_id, last_quantity_prompt[message.chat.id])
            except:
                pass
            last_quantity_prompt.pop(user_chat_id, None)
        
        msg = bot.send_message(message.chat.id, "⚠️ Пожалуйста, введите корректное число больше нуля!")
        last_quantity_prompt[message.chat.id] = msg.message_id
        bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'cart')
def show_cart(call):
    user_chat_id = call.message.chat.id

    # Удаляем главное меню
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except Exception as e:
        print(f"Не удалось удалить главное меню: {e}")

    if user_chat_id not in carts or not carts[user_chat_id]:
        bot.send_message(
            user_chat_id,
            "🛒 Ваша корзина пуста.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return

    # Удаляем старые сообщения, если нужно
    if user_chat_id in cart_message_ids:
        for msg_id in cart_message_ids[user_chat_id]:
            try:
                bot.delete_message(user_chat_id, msg_id)
            except:
                pass
        cart_message_ids[user_chat_id].clear()
    else:
        cart_message_ids[user_chat_id] = []

    # Формируем сообщение
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    for item in carts[user_chat_id]:
        item_total = item['price'] * item['quantity'] / 1000
        total += item_total
        text += (
            f"📦 *{item['name']}*\n"
            f"🔢 Количество: {item['quantity']} шт.\n"
            f"💰 Цена: {item_total:.3f} тг\n\n"
        )
    text += f"💳 *Итого: {total:.3f} тг*"

    # Кнопки
    markup = confirm_keyboard()  # 'Оформить', 'Редактировать', 'Назад в меню'

    sent = bot.send_message(
        user_chat_id,
        text,
        parse_mode='Markdown',
        reply_markup=markup
    )
    cart_message_ids[user_chat_id].append(sent.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'checkout')
def start_checkout(call):
    user_chat_id = call.message.chat.id
    
    if user_chat_id not in carts or not carts[user_chat_id]:
        bot.send_message(user_chat_id, "Ваша корзина пуста!")
        return
    
    bot.send_message(user_chat_id, "Введите ваше ФИО:")
    bot.register_next_step_handler(call.message, process_name)

def process_name(message):
    user_chat_id = message.chat.id
    user_states[user_chat_id] = {'name': message.text}
    
    
    
    bot.send_message(user_chat_id, "Введите ваш адрес доставки:")
    bot.register_next_step_handler(message, process_address)

def process_address(message):
    user_chat_id = message.chat.id
    user_states[user_chat_id]['address'] = message.text
    
    bot.send_message(user_chat_id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, process_phone)


def process_phone(message):
    try:
        user_chat_id = message.chat.id
        phone = message.text
        user_states[user_chat_id]['phone'] = phone
        
        # Генерируем номер заказа
        order_number = get_order_number() + 1
        update_order_number(order_number)
        
        # Формируем сообщение для администратора
        order_items = []
        total = 0
        for item in carts[user_chat_id]:
            item_total = item['price'] * item['quantity'] / 1000
            total += item_total
            order_items.append(
                f"{item['name']} - {item['quantity']} шт. = {item_total:.3f}тг"
            )
            
        
        order_text = (
            f"🛒 Новый заказ #{order_number}\n"
            f"👤 Клиент: {user_states[user_chat_id]['name']}\n"
            f"📞 Телефон: {phone}\n"
            f"🏠 Адрес: {user_states[user_chat_id]['address']}\n\n"
            f"📦 Состав заказа:\n" + "\n".join(order_items) + "\n\n"
            f"💵 Итого: {total:.3f}тг"
        )
        
        # Отправляем администратору
        bot.send_message(GROUP_CHAT_ID, order_text)
        
        # Отправляем клиенту
        bot.send_message(
            user_chat_id,
            f"✅ Ваш заказ #{order_number} оформлен!\n"
            f"Мы свяжемся с вами по номеру {phone} для подтверждения.\n\n"
            "Для нового заказа нажмите /start",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        # Очищаем корзину и состояние
        if user_chat_id in carts:
            del carts[user_chat_id]
        if user_chat_id in user_states:
            del user_states[user_chat_id]
            
    except Exception as e:
        bot.send_message(user_chat_id, f"Произошла ошибка: {e}\nПожалуйста, попробуйте ещё раз.")

@bot.callback_query_handler(func=lambda call: call.data == 'edit_cart')
def edit_cart(call):
    user_chat_id = call.message.chat.id
    
    if user_chat_id not in carts or not carts[user_chat_id]:
        bot.send_message(user_chat_id, "Ваша корзина пуста!")
        return
    
    keyboard = types.InlineKeyboardMarkup()
    for index, item in enumerate(carts[user_chat_id]):
        keyboard.add(types.InlineKeyboardButton(
            f"❌ Удалить {item['name']} ({item['quantity']} шт.)",
            callback_data=f'remove_{index}'
        ))
    
    keyboard.add(types.InlineKeyboardButton("↩️ Назад", callback_data='cart'))
    
    bot.send_message(
        user_chat_id,
        "Выберите товар для удаления:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_'))
def remove_item(call):
    user_chat_id = call.message.chat.id
    index = int(call.data.split('_')[1])
    
    if user_chat_id in carts and 0 <= index < len(carts[user_chat_id]):
        removed_item = carts[user_chat_id].pop(index)
        
        # Удаляем сообщение с кнопками удаления
        try:
            bot.delete_message(user_chat_id, call.message.message_id)
        except:
            pass
        
        # Возвращаем товар на склад
        product_id = removed_item['product_id']
        current_stock = get_stock(product_id)
        update_stock_in_db(product_id, current_stock + removed_item['quantity'])
        
        # Если корзина пуста
        if len(carts[user_chat_id]) == 0:
            del carts[user_chat_id]  # Удаляем пустую корзину

             # Удаляем ещё одно сообщение (предыдущее), если оно осталось
            try:
                bot.delete_message(user_chat_id, call.message.message_id - 1)
            except:
                pass

            bot.send_message(
                user_chat_id,
                "🛒 Ваша корзина теперь пуста.",
                reply_markup=get_back_to_menu_keyboard()
            )
        else:
            # Показываем обновленную корзину
            show_cart(call)
    else:
        bot.answer_callback_query(call.id, "❌ Товар не найден в корзине.")

@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def back_to_main(call):
    user_chat_id = call.message.chat.id

     # Удаляем все сообщения корзины
    if user_chat_id in cart_message_ids:
        for msg_id in cart_message_ids[user_chat_id]:
            try:
                bot.delete_message(user_chat_id, msg_id)
            except:
                pass
        del cart_message_ids[user_chat_id]

    start(call.message)



if __name__ == "__main__":
    print(f"Бот запущен. Режим обслуживания: {'ВКЛ' if BOT_MAINTENANCE else 'ВЫКЛ'}")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}. Перезапуск через 10 сек...")
            time.sleep(10)
