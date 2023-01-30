# @nesibintek_bot
import telebot
from telebot import types
import requests
from string import punctuation
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from pycbrf import ExchangeRates
from datetime import datetime
import schedule
from threading import Thread
import time
import pandas as pd
from bs4 import BeautifulSoup


#запись лога от уровня INFO и выше в файл py_log.log + записывается время
logging.basicConfig(level=logging.INFO, filename="py_log.log",
                    format="%(asctime)s %(levelname)s %(message)s")
#logging.handlers.RotatingFileHandler(filename="py_log.log", maxBytes=40, backupCount=3)
with open('token.txt', 'r') as file:
    TOKEN = file.read()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    '''действия при вызове команды /start'''
    mess = f'Привет, <b>{message.from_user.first_name}</b>)'
 #   bot.send_message(message.chat.id, mess, parse_mode='html')
    bot.send_message(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['all_course'])
def start_handler(message):
    bot.send_message(message.chat.id, all_course_class.get())

@bot.message_handler(commands=['help'])
def start_handler(message):
    '''действия при вызове команды /help'''
    mess = f'<b>/add</b> - добавляет фразу\n<b>/del</b> - удаляет фразу\n<b>/all_phrases</b> - показывает все фразы в каталоге\n<b>/all_course</b> - покажет текущие курсы валют' \
           f'\n<b>/del_bad</b> - удалит слово\n<b>/add_bad</b> - добавит слово'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(commands=['all_phrases'])
def start_handler(message):
    '''действия при вызове команды /all_phrases'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        s1.execute(f'Select phrase from phrases')
        data ='\n'.join([i[0] for i in s1.fetchall()])
        bot.send_message(message.chat.id, data)



@bot.message_handler(commands=['add'])
def start_handler(message):
    '''действия при вызове команды /add'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.split()[1:])
        if len(e) > 0:
            bot.send_message(message.chat.id, f'фраза "{e}" добавлена')
            s1.execute(f'INSERT INTO phrases (phrase) VALUES (?)', (e,))
        else:
            bot.send_message(message.chat.id, f'фраза не должна быть пустой')

@bot.message_handler(commands=['del'])
def start_handler(message):
    '''действия при вызове команды /delete'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.split()[1:])
        s1.execute('SELECT COUNT(id) from phrases where phrase = ?', (e,))
        data = s1.fetchone()
        if data != (0,):
            s1.execute(f'DELETE FROM phrases WHERE phrase = ?', (e,))
            bot.send_message(message.chat.id, f'фраза "{e}" удалена')
        else:
            bot.send_message(message.chat.id, f'фразы не найдено')

@bot.message_handler(commands=['add_bad'])
def start_handler(message):
    '''действия при вызове команды /add_bad - добавление слова в таблицу'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.lower().split()[1:])
        s1.execute(f'SELECT count(name) from NAME where name = ?', (e,))
        data = s1.fetchone()
        if data == (0,):
            s1.execute(f'INSERT INTO bad_words (word) VALUES (?)', (e,))
            bot.send_message(message.chat.id, f'слово "{e}" добавлено')
        else:
            bot.send_message(message.chat.id, f'Такие слова не добавляю')


@bot.message_handler(commands=['del_bad'])
def start_handler(message):
    '''действия при вызове команды /del_bad - удаление слова из таблицы bad_words'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.lower().split()[1:])
        s1.execute(f'SELECT count(id) from bad_words where word = ?', (e, ))
        data = s1.fetchone()
        if data != (0,):
            s1.execute(f'DELETE FROM bad_words WHERE word = ?', (e,))
            bot.send_message(message.chat.id, f'слово "{e}" удалено')
        else:
            bot.send_message(message.chat.id, f'Такого слова нет')


@bot.message_handler(commands=['taboo'])
def start_handler(message):
    '''дeйствия при вызове команды taboo - добавляет слова в таблицу NAME, чтобы эти слова потом нельзя было
    добавить в таблицу bad_words'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.lower().split()[1:])
        s1.execute(f'INSERT INTO NAME (name) VALUES (?)', (e,))
        bot.send_message(message.chat.id, f'слово "{e}" добавлено в список исключений, его нельзя будет добавить в таблицу bad_words')

@bot.message_handler(commands=['taboo_del'])
def start_handler(message):
    '''дeйствия при вызове команды taboo_del - удаляет слово из таблицы NAME'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        e = ' '.join(message.text.lower().split()[1:])
        s1.execute(f'DELETE FROM NAME WHERE name = ?', (e,))
        bot.send_message(message.chat.id, f'слово "{e}" удалено из исключений и его можно добавлять в таблицу bad_words')

@bot.message_handler(commands=['taboo_all'])
def start_handler(message):
    '''действия при вызове комканды taboo_all - покажет список всех исключений'''
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        s1.execute(f'Select name from NAME')
        data = '\n'.join([i[0] for i in s1.fetchall()])
        bot.send_message(message.chat.id, data)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    try:
        '''обработка текстовых сообщений'''
        with sqlite3.connect('bot_nesibintelk.db') as s:
            s1 = s.cursor()
            in_str = message.text.lower().split()
            in_str = [i.strip(punctuation) for i in in_str]
            l = ['?' for _ in range(len(in_str))]
            l = ', '.join(l)
            s1.execute(f'SELECT id FROM bad_words WHERE word IN ({l})', in_str)
        # то, что вернется при исполнении команды в данный список, возвращаем один элемент
            data = s1.fetchone()
            if data:
                s1.execute('select phrase from phrases order by random() limit 1')
                data = s1.fetchall()
                bot.send_message(message.chat.id, data[0][0])
            s1.execute('UPDATE boys SET count = count + 1 WHERE id = ?', (message.from_user.id,))
        if message.text.lower() == 'все курсы':
            bot.send_message(message.chat.id, all_course_class.get())
    except:
        logging.exception('текст')

def send_course():
    bot.send_message(chat_id=-736597313, text=all_course_class.get())
    bot.send_message(chat_id=-1001214772818, text=all_course_class.get())

def check_apartment():
    if datetime.now().day == 19:
        bot.send_message(chat_id=-736597313, text='Подать данные по коммуналке')

def birthday():
    dates = str(datetime.now().day).rjust(2, '0') + '.' + str(datetime.now().month).rjust(2, '0')
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        s1.execute('SELECT name FROM birthday WHERE date = ?', (dates, ))
    b_day = s1.fetchone()
    if b_day:
        if b_day[0] != 'Инна':
            bot.send_message(chat_id=-1001214772818, text=f'Сегодня свой день рождение празднует {b_day[0]}! Давайте все вместе поздравим его!')
        else:
            bot.send_message(chat_id=-736597313, text='Инна, с днем рождения')




def greeting():
    bot.send_message(chat_id=-736597313, text='Доброе утро и хорошего дня!')
    bot.send_message(chat_id=-1001214772818, text='Доброе утро, 36.6')

def error():
    bot.send_message(chat_id=472546754, text='ловим ошибку')


def check_out_boys():
    with sqlite3.connect('bot_nesibintelk.db') as s:
        s1 = s.cursor()
        s1.execute('Select nick, count from boys ORDER BY 2 DESC' )
        all = s1.fetchall()
        text = '\n'.join([f'{i[0]} : {i[1]}' for i in all])
        bot.send_message(chat_id=472546754, text = f'Общая статистика: \n{text}')



class Clipboard:
    def __init__(self):
        self.course_lari = 0
        self.course_dollar = 0
        self.course_euro = 0
        self.course_ali = 0

    def lari(self):
        '''для получения курса лари'''
        e = requests.get('https://pokur.su/gel/rub/1/')
        d = e.text
        index_lari = d.index('грузинского лари в рублях на сегодня составляет')
        return d[index_lari + 48:index_lari + 53]

    def get_dollar(self):
        '''для получения курса доллара'''
        rates = ExchangeRates(datetime.now())
        return str(rates['USD'].value)[0:5]


    def get_ali(self):
        '''для получения курса али'''
        tables = pd.read_html('https://helpix.ru/currency/')
        for df in tables:
            if 'Aliexpress.ru' in df.columns:
                return df.loc[0, 'Aliexpress.ru']


    def get_euro(self):
        '''для получения курса евро'''
        rates = ExchangeRates(datetime.now())
        return str(rates['EUR'].value)[0:5]


    def get_all_course(self):
        self.course_lari = self.lari()
        self.course_dollar = self.get_dollar()
        self.course_euro = self.get_euro()
        self.course_ali = self.get_ali()

    def get(self):
        return f'курс лари: {self.course_lari}\n' \
               f'курс доллара: {self.course_dollar}\n'\
               f'курс евро: {self.course_euro}\n' \
               f'курс али: {self.course_ali}'


all_course_class = Clipboard()


#каждый день в определенное время запускаются задания
# schedule.every().day.at("08:00").do(birthday)
# schedule.every().day.at('09:00').do(greeting)
# schedule.every().day.at('11:10').do(send_course)
# schedule.every().day.at('12:00').do(check_apartment)
# schedule.every().monday.at('17:00').do(check_out_boys)
# schedule.every(1).minutes.do(check_out_boys)
schedule.every(1).minutes.do(all_course_class.get_all_course)

def bots():
    try:
        while True:
            bot.infinity_polling(timeout=10, long_polling_timeout = 5)
    except:
        logging.exception('бот упал')


def sch():
    try:
        while True:
            schedule.run_pending()
            time.sleep(2)
    except:
        logging.exception('время упало')


#2 потока - в одном работает бот, в другом проверка времени
variable = Thread(target=bots)
variable2 = Thread(target=sch)
variable.start()
variable2.start()





