import telebot
from config import TOKEN, currencies
from extensions import Forex, APIException

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start", "help"])
def instructions(message: telebot.types.Message):
    user = message.from_user.first_name
    text = f"Привет, {user}! Я помогу тебе с конвертацией валют по актуальному курсу.\n " \
    "Для этого введи через пробел:" \
           "1) название исходной валюты (кириллицей);\n" \
           "2) название валюты, в которую мы будем конвертировать исходную (кириллицей);\n" \
           "3) количество исходной валюты (числом; десятые/сотые части указываются через точку).\n" \
           "Например: 'доллар рубль 111.50'\n"\
           "Вот другие команды, которые тебе пригодятся:\n" \
           "/values - узнать список доступных валют.\n" \
           "/help - вывести пояснительный текст.\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["values"])
def val(message: telebot.types.Message):
    text = "Доступные валюты: "
    for key in currencies.keys():
        text += ("\n" + key)
    bot.reply_to(message, text=text)

@bot.message_handler(content_types=["text", ])
def exchange(message: telebot.types.Message):
    data = message.text.split()
    data = list(map(str.lower, data))
    try:
        if len(data) < 3:
            raise APIException("Кажется, введено слишком мало параметров")
        if len(data) > 3:
            raise APIException("Кажется, введено слишком много параметров")
        cur_from, cur_to, amount = data
        result = Forex.get_price(cur_to, cur_from, amount)
    except APIException as e:
        bot.reply_to(message, f"Что-то не так c запросом!\n{e}")
    except Exception as e:
        bot.reply_to(message, f"Что-то пошло не так!\n{e}")
    else:
        text = f"Исходная валюта {cur_from}, количество - {amount}. Конвертация в {cur_to}, результат - {round(result, 2)}."
        bot.reply_to(message, text=text)

bot.polling()