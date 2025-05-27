#!/usr/bin/python
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.util import antiflood
import time
import datetime
import threading
import mysql.connector
from config import db_config
from dml import insert_user, insert_task, insert_reminder, update_task_status, delete_task, update_report
from dql import get_known_users, get_tasks, get_active_reminders
from texts import texts

API_TOKEN = '7722682174:AAFxn9OtULIebfhuUcOlnUHYDMkDI6noLm8'
bot = telebot.TeleBot(API_TOKEN)

user_step = {}
spam_data = {}
spam_users = {}
user_lang = {}  
lower_limit, upper_limit, score_limit = 1, 10, 5
SpamBlockDuration = 20

def send_message(*args, **kwargs):
    return antiflood(bot.send_message, *args, **kwargs)

def check_user(cid, username):
    if cid not in get_known_users():
        insert_user(cid, username or "Unknown")
        print(f"New user added: {cid}")

def is_spam(cid):
    if cid in spam_users:
        return True
    now = time.time()
    spam_data.setdefault(cid, {"last_message_time": now, "score": 0})
    if now - spam_data[cid]['last_message_time'] < lower_limit:
        spam_data[cid]['score'] += 1
    elif now - spam_data[cid]['last_message_time'] > upper_limit:
        spam_data[cid]['score'] = max(0, spam_data[cid]['score'] - 1)
    spam_data[cid]['last_message_time'] = now
    if spam_data[cid]['score'] >= score_limit:
        spam_users[cid] = datetime.datetime.now() + datetime.timedelta(seconds=SpamBlockDuration)
        lang = user_lang.get(cid, 'en')
        send_message(cid, texts[lang]['spam_blocked'].format(duration=SpamBlockDuration))
        return True
    return False

def DoTasks():
    while True:
        now = datetime.datetime.now()
        to_remove = [cid for cid, exp_time in spam_users.items() if exp_time < now]
        for cid in to_remove:
            spam_users.pop(cid)
        reminders = get_active_reminders()
        for r in reminders:
            lang = user_lang.get(r['USER_ID'], 'en')
            send_message(r['USER_ID'], f"Reminder: {r['TITLE']}")
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM REMINDERS WHERE REMINDER_ID = %s", (r['REMINDER_ID'],))
            conn.commit()
            conn.close()
        time.sleep(5)

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Reminder"), KeyboardButton("Help"))
    markup.add(KeyboardButton("Planning"), KeyboardButton("Stats"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    send_message(cid, texts[lang]['welcome'], reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text in ["Reminder", "Help", "Planning", "Stats"])
def handle_main_menu(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    text = message.text
    if text == "Help":
        send_message(cid, texts[lang]['help'])
    elif text == "Reminder":
        send_message(cid, texts[lang]['reminder_text'], reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(texts[lang]['back'])))
        user_step[cid] = "reminder_text"
    elif text == "Planning":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Study", callback_data="category_study"),
                   InlineKeyboardButton("Work", callback_data="category_work"))
        markup.add(InlineKeyboardButton("Personal", callback_data="category_personal"))
        markup.add(InlineKeyboardButton(texts[lang]['back'], callback_data="back_to_menu"))
        send_message(cid, "Choose a category for your task:", reply_markup=markup)
        user_step[cid] = "planning_category"
    elif text == "Stats":
        tasks = get_tasks(cid)
        update_report(cid)
        if tasks:
            task_list = "Your tasks:"

            markup = InlineKeyboardMarkup()
            for i, task in enumerate(tasks):
                task_list += f"{i+1}. {task['TITLE']} ({task['CATEGORY']}): {task['STATUS']}"

                markup.add(InlineKeyboardButton(f"Edit {i+1}", callback_data=f"edit_task_{task['TASK_ID']}"),
                           InlineKeyboardButton(f"Delete {i+1}", callback_data=f"delete_task_{task['TASK_ID']}"))
            markup.add(InlineKeyboardButton(texts[lang]['back'], callback_data="back_to_menu"))
            send_message(cid, task_list, reply_markup=markup)
        else:
            send_message(cid, texts[lang]['stats_empty'], reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    if is_spam(cid):
        return
    lang = user_lang.get(cid, 'en')
    data = call.data
    if data.startswith("category_"):
        category = data.split("_")[1].capitalize()
        user_step[cid] = {"step": "planning_task", "category": category}
        send_message(cid, "What’s the task? Please send the task name.",
                     reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(texts[lang]['back'])))
        bot.answer_callback_query(call.id)
    elif data.startswith("edit_task_"):
        task_id = int(data.split("_")[2])
        update_task_status(task_id, "Completed" if get_tasks(cid)[0]['STATUS'] == "In Progress" else "In Progress")
        tasks = get_tasks(cid)
        task_list = "Your tasks:"

        markup = InlineKeyboardMarkup()
        for i, task in enumerate(tasks):
            task_list += f"{i+1}. {task['TITLE']} ({task['CATEGORY']}): {task['STATUS']}"

            markup.add(InlineKeyboardButton(f"Edit {i+1}", callback_data=f"edit_task_{task['TASK_ID']}"),
                       InlineKeyboardButton(f"Delete {i+1}", callback_data=f"delete_task_{task['TASK_ID']}"))
        markup.add(InlineKeyboardButton(texts[lang]['back'], callback_data="back_to_menu"))
        bot.edit_message_text(task_list, cid, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    elif data.startswith("delete_task_"):
        task_id = int(data.split("_")[2])
        delete_task(task_id)
        tasks = get_tasks(cid)
        if tasks:
            task_list = "Your tasks:\n"
        else:
            task_list = texts[lang]['stats_empty']
        markup = InlineKeyboardMarkup()
        for i, task in enumerate(tasks):
            task_list += f"{i+1}. {task['TITLE']} ({task['CATEGORY']}): {task['STATUS']}\n"
            markup.add(InlineKeyboardButton(f"Edit {i+1}", callback_data=f"edit_task_{task['TASK_ID']}"),
                       InlineKeyboardButton(f"Delete {i+1}", callback_data=f"delete_task_{task['TASK_ID']}"))
        markup.add(InlineKeyboardButton(texts[lang]['back'], callback_data="back_to_menu"))
        bot.edit_message_text(task_list, cid, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    elif data == "back_to_menu":
        user_step.pop(cid, None)
        send_message(cid, "Back to the main menu!", reply_markup=main_menu())
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == "planning_task" or isinstance(user_step.get(message.chat.id), dict) and user_step[message.chat.id].get("step") == "planning_task")
def handle_planning_task(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    if message.text != texts[lang]['back']:
        category = user_step[cid]["category"]
        task_id = insert_task(cid, category, message.text)
        send_message(cid, texts[lang]['task_added'].format(task=message.text, category=category), reply_markup=main_menu())
        user_step.pop(cid)
    else:
        user_step.pop(cid)
        send_message(cid, "Back to the main menu!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == "reminder_text")
def handle_reminder_text(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    if message.text != texts[lang]['back']:
        user_step[cid] = {"step": "reminder_date", "text": message.text}
        send_message(cid, texts[lang]['reminder_date'])
    else:
        user_step.pop(cid)
        send_message(cid, "Back to the main menu!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: isinstance(user_step.get(message.chat.id), dict) and user_step[message.chat.id].get("step") == "reminder_date")
def handle_reminder_date(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    try:
        datetime.datetime.strptime(message.text, "%Y/%m/%d")
        user_step[cid]["date"] = message.text
        user_step[cid]["step"] = "reminder_time"
        send_message(cid, texts[lang]['reminder_time'])
    except ValueError:
        send_message(cid, texts[lang]['reminder_error_date'])

@bot.message_handler(func=lambda message: isinstance(user_step.get(message.chat.id), dict) and user_step[message.chat.id].get("step") == "reminder_time")
def handle_reminder_time(message):
    cid = message.chat.id
    if is_spam(cid):
        return
    check_user(cid, message.chat.username)
    lang = user_lang.get(cid, 'en')
    try:
        reminder_time = datetime.datetime.strptime(f"{user_step[cid]['date']} {message.text}", "%Y/%m/%d %H:%M")
        task_id = insert_task(cid, "General", user_step[cid]['text'])
        insert_reminder(task_id, reminder_time)
        send_message(cid, texts[lang]['reminder_set'].format(text=user_step[cid]['text'], date=user_step[cid]['date'], time=message.text), reply_markup=main_menu())
        user_step.pop(cid)
    except ValueError:
        send_message(cid, texts[lang]['reminder_error_time'])

if __name__ == "__main__":
    threading.Thread(target=DoTasks, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
