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
import telegram
import os
import http.client


from news_compare import compare_title, sub_special, morph_and_stopword


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


def save_err_log(log_msg):
    date = str(datetime.today().year) + '-' + str(datetime.today().month) + '-' + str(datetime.today().day)
    path = './err_log/'
    file_name = path + 'log(' + date + ').txt'
    log_file = open(file_name, "a", encoding="UTF8")
    log_file.write(time.asctime())
    log_file.write(': ')
    log_file.write(str(log_msg))
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

    if pid != 0 and count_err_msg == 0:
        # os.kill(pid)
        os.kill(pid, signal.SIGKILL)
        os.wait()
        count_err_msg = 1
        print('\nSIGINT')
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
    # print("invest")
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
            compare_num = compare_title(queue_popular, topic)
            if compare_num < 0.5:
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
                    # print(tid[0])
                    # bot_origin.sendMessage(tid[0], msg)
                    updater.bot.send_message(
                        chat_id=tid[0],
                        text=msg,
                    )
                conn.close()

        time.sleep(60)
    except ValueError as err_msg:
        count_invest_err += 1
        save_err_log(err_msg)
        print("error" + str(count_invest_err))
        if count_invest_err >= 500:
            print("err")
            updater.bot.send_message(
                chat_id=admin_id,
                text="[" + time.asctime() + "]\n" + 'kr.investing 크롤링 부분에 문제가 발생 했습니다.',
            )
            count_invest_err = 0
        time.sleep(10)
    except urllib.error.URLError as err_msg:
        count_invest_err += 1
        save_err_log(err_msg)
        print("error" + str(count_invest_err))
        if count_invest_err >= 500:
            print("err")
            updater.bot.send_message(
                chat_id=admin_id,
                text="[" + time.asctime() + "]\n" + 'kr.investing 크롤링 부분에 문제가 발생 했습니다.',
            )
            count_invest_err = 0
        time.sleep(10)
    except http.client.IncompleteRead as err_msg:
        count_invest_err += 1
        save_err_log(err_msg)
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
    # print("naver")
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
            compare_num = compare_title(queue_naver, topic)
            if compare_num < 0.5:
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
    global count_individual_kr_err, admin_id, count_individual_kr, db_port, db_name, db_user, db_ip, db_pw,\
        check_individual, temp_individual_list
    # print('individual')
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT * FROM `kr_stock_id` WHERE 1;"
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    for sid in row:
        if sid[0] not in temp_individual_list:
            check_individual[sid[0]] = 0
            temp_individual_list.append(sid[0])
    for sid in row:
        try:
            cursor = conn.cursor()
            sql = "SELECT `usnum` FROM `kr_subs` WHERE `krStockID` = '" + sid[0] + "'"
            cursor.execute(sql)
            save_log(sql)
            user_list = cursor.fetchall()
            if len(user_list) == 0:     # 아무도 구독하지 않은 주식이면
                time.sleep(2)
                cursor = conn.cursor()
                sql = "SELECT `usnum` FROM `kr_subs` WHERE `krStockID` = '" + sid[0] + "'"
                cursor.execute(sql)
                save_log(sql)
                user_list = cursor.fetchall()
                if len(user_list) == 0:
                    cursor = conn.cursor()
                    sql = "DELETE FROM `kr_stock_id` WHERE `krStockID` = '" + sid[0] + "'"
                    cursor.execute(sql)  # 데베에서 삭제
                    save_log(sql)
                    conn.commit()
                    pass
            encode_kr = urllib.parse.quote_plus(sid[1])
            individual_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + encode_kr
            req = Request(individual_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            html = urlopen(req).read()
            soup = BeautifulSoup(html, "html.parser")
            soup = soup.find(class_='list_news')
            soup = soup.find_all(class_='news_tit')
            for news in soup:
                title = news['title']
                href = news['href']
                compare_num = compare_title(queue_individual_kr, title)
                # print(title + str(compare_num))
                # time.sleep(1)
                if compare_num < 0.5:
                    count_individual_kr += 1
                    if count_individual_kr > 1000000:
                        count_individual_kr = 500000
                        for i in range(500000):
                            del queue_individual_kr[0]
                    queue_individual_kr.append(title)
                    msg = "\n[" + sid[1] + " 뉴스" + "]\n" + title + "\n" + href
                    if check_individual[str(sid[0])] == 0:
                        continue
                    for user_usnum in user_list:
                        updater.bot.send_message(
                            chat_id=user_usnum[0],
                            text=msg,
                        )
            if check_individual[str(sid[0])] == 0:
                check_individual[str(sid[0])] = 1
        except :
            count_individual_kr_err += 1
            print("individual error" + str(count_individual_kr_err))
            if count_individual_kr_err >= 500:
                updater.bot.send_message(
                    chat_id=admin_id,
                    text="[" + time.asctime() + "]\n" + '개인 주식 크롤링 부분에 문제가 발생 했습니다.',
                )
                count_individual_kr_err = 0
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
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO user(usnum, usname, investKR_news, naver_news) VALUES (" \
                  + str(update.effective_chat.id) + \
                  ", '" + user['first_name'] + " " + user['last_name'] + "', 0, 0);"
            cursor.execute(sql)  # 데베에 유저 정보 등록
            save_log(sql)
            conn.commit()
        except TypeError as errname:
            save_err_log(errname + "\n" + sql)
            updater.bot.send_message(
                chat_id=admin_id,
                text="[" + time.asctime() + "]\n" + 'start 커맨드에 문제가 발생했습니다.',
            )
    conn.close()


def help_command(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=help_str,
    )


def cmd_task_buttons(update, context):
    task_buttons = [[InlineKeyboardButton('국내 뉴스 구독', callback_data=1),
                     InlineKeyboardButton('국내 뉴스 구독 해제', callback_data=2)],
                    [InlineKeyboardButton('국제 뉴스 구독', callback_data=3),
                     InlineKeyboardButton('국제 뉴스 구독 해제', callback_data=4)],
                    [InlineKeyboardButton('국내 개별 종목 뉴스 구독', callback_data=5),
                     InlineKeyboardButton('국내 개별 종목 뉴스 구독 해제', callback_data=6)],
                    [InlineKeyboardButton('구독중인 종목 보기', callback_data=7)],
                    [InlineKeyboardButton('개발자에게 건의사항', callback_data=8)]]
    reply_markup = InlineKeyboardMarkup(task_buttons)
    try:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='아래 작업중 하나를 선택해 주세요!!',
            reply_markup=reply_markup
        )
    except:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='아래 작업중 하나를 선택해 주세요!!',
            reply_markup=reply_markup
        )
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
    try:
        context.bot.send_chat_action(
            chat_id=update.effective_user.id,
            action=ChatAction.TYPING
        )
    except:
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
            text='구독 하려는 종목 이름이나 종목 코드를 입력해주세요.',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        kr_stock_message_id.append(query.message.chat_id)
    elif data == '6':  # 단일 종목 구독 해제
        context.bot.edit_message_text(
            text='구독 해제 하려는 종목 이름이나 종목 코드를 입력해주세요.',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        kr_stock_delete_id.append(query.message.chat_id)
    elif data == '7':  # 구독중인 뉴스 종목 표시
        sub_stock_list = get_personal_sub(query)
        temp_msg = "현재 구독 중이신 종목\n"
        if len(sub_stock_list) == 0:
            context.bot.edit_message_text(
                text='현제 구독 중이신 종목이 없습니다.',
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
            return
        for sid in sub_stock_list:
            temp_msg += '  - ' + sid[2] + '\n'
        context.bot.edit_message_text(
            text=temp_msg,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
    elif data == '8':
        context.bot.edit_message_text(
            text='개발자에게 건의 사항이나 하고 싶은 말 있으시면 타이핑 해주시면 됩니다.',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        dev_message_id.append(query.message.chat_id)
    conn.close()


def get_message(update, context):  # 메세지 핸들링
    global improve_msg, dev_message_id, kr_stock_message_id, temp_stock_list
    query = update
    temp_msg = "여러개의 주식이 검색되었습니다.\n" \
               "아래중 하나로 다시 검색해 주세요.\n"
    # data = query.data
    if query.message.chat_id in dev_message_id:  # 개발자에게 하고픈 말 핸들링
        temp_pid = os.fork()
        if temp_pid == 0:
            save_improve(update)
            os._exit(0)
            print('not_exit\n\n\n\n\n')
        else:
            os.wait()
        dev_message_id.remove(query.message.chat_id)
    elif query.message.chat_id in kr_stock_message_id:  # 국내 주식 삽입 검색
        ppid = os.fork()
        if ppid == 0:
            text_info = context.bot.send_message(
                chat_id=update.message.chat_id,
                text='잠시만 기다려주세요...',
            )
            try:
                user_stock_input = update.message.text
                if user_stock_input.isdigit():  # 입력이 종목 코드일때
                    temp_stock_list = get_stock_id(user_stock_input)
                    href = temp_stock_list[0]['href']
                    stock_name = temp_stock_list[0].find(class_='third').text
                    if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                        context.bot.send_message(
                            chat_id=update.message.chat_id,
                            text='검색하신 주식 항목이 없습니다.',
                        )
                    elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                        if insert_kr_stock(user_stock_input, href, stock_name, update) == -1:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='이미 구독중인 주식 종목 입니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=temp_stock_list[0].find(class_='third').text + " 관련 뉴스가 구독 되었습니다.",
                                message_id=text_info.message_id
                            )
                else:  # 입력이 종목 이름일때
                    temp_stock_list = get_stock_id(user_stock_input)
                    # print(stock_list)
                    if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                        temp_name = get_similar_stock_id(user_stock_input)
                        if temp_name == 'None':
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='검색하신 주식 항목이 없습니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            sim_msg = "혹시 검색하신 주식이 '"
                            sim_msg += temp_name
                            sim_msg += "' 아닌가요?\n 위에 결과로 검색해도 나오지 않는다면 \n" \
                                       "종목 코드로 검색 부탁 드립니다"
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=sim_msg,
                                message_id=text_info.message_id
                            )
                    elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                        stock_number = temp_stock_list[0].find(class_='second').text
                        href = temp_stock_list[0]['href']
                        if insert_kr_stock(stock_number, href, user_stock_input, update) == -1:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='이미 구독중인 주식 종목 입니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=temp_stock_list[0].find(class_='third').text + " 관련 뉴스가 구독 되었습니다.",
                                message_id=text_info.message_id
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
                        context.bot.edit_message_text(
                            chat_id=update.message.chat_id,
                            text=temp_msg,
                            message_id=text_info.message_id
                        )
            except:
                context.bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    text='문제가 발생하였습니다. 다시 부탁드립니다.',
                    message_id=text_info.message_id
                )
            finally:
                os._exit(0)
                print('not_exit\n\n\n\n\n')
        else:
            print('add child = ' + str(ppid))
            # os.wait()
        kr_stock_message_id.remove(query.message.chat_id)
    elif query.message.chat_id in kr_stock_delete_id:  # 국내 주식 삭제 검색
        ppid = os.fork()
        if ppid == 0:
            try:
                text_info = context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='잠시만 기다려주세요...',
                )
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
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='구독중이 아닌 주식 종목 입니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=temp_stock_list[0].find(class_='third').text +
                                     " 관련 뉴스가 구독 해제 되었습니다.",
                                message_id=text_info.message_id
                            )
                else:  # 입력이 종목 이름일때
                    temp_stock_list = get_stock_id(user_stock_input)
                    # print(stock_list)
                    if len(temp_stock_list) == 0:  # 검색 결과가 없을 때
                        temp_name = get_similar_stock_id(user_stock_input)
                        if temp_name == 'None':
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='검색하신 주식 항목이 없습니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            sim_msg = "혹시 검색하신 주식이 '"
                            sim_msg += temp_name
                            sim_msg += "' 아닌가요?\n 위에 결과로 검색해도 나오지 않는다면 \n" \
                                       "종목 코드로 검색 부탁 드립니다"
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=sim_msg,
                                message_id=text_info.message_id
                            )
                    elif len(temp_stock_list) == 1:  # 검색 결과가 하나 일때
                        stock_number = temp_stock_list[0].find(class_='second').text
                        if delete_kr_stock(stock_number, update) == -1:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text='구독중이 아닌 주식 종목 입니다.',
                                message_id=text_info.message_id
                            )
                        else:
                            context.bot.edit_message_text(
                                chat_id=update.message.chat_id,
                                text=temp_stock_list[0].find(class_='third').text +
                                     " 관련 뉴스가 구독 해제 되었습니다.",
                                message_id=text_info.message_id
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
                        context.bot.edit_message_text(
                            chat_id=update.message.chat_id,
                            text=temp_msg,
                            message_id=text_info.message_id
                        )
            except :
                context.bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    text='문제가 발생하였습니다. 다시 부탁드립니다.',
                    message_id=text_info.message_id
                )
            finally:
                os._exit(0)
                print('not_exit\n\n\n\n\n')
        else:
            print('add child = ' + str(ppid))
            # os.wait()
        kr_stock_delete_id.remove(query.message.chat_id)


def insert_kr_stock(user_stock_input, href, stock_name, update):    # 종목번호, 주소, 이름, update
    global check_individual
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
        sql = "INSERT INTO `kr_stock_id`(`krStockID`, `stock_name`, `href`) VALUES ('" +\
              user_stock_input + "', '" + stock_name + "', '"+ href + "');"
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


def get_personal_sub(query):
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw,
                           database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT ks.usnum, ks.krStockID, ksid.stock_name FROM kr_subs AS ks JOIN kr_stock_id AS ksid ON " \
          "ksid.krStockID = ks.krStockID where usnum = " + str(query.message.chat.id)
    cursor.execute(sql)
    save_log(sql)
    row = cursor.fetchall()
    return row



# main
str_url = "https://kr.investing.com/news/most-popular-news"
base_invest_url = "https://kr.investing.com/"
base_naver_url = "https://finance.naver.com"
base_encode_url = "https://kr.investing.com/search/?q="
base_simillar_usrl = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query="

start_str = "안녕하세요 채팅봇 베타 버전입니다!!!\n" \
            "/tasks 명령어를 통해서 다양한 기능을 사용하실 수 있습니다.\n" \
            "사용법은 /help를 통해 보실수 있습니다."

help_str = "안녕하세요 채팅봇 베타 버전입니다!!!\n" \
           "다양한 기능을 사용하시고 싶으시면 /tasks를 입력해 주세요.\n" \
           "현재 사용 가능한 기능은 아래와 같습니다~\n" \
           "추가로 있었으면 하는 기능이나 문제점을 발견시\n" \
           "말씀해 주시면 감사하겠습니다!!!\n" \
           "국내 뉴스 구독: 국내 인기 주식 뉴스 구독\n" \
           "국내 뉴스 구독 해제: 국내 인기 주식 뉴스 구독 해제\n" \
           "국제 뉴스 구독: 국제 인기 주식 뉴스 구독\n" \
           "국제 뉴스 구독 해제: 국제 인기 주식 뉴스 구독 해제\n" \
           "국내 개별 종목 뉴스 구독: 원하시는 국내 종목 뉴스 구독\n" \
           "국내 개별 종목 뉴스 구독 해제: 원하시는 국내 종목 뉴스 구독 해제\n" \
           "개발자에게 건의사항: 개발자에게 건의하고 싶은 내용 메시지로 보내기"


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
check_individual = {}
temp_individual_list = []
temp_popular_list = []
temp_naver_list = []

signal.signal(signal.SIGINT, signal_handler)

ttocken = my_token    # for real
# ttocken = test_token  # for test

updater = Updater(token=ttocken, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start_command)
help_handler = CommandHandler('help', help_command)
task_buttons_handler = CommandHandler('tasks', cmd_task_buttons)
button_callback_handler = CallbackQueryHandler(cb_button)
message_handler = MessageHandler(Filters.text, get_message)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
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
    print('child = ' + str(pid))
    conn = pymysql.connect(host=db_ip, user=db_user, password=db_pw, database=db_name, port=db_port);
    cursor = conn.cursor()
    sql = "SELECT `krStockID` FROM `kr_stock_id` WHERE 1"
    cursor.execute(sql)
    save_log(sql)
    test = cursor.fetchall()
    for sid in test:
        check_individual[sid[0]] = 0
        temp_individual_list.append(sid[0])
    cursor = conn.cursor()
    sql = "SELECT * FROM `user` WHERE `investKR_news` = 1 or `naver_news` = 1"
    cursor.execute(sql)
    save_log(sql)
    test = cursor.fetchall()
    for tid in test:
        try:
            updater.bot.send_message(
                chat_id=tid[0],
                text="봇이 다시 실행 되었습니다!\n"
                     "유익한 뉴스를 다시 제공해 드리겠습니다~~!!\n"
                     "기능을 이용하시려면 /tasks 를 입력해주세요."
                     "사용법이 궁금하시다면 /help 를 입력해주세요!!",
            )
        except telepot.exception.BotWasBlockedError:
            print("err", end=' ')
            # print(tid[0])
            sql_temp = "DELETE FROM `user` WHERE `usnum` = " + str(tid[0])
            cursor.execute(sql_temp)
            save_log(sql)
            conn.commit()
            time.sleep(100)
        except telegram.error.Unauthorized:
            print("err", end=' ')
            # print(tid[0])
            sql_temp = "DELETE FROM `user` WHERE `usnum` = " + str(tid[0])
            cursor.execute(sql_temp)
            save_log(sql)
            conn.commit()
            time.sleep(100)

    # for_the_first = 1
    while True:  # 뉴스 크롤링 파트
        crawl_individual_kr()
        crawl_invest(str_url)
        crawl_naver()
        if for_the_first != 1 or queue_individual_kr_backup != queue_individual_kr:  # 새로운 뉴스 추가 되었을 때 or 처음일 때
            temp_title_list = []
            for title in queue_individual_kr:
                temp_title = sub_special(title)
                temp_title_list.append(morph_and_stopword(temp_title))
            queue_individual_kr_backup = queue_individual_kr
        if for_the_first != 1 or queue_popular_backup != queue_popular:  # 새로운 뉴스 추가 되었을 때 or 처음일 때
            temp_title_list = []
            for title in queue_popular:
                temp_title = sub_special(title)
                temp_title_list.append(morph_and_stopword(temp_title))
            queue_popular_backup = queue_popular
        if for_the_first != 1 or queue_naver_backup != queue_naver:  # 새로운 뉴스 추가 되었을 때 or 처음일 때
            temp_title_list = []
            for title in queue_naver:
                temp_title = sub_special(title)
                temp_title_list.append(morph_and_stopword(temp_title))
            queue_naver_backup = queue_naver
        for_the_first = 1
    conn.close()