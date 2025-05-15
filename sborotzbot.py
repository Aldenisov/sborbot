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
    "stores": ["Магнит", "Пятерочка", "Перекресток", "Лента", "Другой магазин"],
    "categories": {
        "Чистота": ["Отличная", "Хорошая", "Удовлетворительная", "Плохая"],
        "Персонал": ["Вежливый", "Внимательный", "Нейтральный", "Грубый"],
        "Цены": ["Низкие", "Средние", "Высокие"],
        "Ассортимент": ["Широкий", "Средний", "Ограниченный"],
        "Другое": []
    },
    "feedback_types": ["Предложение", "Жалоба", "Благодарность"]
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

def handle_store_selection(chat_id):
    keyboard = create_keyboard(CONFIG["stores"])
    bot.send_message(chat_id, "Выберите магазин:", reply_markup=keyboard)

def ask_for_custom_store(chat_id):
    bot.send_message(
        chat_id,
        "Введите название магазина:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    feedback_data["users"][str(chat_id)] = {"waiting_for_store": True}
    save_data(feedback_data)

def ask_feedback_category(chat_id):
    keyboard = create_keyboard(list(CONFIG["categories"].keys()))
    bot.send_message(chat_id, "Выберите категорию отзыва:", reply_markup=keyboard)

def handle_category_selection(chat_id, category):
    user_data = feedback_data["users"][str(chat_id)]
    user_data["current_feedback"]["category"] = category
    
    if CONFIG["categories"][category]:
        options = CONFIG["categories"][category] + ["Свой вариант"]
        keyboard = create_keyboard(options)
        bot.send_message(chat_id, f"Выберите оценку для '{category}':", reply_markup=keyboard)
    else:
        ask_for_feedback_text(chat_id)

def ask_for_custom_rating(chat_id):
    bot.send_message(
        chat_id,
        "Введите свою оценку:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    feedback_data["users"][str(chat_id)]["waiting_for_rating"] = True
    save_data(feedback_data)

def handle_custom_rating(chat_id, rating):
    user_data = feedback_data["users"][str(chat_id)]
    user_data["current_feedback"]["rating"] = rating
    user_data["waiting_for_rating"] = False
    save_data(feedback_data)
    ask_feedback_type(chat_id)

def ask_feedback_type(chat_id):
    keyboard = create_keyboard(CONFIG["feedback_types"])
    bot.send_message(chat_id, "Выберите тип отзыва:", reply_markup=keyboard)

def ask_for_feedback_text(chat_id):
    bot.send_message(
        chat_id,
        "Напишите ваш отзыв:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    feedback_data["users"][str(chat_id)]["waiting_for_text"] = True
    save_data(feedback_data)

def complete_feedback(chat_id, text):
    user_id = str(chat_id)
    user_data = feedback_data["users"][user_id]

    feedback = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        **user_data["current_feedback"],
        "text": text
    }

    feedback_data["feedbacks"].append(feedback)
    if "feedbacks" not in user_data:
        user_data["feedbacks"] = []
    user_data["feedbacks"].append(feedback)

    keys_to_remove = [
        "current_feedback", "waiting_for_text",
        "waiting_for_store", "waiting_for_rating"
    ]
    for key in keys_to_remove:
        if key in user_data:
            del user_data[key]

    save_data(feedback_data)
    bot.send_message(chat_id, CONFIG["thanks_message"])
    show_main_menu(chat_id)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    user_id = str(chat_id)

    if user_id not in feedback_data["users"]:
        feedback_data["users"][user_id] = {}

    if text == "Оставить отзыв":
        start_feedback(chat_id)
    elif text == "Магазин":
        handle_store_selection(chat_id)
    elif text in CONFIG["stores"]:
        if text == "Другой магазин":
            ask_for_custom_store(chat_id)
        else:
            feedback_data["users"][user_id]["current_feedback"] = {"store": text}
            save_data(feedback_data)
            ask_feedback_category(chat_id)
    elif feedback_data["users"][user_id].get("waiting_for_store"):
        feedback_data["users"][user_id]["current_feedback"] = {"store": text}
        feedback_data["users"][user_id]["waiting_for_store"] = False
        save_data(feedback_data)
        ask_feedback_category(chat_id)
    elif text in CONFIG["categories"]:
        handle_category_selection(chat_id, text)
    elif any(text in options for options in CONFIG["categories"].values()):
        if text == "Свой вариант":
            ask_for_custom_rating(chat_id)
        else:
            feedback_data["users"][user_id]["current_feedback"]["rating"] = text
            save_data(feedback_data)
            ask_feedback_type(chat_id)
    elif feedback_data["users"][user_id].get("waiting_for_rating"):
        handle_custom_rating(chat_id, text)
    elif text in CONFIG["feedback_types"]:
        feedback_data["users"][user_id]["current_feedback"]["feedback_type"] = text
        save_data(feedback_data)
        ask_for_feedback_text(chat_id)
    elif feedback_data["users"][user_id].get("waiting_for_text"):
        complete_feedback(chat_id, text)
    else:
        bot.send_message(chat_id, "Используйте кнопки для навигации.")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
