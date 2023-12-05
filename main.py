# add parser
from FB_parser import FacebookParser

# add param
from config import BOT_TOKEN

import telebot
bot = telebot.TeleBot(BOT_TOKEN)

# Функція для створення первинного посилання для парсингу
def construct_marketplace_url(url=None, min_price=None, max_price=None, min_mileage=None,
                              max_mileage=None, min_year=None, max_year=None,
                              make=None, transmission_type=None):
    constructed_url = f"{url}"
    constructed_url += f"&minPrice={min_price}"
    constructed_url += f"&maxPrice={max_price}"
    constructed_url += f"&minMileage={min_mileage}"
    constructed_url += f"&maxMileage={max_mileage}"
    constructed_url += f"&minYear={min_year}"
    constructed_url += f"&maxYear={max_year}"
    constructed_url += f"&make={make}"
    constructed_url += f"&transmissionType={transmission_type}"

    return constructed_url

user_data = {}  # Dictionary to store user input
user_parsers = {}

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
stop_button = telebot.types.KeyboardButton('Стоп 🛑')
start_button = telebot.types.KeyboardButton('Старт 🚀')
keyboard.add(stop_button, start_button)

@bot.message_handler(func=lambda message: message.text.lower() == 'старт 🚀')
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_parsers[user_id] = FacebookParser()
    user_parsers[user_id].should_continue_parsing = True
    bot.reply_to(message, "Welcome! Please enter geolacation: ", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.lower() == 'стоп 🛑')
@bot.message_handler(commands=['stop'])
def stop_parsing(message):
    user_id = message.chat.id
    user_parsers[user_id].stop_parsing()
    bot.reply_to(message, "Parsing will be stopped after the current iteration.")
    
@bot.message_handler(func=lambda message: True)
def handle_user_input(message):
    user_id = message.chat.id
    chat_id = message.chat.id

    # Check if user data exists, if not, initialize it
    if chat_id not in user_data:
        user_data[chat_id] = {}

    # Prompt the user for the next piece of information based on the current state
    current_state = len(user_data[chat_id])
    # За бажанням можна перекласти
    prompt_messages = [
        "Enter minimum price: ",
        "Enter maximum price: ",
        "Enter minimum mileage: ",
        "Enter maximum mileage: ",
        "Enter minimum year: ",
        "Enter maximum year: ",
        "Enter make: ",
        "Enter transmission type: "
    ]

    # Get the user input based on the current state
    if current_state < len(prompt_messages):
        user_data[chat_id][current_state] = message.text
        bot.reply_to(message, prompt_messages[current_state])
    else:
        # All information collected, construct the URL
        result_url = construct_marketplace_url(*user_data[chat_id].values())
        bot.reply_to(message, f'<a href="{result_url}">Первинна сторінка для парсингу</a>', parse_mode='HTML', disable_web_page_preview=True)
        
        # Clear user data for the next search
        del user_data[chat_id]
        user_parsers[user_id].parse_fb(chat_id, result_url)


# Polling loop to keep the bot running
bot.polling(none_stop=True)
