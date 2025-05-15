import json
import os
import telebot
from telebot import types
from datetime import datetime

#@Sborotz48bot бот для использования кода

CONFIG = {
    "admin_id": 1843685456,
    "data_file": "feedback_data.json",
    "welcome_message": "Добро пожаловать в бот для сбора отзывов о магазинах В Липецкой Области. Нажмите 'Старт' чтобы начать.",
    "thanks_message": "Спасибо за ваш отзыв! Хотите оставить еще один?",
    "stores": ["Линия", "Лента", "Магнит", "Ашан", "Апельсин", "Липка", "Другой магазин"],
    "services": ["Доставка", "Обслуживание", "Ассортимент", "Цены", "Чистота"],
    "feedback_types": ["Предложение", "Жалоба", "Благодарность"]
}

bot = telebot.TeleBot("7504179050:AAFIOaoYJRG6wONsGR9RcyzpZam2vsE6GGs")

feedback_data = {"feedbacks": [], "users": {}}


def load_data():
    if os.path.exists(CONFIG["data_file"]):
        with open(CONFIG["data_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"feedbacks": [], "users": {}}


def save_data():
    with open(CONFIG["data_file"], "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)


def create_keyboard(options, one_time=False):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=one_time)
    for option in options:
        keyboard.add(types.KeyboardButton(option))
    return keyboard


@bot.message_handler(commands=['start'])
def handle_start(message):
    start_keyboard = create_keyboard(["Старт"])
    bot.send_message(message.chat.id, CONFIG["welcome_message"], reply_markup=start_keyboard)


@bot.message_handler(func=lambda message: message.text == "Старт")
def handle_start_button(message):
    show_main_menu(message.chat.id)


def show_main_menu(chat_id):
    menu_options = ["Оставить отзыв", "Мои отзывы", "Помощь"]
    keyboard = create_keyboard(menu_options)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)


def start_feedback(chat_id):
    keyboard = create_keyboard(["Магазин", "Услуга"])
    bot.send_message(chat_id, "О чем вы хотите оставить отзыв?", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    user_id = str(chat_id)

    if text in ["/start", "Старт"]:
        return

    if user_id in feedback_data["users"]:
        if feedback_data["users"][user_id].get("waiting_for_store_name"):
            handle_custom_store(chat_id, text)
            return
        elif feedback_data["users"][user_id].get("waiting_for_feedback"):
            complete_feedback(chat_id, message.from_user.id, text)
            ask_for_another_feedback(chat_id)
            return

    if text == "Оставить отзыв":
        start_feedback(chat_id)
    elif text == "Мои отзывы":
        show_user_feedbacks(chat_id)
    elif text == "Помощь":
        help_text = "Этот бот собирает отзывы о магазинах. Выберите 'Оставить отзыв' чтобы начать."
        bot.send_message(chat_id, help_text)
    elif text == "Да, хочу еще":
        start_feedback(chat_id)
    elif text == "Нет, достаточно":
        bot.send_message(chat_id, "Спасибо за ваши отзывы!", reply_markup=types.ReplyKeyboardRemove())
        show_main_menu(chat_id)
    elif text in ["Магазин", "Услуга"]:
        handle_feedback_type(chat_id, text)
    elif text in CONFIG["stores"]:
        if text == "Другой магазин":
            ask_for_custom_store(chat_id)
        else:
            ask_feedback_details(chat_id, "store", text)
    elif text in CONFIG["services"]:
        ask_feedback_details(chat_id, "service", text)
    elif text in CONFIG["feedback_types"]:
        ask_feedback_text(chat_id, message.from_user.id, text)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопки для навигации.")
        show_main_menu(chat_id)


def ask_for_custom_store(chat_id):
    user_id = str(chat_id)
    if user_id not in feedback_data["users"]:
        feedback_data["users"][user_id] = {"feedbacks": []}

    feedback_data["users"][user_id]["current_feedback"] = {"type": "store"}
    feedback_data["users"][user_id]["waiting_for_store_name"] = True
    save_data()

    bot.send_message(chat_id, "Введите название магазина:", reply_markup=types.ReplyKeyboardRemove())


def handle_custom_store(chat_id, store_name):
    user_id = str(chat_id)
    feedback_data["users"][user_id]["current_feedback"]["item"] = store_name
    feedback_data["users"][user_id]["waiting_for_store_name"] = False
    save_data()

    keyboard = create_keyboard(CONFIG["feedback_types"])
    bot.send_message(chat_id, "Выберите тип отзыва:", reply_markup=keyboard)


def ask_for_another_feedback(chat_id):
    keyboard = create_keyboard(["Да, хочу еще", "Нет, достаточно"])
    bot.send_message(chat_id, CONFIG["thanks_message"], reply_markup=keyboard)


def handle_feedback_type(chat_id, feedback_type):
    user_id = str(chat_id)

    if user_id not in feedback_data["users"]:
        feedback_data["users"][user_id] = {"feedbacks": []}

    feedback_data["users"][user_id]["current_feedback"] = {"type": feedback_type.lower()}
    save_data()

    if feedback_type == "Магазин":
        keyboard = create_keyboard(CONFIG["stores"])
        bot.send_message(chat_id, "Выберите магазин:", reply_markup=keyboard)
    elif feedback_type == "Услуга":
        keyboard = create_keyboard(CONFIG["services"])
        bot.send_message(chat_id, "Выберите услугу:", reply_markup=keyboard)


def ask_feedback_details(chat_id, item_type, item_name):
    user_id = str(chat_id)
    feedback_data["users"][user_id]["current_feedback"]["item"] = item_name
    save_data()

    keyboard = create_keyboard(CONFIG["feedback_types"])
    bot.send_message(chat_id, "Выберите тип отзыва:", reply_markup=keyboard)


def ask_feedback_text(chat_id, user_id, feedback_type):
    user_id = str(user_id)
    feedback_data["users"][str(chat_id)]["current_feedback"]["feedback_type"] = feedback_type
    feedback_data["users"][str(chat_id)]["waiting_for_feedback"] = True
    save_data()

    bot.send_message(chat_id, "Напишите ваш отзыв подробно:", reply_markup=types.ReplyKeyboardRemove())


def complete_feedback(chat_id, user_id, feedback_text):
    user_id = str(user_id)
    chat_id_str = str(chat_id)

    if "current_feedback" not in feedback_data["users"].get(chat_id_str, {}):
        bot.send_message(chat_id, "Ошибка. Пожалуйста, начните заново.")
        show_main_menu(chat_id)
        return

    feedback = {
        "user_id": user_id,
        **feedback_data["users"][chat_id_str]["current_feedback"],
        "text": feedback_text,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

    feedback_data["feedbacks"].append(feedback)
    feedback_data["users"][chat_id_str]["feedbacks"].append(feedback)

    keys_to_remove = ["current_feedback", "waiting_for_feedback", "waiting_for_store_name"]
    for key in keys_to_remove:
        if key in feedback_data["users"][chat_id_str]:
            del feedback_data["users"][chat_id_str][key]

    save_data()

    notify_admin(feedback)
    bot.send_message(chat_id, "Отзыв сохранен!")


def notify_admin(feedback):
    message = (
        f"Новый отзыв\n"
        f"Магазин: {feedback.get('item', '')}\n"
        f"Тип: {feedback['feedback_type']}\n"
        f"Дата: {feedback['date']}\n"
        f"Текст: {feedback['text']}"
    )
    try:
        bot.send_message(CONFIG["admin_id"], message)
    except Exception as e:
        print(f"Ошибка уведомления админа: {e}")


def show_user_feedbacks(chat_id):
    user_id = str(chat_id)
    user_feedbacks = feedback_data["users"].get(user_id, {}).get("feedbacks", [])

    if not user_feedbacks:
        bot.send_message(chat_id, "Вы еще не оставляли отзывов.")
        return

    response = "Ваши отзывы:\n\n"
    for i, fb in enumerate(user_feedbacks, 1):
        response += (
            f"{i}. {fb.get('item', '')}\n"
            f"Тип: {fb['feedback_type']}\n"
            f"Дата: {fb['date']}\n"
            f"Текст: {fb['text']}\n\n"
        )

    bot.send_message(chat_id, response)


if __name__ == "__main__":
    feedback_data = load_data()
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Остановка бота: {e}")
