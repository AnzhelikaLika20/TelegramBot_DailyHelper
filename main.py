import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import time
import logging
import schedule
from multiprocessing import *


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
        zodiac_links[i.text] = "https://horo.mail.ru/" + i['href']
        # print(i.text + " " + zodiac_links[i.text])

    # getting links for the today prediction
    zodiac_prediction_links = {}
    for i in zodiac_links:
        request_to_zodiac = requests.get(zodiac_links[i])
        current_page = BeautifulSoup(request_to_zodiac.text, 'html.parser')
        for j in current_page.findAll('a'):
            if j.strong:
                link = j['href']
                if link[0] == '/':
                    link = "https://horo.mail.ru" + link
                zodiac_prediction_links[i] = link
                # print(i + " " + zodiac_prediction_links[i])
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
    item1 = types.KeyboardButton("Овен")
    item2 = types.KeyboardButton("Рыбы")
    item3 = types.KeyboardButton('Лев')
    item4 = types.KeyboardButton('Близнецы')
    item5 = types.KeyboardButton('Скорпион')
    item6 = types.KeyboardButton('Весы')
    item7 = types.KeyboardButton('Водолей')
    item8 = types.KeyboardButton('Телец')
    item9 = types.KeyboardButton('Рак')
    item10 = types.KeyboardButton('Козерог')
    item11 = types.KeyboardButton('Стрелец')
    item12 = types.KeyboardButton('Дева')
    markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12)
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
        if message.text == 'Овен':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Овен'],
                             reply_markup=markup)
        if message.text == 'Рыбы':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Рыбы'],
                             reply_markup=markup)
        if message.text == 'Лев':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Лев'],
                             reply_markup=markup)
        if message.text == 'Близнецы':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Близнецы'],
                             reply_markup=markup)
        if message.text == 'Скорпион':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Скорпион'],
                             reply_markup=markup)
        if message.text == 'Весы':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Весы'],
                             reply_markup=markup)
        if message.text == 'Водолей':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Водолей'],
                             reply_markup=markup)
        if message.text == 'Телец':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Телец'],
                             reply_markup=markup)
        if message.text == 'Рак':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Рак'],
                             reply_markup=markup)
        if message.text == 'Козерог':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Козерог'],
                             reply_markup=markup)
        if message.text == 'Стрелец':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Стрелец'],
                             reply_markup=markup)
        if message.text == 'Дева':
            bot.send_message(message.chat.id,
                             zodiac_predictions['Дева'],
                             reply_markup=markup)


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


