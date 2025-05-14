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
    "thanks_message": "Спасибо за ваш отзыв!"
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

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(CONFIG["start_button"]))
    bot.send_message(
        message.chat.id,
        CONFIG["welcome_message"],
        reply_markup=keyboard
    )

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)