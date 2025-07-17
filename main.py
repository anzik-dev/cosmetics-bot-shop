import telebot
from telebot import types
import sqlite3
import os
import time





# Настройки
current_directory = os.path.dirname(os.path.abspath(__file__))
project_directory = os.path.join(current_directory, "albaraka")
db_path = os.path.join(project_directory, "orders.db")
GROUP_CHAT_ID = -4011977891
bot = telebot.TeleBot('6858159801:AAFDXPrzZbwDcxNezxfFc4EgichTus2JY00')

ADMIN_ID = 779172775  # Замените на ваш ID



# База данных для статуса
def init_db():
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

# Инициализация
init_db()
BOT_MAINTENANCE = get_status()

def load_stock_from_txt(products_clean, filename='stock.txt'):
    if not os.path.exists(filename):
        return
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) == 3:
                product_id = parts[0].strip()
                name = parts[1].strip()
                stock = int(parts[2].strip())
                if product_id in products_clean:
                    products_clean[product_id]['stock'] = stock

def save_stock_to_txt(products_clean, filename='stock.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for product_id, product in products_clean.items():
            name = product.get('name', '')
            stock = product.get('stock', 0)
            f.write(f"{product_id} | {name} | {stock}\n")





# Данные о товарах (замените photo_base64 на реальные данные)
products_clean = {
    '1': {
        'name': 'ACWELL',
         'photo':os.path.join("images", "1. ACWELL.JPG"),
        'price': 8900,
        'stock': 10,
        'description': 'Идеален для обладателей чувствительной, обезвоженной, уставшей кожи, кому нужен нежный уход и увлажнение. Подойдёт как ежедневный увлажняющий мист в сухих помещениях или после очищения.'
    },
    '2': {
        'name': 'ACWELL eye cream ',
        'photo':os.path.join("images", "2. ACWELL eye cream.JPG"),
        'price': 10400,
        'stock': 10,
        'description': 'В подборке лучших корейских кремов для глаз от Glamour ACWELL Licorice pH Balancing Intensive Eye Cream назван одним из лучших для борьбы с тёмными кругами благодаря комбинации солодки, пептидов, кофеина и антиоксидантов.'
    },
    '3': {
        'name': 'GALACTO PORE toner',
        'photo': os.path.join("images", "3. GALACTO PORE toner.JPG"),
        'stock': 10,
        'price': 7990,
        'description': 'Это корейский тоник, предназначенный для сужения пор, увлажнения и улучшения текстуры кожи. Он сочетает в себе ферментированные компоненты, кислородные пузырьки и растительные экстракты, что делает его подходящим для жирной, комбинированной и склонной к акне кожи.'
    },
    '4': {
        'name': 'GALACTO PORE SERUM',
        'photo': os.path.join("images", "4. GALACTO PORE SERUM.JPG"),
        'price': 9990,
        'stock': 10,
        'description': "Предназначенная для сужения пор, улучшения текстуры кожи и увлажнения. Она является частью популярной линии Galacto Pore от бренда SAM'U, известного своими средствами с ферментированными компонентами."
    },
    '10': {
        'name': 'IN THE ZONE',
        'photo': os.path.join("images", "10. IN THE ZONE.JPG"),
        'price': 0,
        'stock': 10,
        'description': 'Маска увлажняющая.'
    },
    '6': {
        'name': 'PH SENSITIVE AMPOULE',
        'photo': os.path.join("images", "6. PH SENSITIVE AMPOULE(сыворотка).JPG"),
        'price': 13200,
        'stock': 10,
        'description': 'Сыворотке-ампуле для чувствительной и сухой кожи: Идеальна для чувствительной, сухой и комбинированной кожи; Придаёт увлажнение и комфорт без липкости; Прекрасно работает как сыворотка после тонера.'
    },
    '7': {
        'name': 'PH SENSITIVE CREAM',
        'photo': os.path.join("images", "7. PH SENSITIVE CREAM.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'Это качественный корейский уходовый крем в тюбике, сохраняющий влагу, балансирует pH и подходит для разных типов кожи. Рекомендован, если ищешь нежную текстуру и барьерную защиту.'
    },
    '8': {
        'name': 'PH SENSITIVE CREAM MIST',
        'photo': os.path.join("images", "8. PH SENSITIVE CREAM MIST.JPG"),
        'price': 10590,
        'stock': 10,
        'description': 'Легчайший крем в формате миста. Удобен для применения в любое время дня:\n• используется как основа под макияж,\n• как фиксатор макияжа,\n• как средство для освежения и увлажнения в течение дня.'
    },
    '9': {
        'name': 'PH SENSITIVE FACIAL TREATMENT',
        'photo': os.path.join("images", "9. PH SENSITIVE FACIAL TREATMENT.JPG"),
        'price': 13590,
        'stock': 10,
        'description': 'Ты ищешь заключительный этап ухода — ампула-лосьон, укрепляющая барьер и удерживающая влагу. Твоя кожа сухая, чувствительная или комбинированная, и нужна лёгкая, но эффективная формула. Ты хочешь удобное базовое средство под макияж с pH балансом.'
    },
    '10': {
        'name': 'SENSITIVE POCKET SUN STICK',
        'photo': os.path.join("images", "10. SENSITIVE POCKET SUN STICK.JPG"),
        'price': 10500,
        'stock': 10,
        'description': 'СПФ компактная Удобен для мгновенного нанесения и повторного применения в течение дня, без рук . Текстура не оставляет блеска и не белит, ощущается лёгкая и бархатная.'
    },
    '11': {
        'name': 'PH SENSITIVE SPOT CREAM',
        'photo': os.path.join("images", "11. PH SENSITIVE SPOT CREAM.JPG"),
        'price': 7990,
        'stock': 10,
        'description': 'Это локальное средство, которое:\n• Наносится точечно на участки покраснений, раздражений, шелушений;\n• Помогает успокоить кожу, особенно если есть высыпания, раздражение, зуд, сухость;\n• Подходит для чувствительной, реактивной, склонной к дерматиту кожи.'
    },
    '12': {
        'name': 'PH SENSITIVE SUNCREAM',
        'photo': os.path.join("images", "12. PH SENSITIVE SUNCREAM.JPG"),
        'price': 8990,
        'stock': 10,
        'description': 'Защита SPF 50+ PA++++ без белого следа; Увлажняющий и барьер защитный эффект — особенно для сухой, комбинированной и чувствительной кожи; Лёгкая текстура, уход под макияж, без липкости.'
    },
    '13': {
        'name': 'PH SENSITIVE TONER PAD',
        'photo': os.path.join("images", "13. PH SENSITIVE TONER PAD.JPG"),
        'price': 10005,
        'stock': 10,
        'description': 'Это мягкие, комфортные тонер-пады с акцентом на увлажнение, pH-баланс и бережное очищение. Отличный выбор в качестве освежающего ухода и экспресс-маски, особенно для чувствительной кожи.'
    },
    '14': {
        'name': 'Born Panthenol(JELLY WASH)',
        'photo': os.path.join("images", "14. Born Panthenol(JELLY WASH).JPG"),
        'price': 7800,
        'stock': 10,
        'description': 'Это корейское очищающее средство с текстурой желе, предназначенное для увлажнения и успокоения кожи. Подходит для:\n• Сухой и чувствительной кожи, нуждающейся в увлажнении и успокоении./n• Тех, кто ищет мягкое очищающее средство без агрессивных компонентов'
    },
    '15': {
        'name': 'BRIGHT SIDE UP',
        'photo': os.path.join("images", "15. BRIGHT SIDE UP.JPG"),
        'price': 0,
        'stock': 10,
        'description': "🍊 Bright Side Up (серум с витамином C)\n📌 Для чего: Осветляет пигментацию, придаёт коже сияние, защищает от свободных радикалов.\n👤 Кому подойдёт: Для тусклой, усталой, неровной кожи.\n🧪 Активы: Витамин C, ниацинамид, экстракт грейпфрута.\n\n💧 Say You Dew (увлажняющий крем)\n📌 Для чего: Увлажняет и смягчает кожу, улучшает барьер.\n👤 Кому подойдёт: Сухой, комбинированной коже.\n🧪 Формула: Гелевая, освежающая, с витаминами C и E, лимонным экстрактом.\n\n💄 Plush Party (ночная маска для губ)\n📌 Для чего: Питает, восстанавливает губы во время сна.\n🧪 Активы: Масло какао, витамин E, пептиды."
    },
    '16': {
        'name': 'THIRST THINGS FIRST',
        'photo': os.path.join("images", "16. THIRST THINGS FIRST.JPG"),
        'price': 0,
        'stock': 10,
        'description': 'Обеспечивают сияние, увлажнение и защиту кожи . Подходит для: сухой, обезвоженной, тусклой кожи; фиксации макияжа; свежести в течение дня; ночной маски-спрея .'
    },
    '17': {
        'name': "SAM'U",
        'photo': os.path.join("images", "17. SAMU.JPG"),
        'price': 12900,
        'stock': 10,
        'description': 'Это несмываемая ампульная сыворотка для волос, предназначенная для интенсивного увлажнения и восстановления структуры волос'
    }
}
    
load_stock_from_txt(products_clean)


# Форматирование цен
for product in products_clean.values():
    product['formatted_price'] = '{:.3f}'.format(product['price'] / 1000) 

# Глобальные переменные
carts = {}
user_states = {}

# База данных
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS order_numbers (order_number INTEGER)')
    conn.commit()
    conn.close()

init_db()

def get_order_number():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT order_number FROM order_numbers')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_order_number(new_number):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    if get_order_number() == 0:
        cursor.execute('INSERT INTO order_numbers (order_number) VALUES (?)', (new_number,))
    else:
        cursor.execute('UPDATE order_numbers SET order_number = ?', (new_number,))
    conn.commit()
    conn.close()

# Очистка базы данных
def clear_order_number():
    conn = sqlite3.connect('orders.db')
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
def add_in_cart_keybord(product_id):
    keyboard =  keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Добавить в корзину? 🛒', callback_data=f'add_in_cart_{product_id}'))
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
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f'Здравствуйте 👋, {user.first_name} {user.last_name}!\n' 
        'Данный бот поможет вам оформить заказ у нашей компании по продаже корейской косметики\n'
        '🏠 Это ваше главное меню ',
        reply_markup=main_menu_keyboard()
    )


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


@bot.callback_query_handler(func=lambda call: call.data.startswith('clean'))
def show_all_clean_products(call):
    for product_id, product in products_clean.items():
        photo_path=product['photo']
        with open(photo_path, 'rb') as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                f"{product['name']}\n\n📝 {product['description']}\n\n📦 В наличии: {product['stock']}\n\n💸 Цена: {product['formatted_price']} тг",
                reply_markup=add_in_cart_keybord(product_id)
        )
        time.sleep(0.5) 

@bot.callback_query_handler(func=lambda call: call.data.startswith('makeup'))
def show_all_makeup_products(call):
    bot.answer_callback_query(call.id)  # чтобы убрать "крутилку" загрузки
    bot.send_message(
        call.message.chat.id,
        "💄 Раздел *Декоративная косметика* скоро будет доступен!\n\n🔔 Следите за обновлениями!",
        parse_mode='Markdown'
    )



@bot.callback_query_handler(func=lambda call: call.data.startswith('add_in_cart'))
def call_yes_no_buttons(call):
    product_id = call.data.split('_')[-1]
    product = products_clean[product_id]
    
    
    # 🔴 ПРОВЕРКА
    product = products_clean.get(product_id)

    if product.get('stock', 0) <= 0:
        bot.answer_callback_query(call.id, "❌ Товара больше нет в наличии.")
        return

 

    bot.send_message(
        call.message.chat.id,
        f"Вы уверены, что хотите добавить в корзину этот товар? *{product['name']}*",
        reply_markup=confirm_keyboard(product_id),
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def return_to_menu(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🏠 Главное меню:",  reply_markup=main_menu_keyboard())
    except Exception as e:
        print(f"Ошибка удаления: {e}")


@bot.callback_query_handler(func=lambda call: call.data == 'continue_shopping')
def continue_shopping(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    bot.answer_callback_query(call.id, "Продолжайте выбирать товары!")


   

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart(call):
    product_id = call.data.split('_')[1]
    user_chat_id = call.message.chat.id
    
    # Удаляем предыдущие кнопки
    try:
        bot.delete_message(user_chat_id, call.message.message_id)
    except:
        pass
    
    msg = bot.send_message(user_chat_id, "Сколько штук вы хотите заказать? Введите число:")
    bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)

def process_quantity(message, product_id, msg_id):
    try:
        user_chat_id = message.chat.id
        quantity = int(message.text)
        
        if quantity <= 0:
            raise ValueError
        
        product = products_clean[product_id]
        
       # Удаляем сообщение с запросом количества
        try:
            bot.delete_message(user_chat_id, msg_id)  
        except:
            pass

        # Удаляем сообщение с введённым числом
        try:
            bot.delete_message(user_chat_id, message.message_id)
        except:
            pass
        if quantity > product['stock']:
            msg = bot.send_message(
                user_chat_id,
                f"❌ На складе только {product['stock']} шт. товара. Введите меньшее количество:"
            )
            bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)
            return
        
        # Добавляем в корзину
        if user_chat_id not in carts:
            carts[user_chat_id] = []
        
        
        carts[user_chat_id].append({
            'photo': product['photo'],
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'product_id': product_id
        })


        # ⬇️ Уменьшаем остаток
        product['stock'] -= quantity
        save_stock_to_txt(products_clean)
        
        bot.send_message(
            user_chat_id,
            f"✅ Добавлено {quantity} шт. {product['name']} в корзину!",
            reply_markup=post_add_keyboard()
        )
        
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "⚠️ Пожалуйста, введите корректное число больше нуля!")
        bot.register_next_step_handler(msg, process_quantity, product_id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'cart')
def show_cart(call):
    user_chat_id = call.message.chat.id
    if user_chat_id not in carts or not carts[user_chat_id]:
        bot.send_message(
            user_chat_id, 
            "🛒 Ваша корзина пуста.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return
    
    
    total = 0
    for item in carts[user_chat_id]:
        item_total = item['price'] * item['quantity'] / 1000
        total += item_total
        
        # Отправляем фото товара с описанием
        with open(item['photo'], 'rb') as photo:
            bot.send_photo(
            user_chat_id,
            photo,
            caption=f"📦 {item['name']}\n"
                   f"🔢 Количество: {item['quantity']} шт.\n"
                   f"💰 Цена: {item_total:.3f}тг"
        )
    
    bot.send_message(
        user_chat_id,
        f"💳 Итого к оплате: {total:.3f}тг\n"
        "Выберите действие:",
        reply_markup=confirm_keyboard()
    )

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
        
        # Очищаем корзину
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
        bot.send_message(
            user_chat_id,
            f"🗑️ Товар {removed_item['name']} удален из корзины."
        )
    
    show_cart(call)

@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def back_to_main(call):
    start(call.message)



if __name__ == "__main__":
    print(f"Бот запущен. Режим обслуживания: {'ВКЛ' if BOT_MAINTENANCE else 'ВЫКЛ'}")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}. Перезапуск через 10 сек...")
            time.sleep(10)