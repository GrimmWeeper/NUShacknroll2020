#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This bot manages projects through Telegram

It provides updates on how project members are working on different tasks of the projects, helps set meeting timings and agendas.
"""
import logging
import telegram
from pyMethods import DB

from telegram.error import NetworkError, Unauthorized
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

update_id = None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
PROJECT_NAME, MEMBERS, MEMBERS2, EMOJI, LAST_EMOJI, START_PROJECT = range(6)
ADDTODO2, ADDTODO3 = range(2)
ADDDOING2, ADDDOING3 = range(2)
ADDDONE2, ADDDONE3 = range(2)
MOVETASK2, MOVETASK3 = range(2)
DELETETASK2, DELETETASK3 = range(2)
user_data = dict()
temp_emo = ""
temp_data = []


def start(update, context):
    update.message.reply_text(
        "Hello! Let's start a project! What would you like to name this project?"
    )
    return PROJECT_NAME


def project_name(update, context):
    name = str(update.message.text)
    db = DB()
    user_data['board'] = db.board_ref(name)
    if db.board_ref(name).check_if_empty():
        db.board_ref(name).create_from_template()
    update.message.reply_text(
        "Okay, Project " + name + " started!\n"
                                  "How many members do you have inside your project?",
    )

    return MEMBERS


def add_members(update, context):
    user_data['members'] = int(update.message.text)
    user_data['members_list'] = []
    user_data['emoji_list'] = []
    update.message.reply_text("Who's in the project?")
    return MEMBERS2


def add_members2(update, context):
    members_list = user_data.get('members_list')
    members_list.append(update.message.text)
    members = user_data.get('members') - 1
    user_data['members'] = members
    update.message.reply_text("What is {}'s emoji?".format(members_list[-1]))
    if members > 0:
        return EMOJI
    else:
        return START_PROJECT


def add_emoji(update, context):
    emoji_list = user_data.get('emoji_list')
    emoji_list.append(update.message.text)
    members_list = user_data.get('members_list')
    board = user_data['board'].add_member(name=members_list[-1], emoji=emoji_list[-1])
    update.message.reply_text("Alright! Who's the next members?")
    return MEMBERS2


def add_last_emoji(update, context):
    members_list = user_data.get('members_list')
    update.message.reply_text("What is {}'s emoji?".format(members_list[-1]))
    return START_PROJECT


def start_project(update, context):
    emoji_list = user_data.get('emoji_list')
    emoji_list.append(update.message.text)
    members_list = user_data.get('members_list')
    print("marker")
    print(update.message.text)
    board = user_data['board'].add_member(name=members_list[-1], emoji=update.message.text)
    update.message.reply_text("Here's your project code: #1234\n")
    return -1


def show_tasks(update, context):
    data = user_data.get('board').read_tasks()
    reply_text = "*Doing*\n"
    doing = data['doing']['body']
    for x in doing:
        reply_text += x + ": " + doing.get(x) + "\n"
    reply_text += "\n"

    reply_text += "*Todo*\n"
    doing = data['todo']['body']
    for x in doing:
        reply_text += x + ": " + doing.get(x) + "\n"
    reply_text += "\n"

    reply_text += "*Done*\n"
    doing = data['done']['body']
    for x in doing:
        reply_text += x + ": " + doing.get(x) + "\n"
    update.message.reply_text(reply_text, ParseMode.MARKDOWN)
    reply_text += "\n"


def show_members(update, context):
    data = user_data.get('board').read_members()
    reply_text = ""
    for x in data:
        reply_text += x + ": " + data.get(x)['emoji'] + "\n"

    update.message.reply_text(reply_text)


##############################################################
# ADD TASK
##############################################################
# TODO: Change emojis selection into buttons
def add_task_todo_1(update, context):
    data = user_data.get('board').read_members()
    emoji_list = []
    print(data)
    for x in data:
        emoji_list.append(str(data[x]['emoji']))
    reply_keyboard = [emoji_list]
    update.message.reply_text(
        "Please type in the emoji:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ADDTODO2


def add_task_todo_2(update, context):
    user_data['temp_emo'] = update.message.text
    update.message.reply_text(
        "Please enter To-Do tasks:"
    )
    return ADDTODO3


def add_task_todo_3(update, context):
    temp_text = update.message.text
    user_data.get('board').add_task("todo", temp_text, user_data.get('temp_emo'))
    update.message.reply_text(
        "Task Recorded! Use /showTasks to see the tasks."
    )
    return -1

def add_task_doing_1(update, context):
    data = user_data.get('board').read_members()
    emoji_list = []
    print(data)
    for x in data:
        emoji_list.append(str(data[x]['emoji']))
    reply_keyboard = [emoji_list]
    update.message.reply_text(
        "Please type in the emoji:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ADDDOING2


def add_task_doing_2(update, context):
    user_data['temp_emo'] = update.message.text
    update.message.reply_text(
        "Please enter Doing tasks:"
    )
    return ADDDOING3


def add_task_doing_3(update, context):
    temp_text = update.message.text
    user_data.get('board').add_task("doing", temp_text, user_data.get('temp_emo'))
    update.message.reply_text(
        "Task Recorded! Use /showTasks to see the tasks."
    )
    return -1


def add_task_done_1(update, context):
    data = user_data.get('board').read_members()
    emoji_list = []
    print(data)
    for x in data:
        emoji_list.append(str(data[x]['emoji']))
    reply_keyboard = [emoji_list]
    update.message.reply_text(
        "Please type in the emoji:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ADDDONE2


def add_task_done_2(update, context):
    user_data['temp_emo'] = update.message.text
    update.message.reply_text(
        "Please enter Doing tasks:"
    )
    return ADDDONE3


def add_task_done_3(update, context):
    temp_text = update.message.text
    user_data.get('board').add_task("done", temp_text, user_data.get('temp_emo'))
    update.message.reply_text(
        "Task Recorded! Use /showTasks to see the tasks."
    )
    return -1



##############################################################
# MOVE TASK
##############################################################    

def moving_task_1(update, context):
    reply_keyboard = [['To-Do', 'Doing']]
    update.message.reply_text("Choose the categories of tasks that you want to move.",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return MOVETASK2


def moving_task_2(update, context):
    if update.message.text == "To-Do":
        user_data['temp_data'] = "To-Do"
        data = user_data.get('board').read_tasks()
        data_list = data['todo']['body']
        reply_keyboard = [data_list]
        update.message.reply_text("Choose the tasks no. that you would like to move from.",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MOVETASK3

    elif update.message.text == "Doing":
        user_data['temp_data'] = "Doing"
        data = user_data.get('board').read_tasks()
        data_list = data['doing']['body']
        reply_keyboard = [data_list]
        update.message.reply_text("Choose the tasks no. that you would like to move.",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return MOVETASK3


def moving_task_3(update, context):
    if user_data['temp_data'] == "To-Do":
        user_data['board'].move_task("todo", "doing", update.message.text)
        print(update.message.text)

    elif user_data['temp_data'] == "Doing":
        user_data['board'].move_task("doing", "done", update.message.text)
        print(update.message.text)

    update.message.reply_text(
        "Task moved! Use /showTasks to see the tasks."
    )
    return -1


##############################################################
# DELETE TASK
##############################################################    

def delete_task_1(update, context):
    reply_keyboard = [['To-Do', 'Doing', 'Done']]
    update.message.reply_text("Choose the categories of tasks that you want to delete from.",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return DELETETASK2


def delete_task_2(update, context):
    if update.message.text == "To-Do":
        user_data['temp_data'] = "To-Do"
        data = user_data.get('board').read_tasks()
        data_list = data['todo']['body']
        reply_keyboard = [data_list]
        update.message.reply_text("Choose the tasks no. that you would like to delete.",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return DELETETASK3

    elif update.message.text == "Doing":
        user_data['temp_data'] = "Doing"
        data = user_data.get('board').read_tasks()
        data_list = data['doing']['body']
        reply_keyboard = [data_list]
        update.message.reply_text("Choose the tasks no. that you would like to move.",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
        return DELETETASK3

    elif update.message.text == "Done":
        user_data['temp_data']  = "Done"
        data = user_data.get('board').read_tasks()
        data_list = data['done']['body']
        reply_keyboard = [data_list]
        update.message.reply_text("Choose the tasks no. that you would like to move.",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
        return DELETETASK3


def delete_task_3(update, context):
    if user_data['temp_data'] == "To-Do":
        user_data['board'].delete_task("todo", update.message.text)

    elif user_data['temp_data'] == "Doing":
        user_data['board'].delete_task("doing", update.message.text)

    elif user_data['temp_data'] == "Done":
        user_data['board'].delete_task("done", update.message.text)

    update.message.reply_text(
        "Task deleted! Use /showTasks to see the tasks."
    )
    return -1

def cancel(update,context):
    update.message.reply_text(
        "Action Cancelled! What would you like to do now?"
    )
    return -1
def main():
    """Run the bot."""
    global update_id

    # Telegram Bot Authorization Token
    updater = Updater('941751379:AAELtiX3GIR_tvj1ibksOWa-a5dm6X8ZTJw', use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROJECT_NAME: [MessageHandler(Filters.text, project_name)],
            MEMBERS: [MessageHandler(Filters.text, add_members)],
            MEMBERS2: [MessageHandler(Filters.text, add_members2)],
            EMOJI: [MessageHandler(Filters.text, add_emoji)],
            LAST_EMOJI: [MessageHandler(Filters.text, add_last_emoji)],
            START_PROJECT: [MessageHandler(None, start_project)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("showTasks", show_tasks))
    dp.add_handler(CommandHandler("showMembers", show_members))

    addtodo = ConversationHandler(
        entry_points=[CommandHandler('addToDo', add_task_todo_1)],
        states={
            ADDTODO2: [MessageHandler(Filters.text, add_task_todo_2)],
            ADDTODO3: [MessageHandler(Filters.text, add_task_todo_3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(addtodo)

    addDoing = ConversationHandler(
        entry_points=[CommandHandler('addDoing', add_task_todo_1)],
        states={
            ADDDOING2: [MessageHandler(Filters.text, add_task_doing_2)],
            ADDDOING3: [MessageHandler(Filters.text, add_task_doing_3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(addDoing)

    addDone = ConversationHandler(
        entry_points=[CommandHandler('addDone', add_task_todo_1)],
        states={
            ADDDONE2: [MessageHandler(Filters.text, add_task_done_2)],
            ADDDONE3: [MessageHandler(Filters.text, add_task_done_3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(addDone)

    moveTask = ConversationHandler(
        entry_points=[CommandHandler('moveTask', moving_task_1)],
        states={
            MOVETASK2: [MessageHandler(Filters.text, moving_task_2)],
            MOVETASK3: [MessageHandler(Filters.text, moving_task_3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(moveTask)

    deleteTask = ConversationHandler(
        entry_points=[CommandHandler('deleteTask', delete_task_1)],
        states={
            DELETETASK2: [MessageHandler(Filters.text, delete_task_2)],
            DELETETASK3: [MessageHandler(Filters.text, delete_task_3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(deleteTask)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
