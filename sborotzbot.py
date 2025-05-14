import json
import os
import telebot
from telebot import types
from datetime import datetime

CONFIG = {
    "admin_id": 1843685456,
    "data_file": "feedback_data.json",
    "welcome_message": "Добро пожаловать в бот для сбора отзывов о магазинах.",
    "start_button": "Начать",
    "thanks_message": "Спасибо за ваш отзыв!",
    "stores": ["Магнит", "Пятерочка", "Перекресток", "Лента", "Другой магазин"]
}

bot = telebot.TeleBot("8073845003:AAEoS-6jRU6S9qecGHTLKQdSD28zmD6OmFU")

def load_data():
    if not os.path.exists(CONFIG["data_file"]):
        return {"feedbacks": [], "users": {}}
    with open(CONFIG["data_file"], "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(CONFIG["data_file"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

feedback_data = load_data()

def create_keyboard(options, row_width=2, one_time=False):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=row_width,
        resize_keyboard=True,
        one_time_keyboard=one_time
    )
    for option in options:
        keyboard.add(types.KeyboardButton(option))
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = create_keyboard([CONFIG["start_button"]])
    bot.send_message(
        message.chat.id,
        CONFIG["welcome_message"],
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda m: m.text == CONFIG["start_button"])
def handle_start_button(message):
    show_main_menu(message.chat.id)

def show_main_menu(chat_id):
    options = ["Оставить отзыв", "Мои отзывы", "Помощь"]
    keyboard = create_keyboard(options)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)

def start_feedback(chat_id):
    options = ["Магазин", "Услуга"]
    keyboard = create_keyboard(options)
    bot.send_message(chat_id, "Выберите категорию для отзыва:", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    if text == "Оставить отзыв":
        start_feedback(chat_id)
    else:
        bot.send_message(chat_id, "Используйте кнопки для навигации.")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
