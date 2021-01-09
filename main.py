# -*- coding: utf-8 -*-

import time

import psutil
import telepot
from telepot.loop import MessageLoop
from urllib.request import Request, urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pymysql
import signal
import sys
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import ChatAction
import os


def save_log(log_msg):
    date = str(datetime.today().year) + '-' + str(datetime.today().month) + '-' + str(datetime.today().day)
    path = './log/'
    file_name = path + 'log(' + date + ').txt'
    log_file = open(file_name, "a", encoding="UTF8")
    log_file.write(time.asctime())
    log_file.write(': ')
    log_file.write(log_msg)
    log_file.write('\n')
    log_file.close()


def save_improve(improve_msg):
    date = str(datetime.today().year) + '-' + str(datetime.today().month) + '-' + str(datetime.today().day)
    path = './improve/'
    file_name = path + 'message(' + date + ').txt'
    # print(file_name)
    person_name = improve_msg.message.chat.first_name + ' ' + improve_msg.message.chat.last_name\
                  + '(' + str(improve_msg.message.chat.id) + '): '
    # print(improve_msg['chat']['id'])
    log_file = open(file_name, "a", encoding="UTF8")
    log_file.write(time.asctime())
    log_file.write('\n')
    log_file.write(person_name)
    log_file.write(improve_msg.message.text)
    log_file.write('\n\n')
    log_file.close()


def signal_handler(sig, frame):
    global count_err_msg, ttocken
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.kill(pid, signal.SIGKILL)
    if pid != 0 and count_err_msg == 0:
        # os.kill(pid)
        count_err_msg = 1
        print('SIGINT')
        save_log('SIGINT')
        conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
        cursor = conn.cursor()
        sql = "SELECT `usnum` FROM `user` WHERE `investKR_news` = 1 or 'naver_news' = 1"
        cursor.execute(sql)
        save_log(sql)
        test = cursor.fetchall()
        for tid in test:
            updater.bot.send_message(
                chat_id=tid[0],
                text='봇이 정지 되었습니다!!!\n금방 다시 실행되겠습니다~~!',
            )
        conn.close()
    os._exit(0)


def crawl_invest(str0):
    global count_invest_err, admin_id, count_popular, db_port, db_name, db_user, db_ip, db_pw, ttocken
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
                    count_popular = 500
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
                # print('test\n\n\n')
                for tid in test:
                    # bot_origin.sendMessage(tid[0], msg)
                    updater.bot.send_message(
                        chat_id=tid[0],
                        text=msg,
                    )
                conn.close()

        time.sleep(60)
    except ValueError:
        count_invest_err += 1
        print("error" + str(count_invest_err))
        if count_invest_err >= 500:
            print("err")
            updater.bot.send_message(
                chat_id=admin_id,
                text="[" + time.asctime() + "]\n" + 'kr.investing 크롤링 부분에 문제가 발생 했습니다.',
            )
            count_invest_err = 0
        time.sleep(10)


def crawl_naver():
    global count_naver_err, admin_id, count_naver, db_port, db_name, db_user, db_ip, db_pw, ttocken
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
                    count_naver = 500
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
                    # bot_origin.sendMessage(tid[0], msg)
                    updater.bot.send_message(
                        chat_id=tid[0],
                        text=msg,
                    )
                conn.close()
    except:
        count_naver_err += 1
        print("error" + str(count_naver))
        if count_naver_err >= 500:
            print("err")
            updater.bot.send_message(
                chat_id=admin_id,
                text="[" + time.asctime() + "]\n" + '네이버 크롤링 부분에 문제가 발생 했습니다.',
            )
            count_naver_err = 0
        time.sleep(10)


def crawl_individual_kr():
    global count_individual_kr_err, admin_id, count_individual_kr, db_port, db_name, db_user, db_ip, db_pw
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `kr_stock_id` WHERE 1;"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    for sid in row:
        try:
            cursor = conn.cursor()
            sql = "SELECT `usnum` FROM `kr_subs` WHERE `krStockID` = " + sid[0]
            cursor.execute(sql)
            save_log(sql)
            user_list = cursor.fetchall()
            if len(user_list) == 0:     # 아무도 구독하지 않은 주식이면
                cursor = conn.cursor()
                sql = "DELETE FROM `kr_stock_id` WHERE `krStockID` = " + sid[0]
                cursor.execute(sql)  # 데베에서 삭제
                save_log(sql)
                conn.commit()
            individual_url = 'https://kr.investing.com' + sid[1] + '-news'
            req = Request(individual_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            html = urlopen(req).read()
            soup = BeautifulSoup(html, "html.parser")
            stock_name = soup.find(class_='float_lang_base_1 relativeAttr').text.strip()
            soup = soup.find_all(class_="mediumTitle1")[1]
            soup = soup.find_all(class_='textDiv')
            for article in soup:
                title = article.find('a').text
                href = article.find('a')['href']
                if 'https://' not in href:
                    href = 'https://kr.investing.com/' + href
                if href not in queue_individual_kr:
                    count_individual_kr += 1
                    if count_individual_kr > 1000000:
                        count_individual_kr = 500000
                        for i in range(500000):
                            del queue_naver[0]
                    queue_individual_kr.append(href)
                    msg = "\n[" + stock_name + " 뉴스" + "]\n" + title + "\n" + href
                    if for_the_first == 0:
                        continue
                    for user_usnum in user_list:
                        updater.bot.send_message(
                            chat_id=user_usnum[0],
                            text=msg,
                        )
        except ValueError:
            count_individual_kr_err += 1
            print("error" + str(count_naver))
            if count_individual_kr_err >= 500:
                print("err")
                updater.bot.send_message(
                    chat_id=admin_id,
                    text="[" + time.asctime() + "]\n" + '개인 주식 크롤링 부분에 문제가 발생 했습니다.',
                )
                count_naver_err = 0
            time.sleep(10)
    time.sleep(10)


def start_command(update, context):
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `user` where usnum = " + str(update.effective_user.id) + ";"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()

    context.bot.send_message(chat_id=update.effective_chat.id, text=start_str)
    user = update.message.from_user
    if len(row) == 0:
        cursor = conn.cursor()
        sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" \
              + str(update.effective_chat.id) + \
              ", '" + user['first_name'] + " " + user['last_name'] + "', 0, 0);"
        cursor.execute(sql)  # 데베에 유저 정보 등록
        save_log(sql)
        conn.commit()
    conn.close()


def cmd_task_buttons(update, context):
    task_buttons = [[InlineKeyboardButton('국내 뉴스 구독', callback_data=1),
                     InlineKeyboardButton('국내 뉴스 구독 해제', callback_data=2)],
                    [InlineKeyboardButton('국제 뉴스 구독', callback_data=3),
                     InlineKeyboardButton('국제 뉴스 구독 해제', callback_data=4)],
                    [InlineKeyboardButton('국내 개별 종목 뉴스 구독', callback_data=5),
                     InlineKeyboardButton('국내 개별 종목 뉴스 구독 해제', callback_data=6)],
                    [InlineKeyboardButton('개발자에게 건의사항', callback_data=7)]]
    reply_markup = InlineKeyboardMarkup(task_buttons)
    try:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='아래 작업중 하나를 선택해 주세요!!',
            reply_markup=reply_markup
        )
    except:
        pass


def cb_button(update, context):
    global improve_msg, dev_message_id, kr_stock_message_id
    # database setting
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `user` where usnum = " + str(update.effective_user.id) + ";"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()

    query = update.callback_query
    data = query.data
    context.bot.send_chat_action(
        chat_id=update.effective_user.id,
        action=ChatAction.TYPING
    )
    if data == '1':  # 네이버 뉴스 구독
        if len(row) == 0:  # 데베에 등록되어 있지 않다면
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" \
                  + str(update.effective_user.id) + \
                  ", '" + query['chat']['first_name'] + " " + query['chat']['last_name'] + "', 0, 1);"
            cursor.execute(sql)  # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()
            context.bot.edit_message_text(
                text='네이버 뉴스가 구독 되었습니다!',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
        elif len(row) != 0:  # 데베에 데이터가 있다면
            cursor = conn.cursor()
            sql = "SELECT `naver_news` FROM `user` WHERE `usnum` = " + str(update.effective_user.id)
            cursor.execute(sql)  # 데베에 등
            save_log(sql)
            test = cursor.fetchone()
            if test[0] == 0:
                cursor = conn.cursor()
                sql = "UPDATE user SET `naver_news` = 1 WHERE `usnum` = " + str(update.effective_user.id)
                cursor.execute(sql)  # 데베에 가입 등록
                save_log(sql)
                conn.commit()
                context.bot.edit_message_text(
                    text='네이버 뉴스가 구독 되었습니다!',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
            else:
                context.bot.edit_message_text(
                    text='네이버 뉴스가 이미 구독중입니다!',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
    elif data == '2':  # 네이버 뉴스 구독 해제
        cursor = conn.cursor()
        sql = "SELECT `naver_news` FROM `user` WHERE `usnum` = " + str(update.effective_user.id)
        cursor.execute(sql)  # 데베에 등
        save_log(sql)
        test = cursor.fetchone()
        if test[0] == 0:
            context.bot.edit_message_text(
                text='네이버 뉴스를  구독중이 아니십니다!',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
            return
        cursor = conn.cursor()
        sql = "UPDATE user SET `naver_news` = 0 WHERE `usnum` = " + str(update.effective_user.id)
        cursor.execute(sql)  # 데베에 가입 등록
        save_log(sql)
        conn.commit()
        context.bot.edit_message_text(
            text='네이버 뉴스가 구독해제 되었습니다!',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    elif data == '3':  # investing 뉴스 구독
        if len(row) == 0:  # 데베에 등록되어 있지 않다면
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" \
                  + str(update.effective_user.id) + \
                  ", '" + query['chat']['first_name'] + " " + query['chat']['last_name'] + "', 1, 0);"
            cursor.execute(sql)  # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()
            context.bot.edit_message_text(
                text='investing.kr 뉴스가 구독 되었습니다!',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
        elif len(row) != 0:  # 데베에 데이터가 있다면
            cursor = conn.cursor()
            sql = "SELECT `investKR_news` FROM `user` WHERE `usnum` = " + str(update.effective_user.id)
            cursor.execute(sql)  # 데베에 등
            save_log(sql)
            test = cursor.fetchone()
            if test[0] == 0:
                cursor = conn.cursor()
                sql = "UPDATE user SET `investKR_news` = 1 WHERE `usnum` = " + str(update.effective_user.id)
                cursor.execute(sql)  # 데베에 가입 등록
                save_log(sql)
                conn.commit()
                context.bot.edit_message_text(
                    text='investing.kr 뉴스가 구독 되었습니다!',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
            else:
                context.bot.edit_message_text(
                    text='investing.kr 뉴스가 이미 구독중입니다!',
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
    elif data == '4':  # investing 뉴스 구독 해제
        cursor = conn.cursor()
        sql = "SELECT `investKR_news` FROM `user` WHERE `usnum` = " + str(update.effective_user.id)
        cursor.execute(sql)  # 데베에 등
        save_log(sql)
        test = cursor.fetchone()
        if test[0] == 0:
            context.bot.edit_message_text(
                text='investing.kr 뉴스가 구독중이 아니십니다!',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
            return
        cursor = conn.cursor()
        sql = "UPDATE user SET `investKR_news` = 0 WHERE `usnum` = " + str(update.effective_user.id)
        cursor.execute(sql)  # 데베에 가입 등록
        save_log(sql)
        conn.commit()
        context.bot.edit_message_text(
            text='investing.kr 뉴스가 구독해제 되었습니다!',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    elif data == '5':  # 단일 종목 구독
        context.bot.edit_message_text(
            text='구독 하려는 종목 이름이나 종목 코드를 입력해주세요...!',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        kr_stock_message_id.append(query.message.chat_id)
        # nspid = os.fork()
        # if nspid == 0:
    elif data == '6':  # 단일 종목 구독 해제
        context.bot.edit_message_text(
            text='구독 해제 하려는 종목 이름이나 종목 코드를 입력해주세요...!',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        kr_stock_delete_id.append(query.message.chat_id)
    elif data == '7':
        context.bot.edit_message_text(
            text='개발자에게 건의 사항이나 하고 싶은 말 있으시면 타이핑 해주시면 됩니다...!',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        dev_message_id.append(query.message.chat_id)
        # ppid = os.fork()
        # if ppid == 0:
        #     pass
    conn.close()


def get_message(update, context):  # 메세지 핸들링
    global improve_msg, dev_message_id, kr_stock_message_id, temp_stock_list
    query = update
    temp_msg = "여러개의 주식이 검색된었습니다.\n" \
               "아래중 하나로 다시 검색해 주세요.\n"
    # data = query.data
    if query.message.chat_id in dev_message_id:  # 개발자에게 하고픈 말 핸들링
        temp_pid = os.fork()
        if temp_pid == 0:
            # bot_alarm.sendMessage(admin_id, update.message.text)
            save_improve(update)
            os._exit(0)
            print('not_exit\n\n\n\n\n')
        dev_message_id.remove(query.message.chat_id)
    elif query.message.chat_id in kr_stock_message_id:  # 국내 주식 삽입 검색
        ppid = os.fork()
        if ppid == 0:
            user_stock_input = update.message.text
            if user_stock_input.isdigit():   # 입력이 종목 코드일때
                temp_stock_list = get_stock_id(user_stock_input)
                href = temp_stock_list[0]['href']
                if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                    context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text='검색하신 주식 항목이 없습니다.',
                    )
                elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                    if insert_kr_stock(user_stock_input, href, update) == -1:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='이미 구독중인 주식 종목 입니다.'
                        )
                    else:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='종목코드(' + user_stock_input + ") 관련 뉴스가 구독 되었습니다."
                        )
            else:   # 입력이 종목 이름일때
                temp_stock_list = get_stock_id(user_stock_input)
                # print(stock_list)
                if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                    temp_name = get_similar_stock_id(user_stock_input)
                    if temp_name == 'None':
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='검색하신 주식 항목이 없습니다.',
                        )
                    else:
                        sim_msg = "혹시 검색하신 주식이 '"
                        sim_msg += temp_name
                        sim_msg += "' 아닌가요?\n 위에 결과로 검색해도 나오지 않는다면 \n" \
                                   "종목 코드로 검색 부탁 드립니다"
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text=sim_msg,
                        )
                elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                    stock_number = temp_stock_list[0].find(class_='second').text
                    href = temp_stock_list[0]['href']
                    if insert_kr_stock(stock_number, href, update) == -1:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='이미 구독중인 주식 종목 입니다.'
                        )
                    else:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='종목코드(' + stock_number + ") 관련 뉴스가 구독 되었습니다."
                        )
                else:
                    for i in range(len(temp_stock_list)):
                        temp_msg += '   - '
                        temp_msg += temp_stock_list[i].find(class_='second').text
                        temp_msg += ' / '
                        temp_msg += temp_stock_list[i].find(class_='third').text
                        temp_msg += ' / '
                        temp_msg += temp_stock_list[i].find(class_='fourth').text
                        temp_msg += '\n'
                    context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=temp_msg,
                    )
            os._exit(0)
            print('not_exit\n\n\n\n\n')
        kr_stock_message_id.remove(query.message.chat_id)
    elif query.message.chat_id in kr_stock_delete_id:  # 국내 주식 삭제 검색
        ppid = os.fork()
        if ppid == 0:
            user_stock_input = update.message.text
            if user_stock_input.isdigit():  # 입력이 종목 코드일때
                temp_stock_list = get_stock_id(user_stock_input)
                if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                    context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text='검색하신 주식 항목이 없습니다.',
                    )
                elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                    if delete_kr_stock(user_stock_input, update) == -1:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='구독중이 아닌 주식 종목 입니다.'
                        )
                    else:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='종목코드(' + user_stock_input + ") 관련 뉴스가 구독 해제 되었습니다."
                        )
            else:  # 입력이 종목 이름일때
                temp_stock_list = get_stock_id(user_stock_input)
                # print(stock_list)
                if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                    temp_name = get_similar_stock_id(user_stock_input)
                    if temp_name == 'None':
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='검색하신 주식 항목이 없습니다.',
                        )
                    else:
                        sim_msg = "혹시 검색하신 주식이 '"
                        sim_msg += temp_name
                        sim_msg += "' 아닌가요?\n 위에 결과로 검색해도 나오지 않는다면 \n" \
                                   "종목 코드로 검색 부탁 드립니다"
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text=sim_msg,
                        )
                elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                    stock_number = temp_stock_list[0].find(class_='second').text
                    if delete_kr_stock(stock_number, update) == -1:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='구독중이 아닌 주식 종목 입니다.'
                        )
                    else:
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='종목코드(' + user_stock_input + ") 관련 뉴스가 구독 해제 되었습니다."
                        )
                else:
                    for i in range(len(temp_stock_list)):
                        temp_msg += '   - '
                        temp_msg += temp_stock_list[i].find(class_='second').text
                        temp_msg += ' / '
                        temp_msg += temp_stock_list[i].find(class_='third').text
                        temp_msg += '\t/\t'
                        temp_msg += temp_stock_list[i].find(class_='fourth').text
                        temp_msg += '\n'
                    context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=temp_msg,
                    )
            os._exit(0)
            print('not_exit\n\n\n\n\n')
        kr_stock_delete_id.remove(query.message.chat_id)


def insert_kr_stock(user_stock_input, href, update):
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw,
                           database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `kr_stock_id` WHERE `krStockID` = '" \
          + user_stock_input + "';"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    if len(row) == 0:  # db에 주식 데이터 없을시
        cursor = conn.cursor()
        sql = "INSERT INTO `kr_stock_id`(`krStockID`, `href`) VALUES ('" + user_stock_input + "', '" \
              + href + "');"
        cursor.execute(sql)  # 데베에 주식 정보 등록
        save_log(sql)
        conn.commit()
    cursor = conn.cursor()
    sql = "SELECT * FROM `kr_subs` WHERE `usnum` = '" \
          + str(update.message.chat_id) + "' and `krStockID` = " + user_stock_input + ";"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    if len(row) == 0:   # db에 사용자가 주식 정보 등록 안했을 때
        cursor = conn.cursor()
        sql = "INSERT INTO `kr_subs`(`usnum`, `krStockID`) VALUES ('" + str(update.message.chat_id) \
              + "', '" + user_stock_input + "');"
        cursor.execute(sql)  # 데베에 유저, 주식 정보 등록
        save_log(sql)
        conn.commit()
        conn.close()
        return 0
    else:
        conn.close()
        return -1


def delete_kr_stock(user_stock_input, update):
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw,
                           database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `kr_subs` WHERE `krStockID` = '" \
          + user_stock_input + "' and `usnum` = '" + str(update.message.chat_id) + "';"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    if len(row) == 0:  # db에 주식 데이터 없을시
        return -1
    cursor = conn.cursor()
    sql = "DELETE FROM `kr_subs` WHERE `krStockID` = '" + user_stock_input\
          + "' and `usnum` = '" + str(update.message.chat_id) + "';"
    cursor.execute(sql)
    save_log(sql)
    conn.commit()
    return 0


def get_stock_id(value):
    cn = 0
    encode_kr = urllib.parse.quote_plus(value)
    req = Request(base_encode_url + encode_kr)
    req.add_header('User-Agent', 'Mozilla/5.0')
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    soup = soup.find_all(class_='js-inner-all-results-quote-item row')
    return soup
    # soup = soup.find(class_="t_nm")
    # print(soup)


def get_similar_stock_id(value):
    cn = 0
    encode_kr = urllib.parse.quote_plus(value)
    req = Request(base_simillar_usrl + encode_kr)
    req.add_header('User-Agent', 'Mozilla/5.0')
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    try:
        soup = soup.find(class_='sp_company sc_new _au_company_search _au_company_answer')
        soup = soup.find(class_='main_title').text
        return soup
    except:
        return 'None'


# main
str_url = "https://kr.investing.com/news/most-popular-news"
base_invest_url = "https://kr.investing.com/"
base_naver_url = "https://finance.naver.com"
base_encode_url = "https://kr.investing.com/search/?q="
base_simillar_usrl = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query="

start_str = "안녕하세요 채팅봇 베타 버전입니다!!!\n" \
            "/tasks 명령어를 통해서 다양한 기능을 사용하실 수 있습니다."

help_str = "안녕하세요 채팅봇 베타 버전입니다!!!\n" \
           "현재 사용 가능한 기능은 아래와 같습니다~\n" \
           "추가로 있었으면 하는 기능이나 문제점을 발견시\n" \
           "말씀해 주시면 감사하겠습니다!!!\n" \
           "개발자에게 메세지를 보내시고 싶으시면 채팅 치듯이 보내주시면 됩니다!!\n" \
           "invest.kr 인기 뉴스 구독 하기: /Subscribe_investKR_News\n" \
           "invest.kr 인기 뉴스 구독해제 하기: /Unsubscribe_investKR_News\n" \
           "Naver 인기 뉴스 구독 하기: /Subscribe_Naver_News\n" \
           "Naver 인기 뉴스 구독해제 하기: /Unsubscribe_Naver_News"

token_file = open("token_data.txt", "r", encoding="UTF8")
id_file = open("id_data.txt", "r", encoding="UTF8")
db_file = open("db_data.txt", "r", encoding="UTF8")
my_token = token_file.readline()
my_token = my_token[1:len(my_token) - 1]
test_token = token_file.readline()
test_token = test_token[:len(test_token) - 1]
alarm_token = token_file.readline()
admin_id = id_file.readline()
admin_id = admin_id[1:]
db_ip = db_file.readline()
db_ip = db_ip[:len(db_ip) - 1]
db_user = db_file.readline()
db_user = db_user[:len(db_user) - 1]
db_pw = db_file.readline()
db_pw = db_pw[:len(db_pw) - 1]
db_name = db_file.readline()
db_name = db_name[:len(db_name) - 1]
db_port = db_file.readline()
db_port = int(db_port)
token_file.close()
id_file.close()
db_file.close()

tele_id = []

temp_stock_list = []  # 주식 검색 결과 리스트
dev_message_id = []  # 메시지 전달 id
kr_stock_message_id = []  # 주식 입력 번호 전달 id
kr_stock_delete_id = []  # 주식 삭제 번호 전달 id
improve_check = 0
improve_msg = ""
for_the_first = 0
count_err_msg = 0
count_naver = 0
count_popular = 0
count_individual_kr = 0
count_invest_err = 0  # invest error 횟수
count_naver_err = 0  # naver error 횟수
count_individual_kr_err = 0  # individual error 횟수
queue_popular = []
queue_naver = []
queue_individual_kr = []

signal.signal(signal.SIGINT, signal_handler)

# ttocken = my_token    # for real
ttocken = test_token  # for test

updater = Updater(token=test_token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start_command)
task_buttons_handler = CommandHandler('tasks', cmd_task_buttons)
button_callback_handler = CallbackQueryHandler(cb_button)
message_handler = MessageHandler(Filters.text, get_message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(task_buttons_handler)
dispatcher.add_handler(button_callback_handler)
dispatcher.add_handler(message_handler)

parent_pid = os.getpid()
pid = os.fork()
# pid = 1
if pid == 0:  # parent
    updater.start_polling(timeout=3, clean=True)
    updater.idle()
    exit(0)
elif pid != 0:  # child
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT `usnum` FROM `user` WHERE `investKR_news` = 1 or 'naver_news' = 1"
    cursor.execute(sql)
    save_log(sql)
    test = cursor.fetchall()
    # for tid in test:
    #     try:
    #         bot.sendMessage(tid[0], "봇이 다시 실행 되었습니다!\n"
    #                                 "유익한 뉴스를 다시 제공해 드리겠습니다~~!!\n"
    #                                 "사용법이 궁금하시다면 /help 를 입력해주세요!!")
    #     except telepot.exception.BotWasBlockedError:
    #         print("err", end=' ')
    #         print(tid[0])
    #         sql_temp = "DELETE FROM `user` WHERE `usnum` = " + str(tid[0])
    #         cursor.execute(sql_temp)
    #         save_log(sql)
    #         conn.commit()
    #         time.sleep(100)
    conn.close()
    # for_the_first = 1
    while True:  # 뉴스 크롤링 파트
        crawl_individual_kr()
        crawl_invest(str_url)
        crawl_naver()
        for_the_first = 1
