# 탤레그램 뉴스 알림이

텔레그램을 통한 국내외 뉴스를 받아볼수 있는 텔레그램 봇을 만들었습니다. 또한 추가 사항으로 국내 주식은 개별 뉴스 소식을 받아 보실수 있습니다.


## Table of Contents

- [사용된 언어 및 라이브러리](#사용된-언어-및-라이브러리)
- [사용법](#사용법)


## 사용된 언어 및 라이브러리

- python
	- telepot
	- urllib
	- bs4
	- pymysql
	- signal
	- tatetime
	- telegram
	- os
	- re
	- konlpy
	- sklearn
	- numpy
	
- mysql


## 사용법

해당 코드는 서버와의 연동이 필요하여 임의로 실행할 경우 정상적인 작동을 하지 않습니다.   
뉴스를 받아 보시려는 분들은 텔레그램에서 "@economic_help_bot"을 검색하여 사용하실수 있습니다.
![텔레그램](https://user-images.githubusercontent.com/49528515/106888319-bc92f600-6729-11eb-9204-d9a0238add8f.jpg)
![텔레그램 메뉴](https://user-images.githubusercontent.com/49528515/105572119-886a1d80-5d98-11eb-850c-68cf36b93ddd.PNG)

- 국내뉴스 구독   
	네이버 경제 뉴스 업데이트시 알림 받기
- 국제뉴스 구독   
	kr.investing의 경제 뉴스 업데이트시 알림 받기
- 개별 종목 뉴스 구독   
	국내 주식 개별 뉴스 업데이트시 알림 받기
- 구독중인 종목 보기   
	현재 내가 구독중인 개별 종목 보기
- 개발자에게 건의사항   
	개발자에게 건의하고 싶은 사항 보내기

## 코드 구성
### SQL 로그 저장
```{.python}
def save_log(log_msg):
    date = 로그 발생시간
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 시간과 내용을 저장한다
    log_file 닫기
```
### ERROR 로그 저장
```{.python}
def save_err_log(log_msg):
    date = 로그 발생 시간
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 시간과 내용을 저장한다
    log_file 닫기
```
### 건의사항 저장
```{.python}
def save_improve(improve_msg):
    date = 건의 시간
    path = 파일 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    person_name = 건의한 사람 아이디
    log_file = 로그파일 열기
    log_file에 로그 발생 시간, 건의자와 내용을 저장한다
    log_file 닫기
```
### 시그널 핸들러
```{.python}
def signal_handler(sig, frame):
    SIGINT 무시하기
    if 자식 프로세스가 아니고 첫 실행이면:
		pid 프로세서 죽이고 죽을때 까지 기다리기
		log에 SIGINT 저장하기
        서비스 사용중인 사람들 리스트 DB에서 받아오기
        sql문 로그에 저장하기
        서비스 사용중인 사람들에게 프로그램 중지되었음을 안내
    프로그램 끝내기
```
### 국제 주식 뉴스 크롤링
```{.python}
def crawl_invest(str0):
    try:
        kr.investing 사이트에서 뉴스 목록든 soup 리스트 받아오기
        for row in soup:
            topic = 뉴스 제목
            link = 뉴스 링크
            compare_num = compare_title()	# 이전에 받아왔던 뉴스들과의 유사도 검사
            if compare_num < 0.5:
                queue_popular에 뉴스 제목 추가
                count_popular += 1
                if count_popular > 1000:
                    count_popular = 500
                    queue_popular를 메모리 관리를 위해 오래된 뉴스 정리
                해당 뉴스를 구독중인 사람 정보를 DB에서 받아오기
                sql을 로그에 저장
                구독중인 사람들에게 뉴스 정보를 보냄
    except ValueError as err_msg:
        save_err_log()로 에러 메시지 저장
        관리자에게 에러 발생을 메세지로 전송
    except urllib.error.URLError as err_msg:
        save_err_log()로 에러 메시지 저장
        관리자에게 에러 발생을 메세지로 전송
    except http.client.IncompleteRead as err_msg:
        save_err_log()로 에러 메시지 저장
        관리자에게 에러 발생을 메세지로 전송
```
### 국내 주식 뉴스 크롤링
```{.python}
def crawl_naver():
    try:
        finance.naver.com에서 뉴스 목록든 soup 리스트 받아오기
        for row in soup:
            topic = 뉴스 제목
            link = 뉴스 링크
            compare_num = compare_title()	# 이전에 받아왔던 뉴스들과의 유사도 검사
            if compare_num < 0.5:
                queue_naver에 뉴스 제목 추가
                count_naver += 1
                if count_naver > 1000:
                    count_naver = 500
                    for i in range(500):
                    	queue_naver를 메모리 관리를 위해 오래된 뉴스 정리
                해당 뉴스를 구독중인 사람 정보를 DB에서 받아오기
                sql을 로그에 저장
                구독중인 사람들에게 뉴스 정보를 보냄
    except:
        save_err_log()로 에러 메시지 저장
        관리자에게 에러 발생을 메세지로 전송
```
### 국내 개별 주식 크롤링
```{.python}
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
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```
```{.python}
def save_log(log_msg):
    date = 오늘 날짜 받기
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 기간과 내용을 저장한다
    log_file 닫기
```