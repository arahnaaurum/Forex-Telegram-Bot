import telebot
from telebot import types
import requests
import json
from config import TOKEN, AKEY, currencies

class APIException(Exception):
    pass

bot = telebot.TeleBot(TOKEN)

def new_keyboard (base = None):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = []
    for key in currencies.keys():
       if key != base:
            buttons.append(types.KeyboardButton(key.capitalize()))
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=["start", "help"])
def instructions(message: telebot.types.Message):
    user = message.from_user.first_name
    text = f"Привет, {user}! Я помогу тебе с конвертацией валют по актуальному курсу.\n " \
    "Для этого введи:" \
           "/values - узнать список доступных валют.\n" \
           "/convert - начать конвертацию.\n"\
           "/help - вывести пояснительный текст.\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["values"])
def val(message: telebot.types.Message):
    text = "Доступные валюты: "
    for key in currencies.keys():
        text += ("\n" + key)
    bot.reply_to(message, text=text)

@bot.message_handler(commands=["convert", ])
def exchange_1(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Выбери валюту, из которой мы конвертируем', reply_markup=new_keyboard())
    bot.register_next_step_handler(message, exchange_2)

def exchange_2(message: telebot.types.Message):
    cur_from = message.text.lower()
    bot.send_message(message.chat.id, 'Выбери валюту, в которую мы конвертируем', reply_markup=new_keyboard(cur_from))
    bot.register_next_step_handler(message, exchange_3, cur_from)

def exchange_3(message: telebot.types.Message, cur_from):
    cur_to = message.text.lower()
    bot.send_message(message.chat.id, 'Введи сумму валюты для конвертации')
    bot.register_next_step_handler(message, exchange_final, cur_from, cur_to)

def exchange_final(message: telebot.types.Message, cur_from, cur_to):
    amount = message.text.strip()
    check = None
    try:
        amount = float(amount)
        check = False
    except ValueError:
        check = True
        bot.reply_to(message, "Что-то не так c запросом!")
    if check:
        message = bot.send_message(message.chat.id, 'Введи сумму валюты для конвертации')
        bot.register_next_step_handler(message, exchange_final, cur_from, cur_to)
        return
    r = requests.get(f"https://free.currconv.com/api/v7/convert?q={currencies[cur_from]}_{currencies[cur_to]}&compact=ultra&apiKey={AKEY}")
    conv_rate = json.loads(r.content).values()
    conv_rate_list = list(
    json.loads(r.content).values())
    result = float(conv_rate_list[0]) * float(amount)
    text = f"Исходная валюта {cur_from}, количество - {amount}. Конвертация в {cur_to}, результат - {round(result, 2)}."
    bot.send_message(message.chat.id, text=text)

bot.polling()