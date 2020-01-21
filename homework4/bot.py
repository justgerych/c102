import telebot
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import datetime

Days = ['1day', '2day', '3day', '4day', '5day', '6day']
access_token = '1023985539:AAGGJZmmsIRWxZcM-XFRMnoYj_WRZFcx3h0'
telebot.apihelper.proxy = {'https': 'https://117.1.16.131:8080'}
bot = telebot.TeleBot(access_token)

def get_page(group: str, week: str='') -> str:
    if week:
        week = str(week) + '/'
    url = f'http://www.ifmo.ru/ru/schedule/0/{group}/{week}raspisanie_zanyatiy_{group}.htm'
    response = requests.get(url)
    web_page = response.text
    return web_page

def get_schedule(web_page: str, day: str) -> Tuple[List[str], List[str], List[str]]:
    soup = BeautifulSoup(web_page, "html5lib")

    # Получаем таблицу с расписанием на понедельник
    schedule_table = soup.find("table", attrs={"id": day})

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list

@bot.message_handler(commands=['near_lesson'])
def get_near_lesson(message: str) -> None:
    _, group = message.text.split()
    web_page = get_page(group)

    today = datetime.datetime.today().weekday()

    if today != 6:
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, Days[today])
        current_time = datetime.datetime.now().time()
        next_time = []
        next_location = []
        next_lesson = []

        for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
            time_ranges = time.split("-")
            time_components = []
            for i in time_ranges:
                time_components.append(i.split(":"))
            lesson_starts_time = datetime.time(hour=int(time_components[0][0]), minute=int(time_components[0][1]))
            lesson_ends_time = datetime.time(hour=int(time_components[1][0]), minute=int(time_components[1][1]))

            if current_time <= lesson_starts_time:
                next_time.append(time)
                next_location.append(location)
                next_lesson.append(lesson)

        resp = ''
        if next_time != []:
            resp += '<b>{}</b>, <i>{}</i>, {}\n'.format(next_time[0], next_location[0], next_lesson[0])
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Сегодня занятий больше нет!")
    else:
        bot.send_message(message.chat.id, 'Сегодня же Воскресенье!')

# BUG: week <- 0 || 2 = Crash
@bot.message_handler(commands=['all'])
def get_all(message: str) -> None:
    _, week, group = message.text.split()
    web_page = get_page(group, week)
    times = []
    locations = []
    lessons = []
    for current_day in Days:
        try:
            times_lst, locations_lst, lessons_lst = get_schedule(web_page, current_day)
            times.append(times_lst)
            locations.append(locations_lst)
            lessons.append(lessons_lst)
        except AttributeError:
            pass

    for day_time, day_location, day_lesson in zip(times, locations, lessons):
        resp = ''
        for time, location, lession in zip(day_time, day_location, day_lesson):
            resp += '<b>{}</b>, <i>{}</i>, {}\n'.format(time, location, lession)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['tomorrow'])
def get_tomorrow(message: str) -> None:
    _, group = message.text.split()
    web_page = get_page(group)
    today = datetime.datetime.today().weekday()
    if today == 5 or today == 6:
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, Days[0])
    else:
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, Days[today+1])

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, <i>{}</i>, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')

@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'])
def get_day(message: str) -> None:
    cmds = ['/monday', '/tuesday', '/wednesday', '/thursday', '/friday', '/saturday']
    cmd, week, group = message.text.split()
    day = cmds.index(cmd)
    web_page = get_page(group, week)
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, Days[day])

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, <i>{}</i>, {}\n'.format(time, location, lession)
    bot.send_message(message.chat.id, resp, parse_mode='HTML')

def decorator(func, toggle):
    def wrapper(message: str):
        if toggle:
            bot.send_message(message.chat.id,"*****************")
            func(message)
            bot.send_message(message.chat.id,"*****************")
        else:
            func(message)
    return wrapper

def greeting(message: str):
    bot.send_message(message.chat.id, "Hi there!")

@bot.message_handler(commands=['test_decorator'])
def test_decorator(message: str) -> None:
    _, toggle = message.text.split()

    if toggle == "false":
        toggle = False
    else:
        toggle = True

    func = decorator(greeting, toggle)
    func(message)

if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=123)
