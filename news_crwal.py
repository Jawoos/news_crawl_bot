# -*- coding: utf-8 -*-

import time
import telepot
from telepot.loop import MessageLoop
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pymysql
import signal
import sys
from datetime import datetime


def save_log(log_msg):
    log_file = open("log.txt", "a", encoding="UTF8")
    log_file.write(time.asctime())
    log_file.write(': ')
    log_file.write(log_msg)
    log_file.write('\n')
    log_file.close()


def save_improve(improve_msg):
    # print('test')
    # print(msg['text'])
    date = str(datetime.today().year) + '-' + str(datetime.today().month) + '-' + str(datetime.today().day)
    path = './improve/'
    file_name = path + date + '.txt'
    person_name = improve_msg['chat']['first_name'] + ' ' + improve_msg['chat']['last_name'] + '(' + str(improve_msg['chat']['id']) + '): '
    # print(improve_msg['chat']['id'])
    log_file = open(file_name, "a", encoding="UTF8")
    log_file.write(time.asctime())
    log_file.write('\n')
    log_file.write(person_name)
    log_file.write(improve_msg['text'])
    log_file.write('\n\n')
    log_file.close()


def signal_handler(sig, frame):
    save_log('SIGINT')
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT `usnum` FROM `user` WHERE `investKR_news` = 1 or 'naver_news' = 1"
    cursor.execute(sql)
    save_log(sql)
    test = cursor.fetchall()
    for tid in test:
        bot.sendMessage(tid[0], "봇이 정지 되었습니다!!!\n금방 다시 실행되겠습니다~~!")
    conn.close()
    sys.exit(0)


def Chatbot(msg):
    global db_port, db_name, db_user, db_ip, db_pw
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `user` where usnum = " + str(chat_id) + ";"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    # print(msg)
    if msg['text'] == "/Subscribe_investKR_News":    # invest.kr 뉴스 구독
        if len(row) == 0:      # 데베에 등록되어 있지 않다면
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" + str(chat_id) + \
                  ", '" + msg['chat']['first_name'] + " " + msg['chat']['last_name'] + "', 1, 0);"
            cursor.execute(sql)     # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()
            bot.sendMessage(chat_id, "investing.kr 뉴스가 구독 되었습니다!")
        elif len(row) != 0:     # 데베에 데이터가 있다면
            cursor = conn.cursor()
            sql = "SELECT `investKR_news` FROM `user` WHERE `usnum` = " + str(chat_id)
            cursor.execute(sql)  # 데베에 등
            save_log(sql)
            test = cursor.fetchone()
            if test[0] == 0:
                cursor = conn.cursor()
                sql = "UPDATE user SET `investKR_news` = 1 WHERE `usnum` = " + str(chat_id)
                cursor.execute(sql)  # 데베에 가입 등록
                save_log(sql)
                conn.commit()
                bot.sendMessage(chat_id, "investing.kr 뉴스가 구독 되었습니다!")
            else:
                bot.sendMessage(chat_id, "investing.kr 뉴스가 이미 구독중입니다!")

    elif msg['text'] == "/Unsubscribe_investKR_News":      # invest.kr 뉴스 구독 해제
        cursor = conn.cursor()
        sql = "SELECT `investKR_news` FROM `user` WHERE `usnum` = " + str(chat_id)
        cursor.execute(sql)  # 데베에 등
        save_log(sql)
        test = cursor.fetchone()
        if test[0] == 0:
            bot.sendMessage(chat_id, "investing.kr 뉴스가 구독중이 아니십니다!")
            return
        cursor = conn.cursor()
        sql = "UPDATE user SET `investKR_news` = 0 WHERE `usnum` = " + str(chat_id)
        cursor.execute(sql)  # 데베에 가입 등록
        save_log(sql)
        conn.commit()
        bot.sendMessage(chat_id, "investing.kr 뉴스가 구독해제 되었습니다!")
    elif msg['text'] == "/Subscribe_Naver_News":    # Naver 뉴스 구독
        if len(row) == 0:      # 데베에 등록되어 있지 않다면
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" + str(chat_id) + \
                  ", '" + msg['chat']['first_name'] + " " + msg['chat']['last_name'] + "', 0, 1);"
            cursor.execute(sql)     # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()
            bot.sendMessage(chat_id, "네이버 뉴스가 구독 되었습니다!")
        elif len(row) != 0:     # 데베에 데이터가 있다면
            cursor = conn.cursor()
            sql = "SELECT `naver_news` FROM `user` WHERE `usnum` = " + str(chat_id)
            cursor.execute(sql)  # 데베에 등
            save_log(sql)
            test = cursor.fetchone()
            if test[0] == 0:
                cursor = conn.cursor()
                sql = "UPDATE user SET `naver_news` = 1 WHERE `usnum` = " + str(chat_id)
                cursor.execute(sql)  # 데베에 가입 등록
                save_log(sql)
                conn.commit()
                bot.sendMessage(chat_id, "네이버 뉴스가 구독 되었습니다!")
            else:
                bot.sendMessage(chat_id, "네이버 뉴스가 이미 구독중입니다!")

    elif msg['text'] == "/Unsubscribe_Naver_News":      # Naver 뉴스 구독 해제
        cursor = conn.cursor()
        sql = "SELECT `naver_news` FROM `user` WHERE `usnum` = " + str(chat_id)
        cursor.execute(sql)  # 데베에 등
        save_log(sql)
        test = cursor.fetchone()
        if test[0] == 0:
            bot.sendMessage(chat_id, "네이버 뉴스가 구독중이 아니십니다!")
            return
        cursor = conn.cursor()
        sql = "UPDATE user SET `naver_news` = 0 WHERE `usnum` = " + str(chat_id)
        cursor.execute(sql)  # 데베에 가입 등록
        save_log(sql)
        conn.commit()
        bot.sendMessage(chat_id, "네이버 뉴스가 구독해제 되었습니다!")
    # elif msg['text'] == "/send_message_to_developer":      # 메세지 받기
    #     print("get message")
    #     MessageLoop(bot, save_improve)
    elif msg['text'] == "/help":
        bot.sendMessage(chat_id, help_str)
    elif msg['text'] == "/start":
        bot.sendMessage(chat_id, help_str)
        if len(row) == 0:
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" + str(chat_id) + \
                  ", '" + msg['chat']['first_name'] + " " + msg['chat']['last_name'] + "', 0, 0);"
            print(sql)
            cursor.execute(sql)  # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()

    else:
        save_improve(msg)
    conn.close()


def crawl_invest(str0):
    global count_invest_err, admin_id, bot, count_popular, db_port, db_name, db_user, db_ip, db_pw
    try:
        req = Request(str0)
        req.add_header('User-Agent', 'Mozilla/5.0')
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find(class_="largeTitle")
        soup = soup.find_all(class_="textDiv")
        for row in soup:
            a = row.find('a')
            topic = a.text
            link = a.attrs['href']
            if topic not in queue_popular:
                queue_popular.append(topic)
                count_popular += 1
                if count_popular > 1000:
                    count_popular = 0
                    for i in range(500):
                        del queue_popular[0]
                msg = "\n[" + "invest.kr 인기 뉴스" + "]\n" + topic + "\n" + base_invest_url + link
                if for_the_first == 0:
                    continue
                conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
                cursor = conn.cursor()
                sql = "SELECT `usnum` FROM `user` WHERE `investKR_news` = 1"
                cursor.execute(sql)  # 데베에 등록
                save_log(sql)
                test = cursor.fetchall()
                for tid in test:
                    bot.sendMessage(tid[0], msg)
                conn.close()

        time.sleep(60)
    except ValueError:
        count_invest_err += 1
        print("error" + str(count_invest_err))
        if count_invest_err >= 500:
            print("err")
            bot.sendMessage(admin_id, "도메인에 문제가 있습니다.")
            count_invest_err = 0
        time.sleep(10)


def crawl_naver():
    global count_naver_err, admin_id, bot, count_naver, db_port, db_name, db_user, db_ip, db_pw
    try:
        req = Request('https://finance.naver.com/news/news_list.nhn?mode=RANK')
        req.add_header('User-Agent', 'Mozilla/5.0')
        html = urlopen(req).read()
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find(class_="newsList")
        soup = soup.find_all('a')
        for row in soup:
            topic = row.text
            link = row.attrs['href']
            if topic not in queue_naver:
                queue_naver.append(topic)
                count_naver += 1
                if count_naver > 1000:
                    count_naver = 0
                    for i in range(500):
                        del queue_naver[0]
                msg = "\n[" + "네이버 인기 뉴스" + "]\n" + topic + "\n" + base_naver_url + link
                if for_the_first == 0:
                    continue
                conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
                cursor = conn.cursor()
                sql = "SELECT `usnum` FROM `user` WHERE `naver_news` = 1"
                cursor.execute(sql)  # 데베에 등록
                save_log(sql)
                test = cursor.fetchall()
                for tid in test:
                    bot.sendMessage(tid[0], msg)
                conn.close()
        time.sleep(10)
    except:
        count_naver_err += 1
        print("error" + str(count_naver))
        if count_naver_err >= 500:
            print("err")
            bot.sendMessage(admin_id, "도메인에 문제가 있습니다.")
            count_naver_err = 0
        time.sleep(10)


# main
str_url = "https://kr.investing.com/news/most-popular-news"
base_invest_url = "https://kr.investing.com/"
base_naver_url = "https://finance.naver.com"

help_str = "안녕하세요 채팅봇 베타 버전입니다!!!\n" \
           "현재 사용 가능한 기능은 아래와 같습니다~\n" \
           "추가로 있었으면 하는 기능이나 문제점을 발견시\n" \
           "말씀해 주시면 감사하겠습니다!!!\n" \
           "개발자에게 메세지를 보내시고 싶으시면 채팅 치듯이 보내주시면 됩니다!!\n" \
           "invest.kr 인기 뉴스 구독 하기: /Subscribe_investKR_News\n" \
           "invest.kr 인기 뉴스 구독해제 하기: /Unsubscribe_investKR_News\n"\
           "Naver 인기 뉴스 구독 하기: /Subscribe_Naver_News\n" \
           "Naver 인기 뉴스 구독해제 하기: /Unsubscribe_Naver_News"


token_file = open("token_data.txt", "r", encoding="UTF8")
id_file = open("id_data.txt", "r", encoding="UTF8")
db_file = open("db_data.txt", "r", encoding="UTF8")
my_token = token_file.readline()
my_token = my_token[1:]
admin_id = id_file.readline()
db_ip = db_file.readline()
db_ip = db_ip[:len(db_ip)-1]
db_user = db_file.readline()
db_user = db_user[:len(db_user)-1]
db_pw = db_file.readline()
db_pw = db_pw[:len(db_pw)-1]
db_name = db_file.readline()
db_name = db_name[:len(db_name)-1]
db_port = db_file.readline()
db_port = int(db_port)
token_file.close()
id_file.close()
db_file.close()

tele_id = []

for_the_first = 0;
count_naver = 0
count_popular = 0
count_invest_err = 0    # invest error 횟수
count_naver_err = 0    # naver error 횟수
queue_popular = []
queue_naver = []

signal.signal(signal.SIGINT, signal_handler)
bot = telepot.Bot(my_token)
MessageLoop(bot, Chatbot).run_as_thread()
conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
cursor = conn.cursor()
sql = "SELECT `usnum` FROM `user` WHERE `investKR_news` = 1 or 'naver_news' = 1"
cursor.execute(sql)
save_log(sql)
test = cursor.fetchall()
for tid in test:
    try:
        bot.sendMessage(tid[0], "봇이 다시 실행 되었습니다!\n"
                                "유익한 뉴스를 다시 제공해 드리겠습니다~~!!\n"
                                "사용법이 궁금하시다면 /help 를 입력해주세요!!")
    except telepot.exception.BotWasBlockedError:
        print("err", end = ' ')
        print(tid[0])
        sql_temp = "DELETE FROM `user` WHERE `usnum` = " + str(tid[0])
        cursor.execute(sql_temp)
        save_log(sql)
        conn.commit()
        time.sleep(100)
conn.close()
while True:     # 뉴스 크롤링 파트
    crawl_invest(str_url)
    crawl_naver()
    for_the_first = 1
