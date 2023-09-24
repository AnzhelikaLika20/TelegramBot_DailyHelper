import logging
import os
import time
from multiprocessing import *

import requests
import schedule
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MSG = "Чтобы получить гороскоп на сегодня, выбери свой знак зодиака)"

bot = telebot.TeleBot(TOKEN)

zodiac_predictions = {}


def prepare_predictions():
    request = requests.get("https://horo.mail.ru/horoscope/zodiac/")
    page = BeautifulSoup(request.text, 'html.parser')
    divs = page.findAll("a", class_='hdr__text hdr__text_link')

    # dictionary with zodiacs and links to their pages
    zodiac_links = {}
    for i in divs:
        zodiac_links[i.text] = f"https://horo.mail.ru/{i['href']}"

    # getting links for the today prediction
    zodiac_prediction_links = {}
    for i in zodiac_links:
        request_to_zodiac = requests.get(zodiac_links[i])
        current_page = BeautifulSoup(request_to_zodiac.text, 'html.parser')
        for j in current_page.findAll('a'):
            if j.strong:
                link = j['href']
                if link[0] == '/':
                    link = f"https://horo.mail.ru{link}"
                zodiac_prediction_links[i] = link
                break

    # getting predictions
    for i in zodiac_prediction_links:
        request_to_prediction = requests.get(zodiac_prediction_links[i])
        current_page = BeautifulSoup(request_to_prediction.text, 'html.parser')
        div = current_page.findAll("div", class_="article__item article__item_alignment_left article__item_html")[0]
        prediction = ""
        for j in div.findAll('p'):
            prediction += j.text
        zodiac_predictions[i] = prediction


def zodiac_markup(markup):
    names = ['Близнецы', 'Весы', 'Водолей', 'Дева',
             'Козерог', 'Лев', 'Овен', 'Рак',
             'Рыбы', 'Скорпион', 'Стрелец', 'Телец']
    items = []
    for name in names:
        items.append(types.KeyboardButton(name))
    markup.add(*items)
    return markup


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    zodiac_markup(markup)
    bot.send_message(message.chat.id, f"Привет, {user_name}! {MSG}", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def go_send_messages(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    zodiac_markup(markup)
    if message.chat.type == 'private':
        if message.text in zodiac_predictions:
            bot.send_message(message.chat.id,
                             zodiac_predictions[message.text],
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Введен несуществующий знак зодиака")


def start_process():
    Process(target=start_schedule, args=()).start()


def start_schedule():
    schedule.every().day.at("00:01").do(prepare_predictions)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        print("start")
        prepare_predictions()
        print("preparations were made")
        start_process()
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as r:
        print("Непредвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")
