import telebot
import requests
from config import TOKEN
from bs4 import BeautifulSoup as BS
from telebot import types
from flask import Flask, request
import os


city = ''
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start = types.KeyboardButton('/start')
keyboard_weather = types.KeyboardButton('/weather')
markup.add(keyboard_start, keyboard_weather)


@bot.message_handler('start')
def start_message(message):
    bot.send_message(message.chat.id, 'Напиши город в котором ты находишься?', reply_markup=markup)
    bot.register_next_step_handler(message, reg_city)
    print(city)


@bot.message_handler('weather')
def weather_message(message):
    if not city == '':
        r = requests.get(f'https://sinoptik.ua/погода-{city}')
        html = BS(r.content, 'html.parser')
        for el in html.select('#content'):
            t_min = el.select('.temperature .min')[0].text
            t_max = el.select('.temperature .max')[0].text
            text = el.select('.description')[0].text
        bot.send_message(message.chat.id, f'Температура на сегодня {t_min} - {t_max}\n{text}')
    else:
        bot.send_message(message.chat.id, 'Сначала введите название город с помощью команды /start')


def reg_city(message):
    global city
    city = message.text
    bot.send_message(message.chat.id, f'отлично{message.first_name}\nты так же можешь использовать команду'
                                      f' /start для изменения города')


@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "Python Telegram Bot 25-11-2022", 200


@app.route('/')
def main():
    bot.remove_webhook()
    bot.set_webhook(url='https://weather123bot.herokuapp.com/' + TOKEN)
    return "Python Telegram Bot", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
