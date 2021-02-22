# 탤레그램 뉴스 알림이

텔레그램을 통한 국내외 뉴스를 받아볼수 있는 텔레그램 봇을 만들었습니다. 또한 추가 사항으로 국내 주식은 개별 뉴스 소식을 받아 보실수 있습니다.

---
## 목차
- [업데이트 사항](#업데이트-사항)
- [사용된 언어 및 라이브러리](#사용된-언어-및-라이브러리)
- [사용법](#사용법)
- [코드 구성](#코드-구성)   
	- [main.py](#mainpy)   
	- [news_compare.py](#news_comparepy)  
---
## 업데이트 사항
- 개별 종목 뉴스중 비슷한 제목의 뉴스는 사용자에게 전달하지 않음
- 오래된 뉴스는 사용자에게 전달하지 않음
---
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
---
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
---
## 코드 구성
### main.py
#### SQL 로그 저장
```{.python}
def save_log(log_msg):
    date = 로그 발생시간
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 시간과 내용을 저장한다
    log_file 닫기
```
#### ERROR 로그 저장
```{.python}
def save_err_log(log_msg):
    date = 로그 발생 시간
    path = 로그 저장 위치
    file_name = 파일 저장 경로와 이름을 결합하다
    log_file = 로그파일 열기
    log_file에 로그 발생 시간과 내용을 저장한다
    log_file 닫기
```
#### 건의사항 저장
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
#### 시그널 핸들러
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
#### 국제 주식 뉴스 크롤링
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
#### 국내 주식 뉴스 크롤링
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
#### 국내 개별 주식 크롤링
```{.python}
def crawl_individual_kr():
    row = DB에서 현재 등록된 개별 주식 리스트 받아 저장
    for sid in row:
        try:
            user_list = 현재 sid 종목코드를 가진 주식을 구돈한 사람 정보
            if len(user_list) == 0:     # 아무도 구독하지 않은 주식이면
                해당 종목을 DB에서 삭제한다
            encode_kr = 종목 이름을 인코딩
            soup = 뉴스 리스트 크롤링
            for news in soup:
                title = 뉴스 제목
                href = 뉴스 링크
                compare_num = compare_title()	# 이전에 받아왔던 뉴스들과의 유사도 검사
                if compare_num < 0.5:
                    count_individual_kr += 1
                    if count_individual_kr > 1000000:
                        count_individual_kr = 500000
                        for i in range(500000):
                            queue_individual_kr를 메모리 관리를 위해 오래된 뉴스 정리
                    queue_individual_kr에 뉴스 제목 저장
                    for user_usnum in user_list:
                        user_usnum에 뉴스 전달
        except :
        	save_err_log()로 에러 메시지 저장
        	관리자에게 에러 발생을 메세지로 전송
```
#### start 명령어 핸들러
```{.python}
def start_command(update, context):
    row = start 명령어 보낸 사람 정보 DB에서 받아오기
    유저에게 환영 메시지및 명령어 사용법 메시지 보내기
    if start 명령어 보낸 유저가 DB에 등록되지 않았을 때:
        try:
            DB에 유저 정복 등록
        except TypeError as errname:
            save_err_log()로 에러 메시지 저장
        	관리자에게 에러 발생을 메세지로 전송
    conn.close()
```
#### help 명령어 핸들러
```{.python}
def help_command(update, context):
	help_str = 명령어 사용법 문자열
    유저에게 help_str 보내기
```
#### tasks 버튼
```{.python}
def cmd_task_buttons(update, context):
    task_buttons = 국내 뉴스 구독
                   국내 뉴스 구독 해제
                   국제 뉴스 구독
                   국제 뉴스 구독 해제
                   국내 개별 종목 뉴스 구독
                   국내 개별 종목 뉴스 구독 해제
                   구독중인 종목 보기
                   개발자에게 건의사항
    reply_markup = 사용자 입력 받을 변수
    사용자에게 task_buttons 보내 입력값 받기
```
#### cd 버튼
```{.python}
def cb_button(update, context):
    row = 버튼 입력한 유저 정보 DB에서 받아오기
    query = 사용자 버튼 입력 쿼리
    data = 쿼리에서 입력 받은 버튼 정보 추출
    try:
        사용자에게 입력중이라 표시
    except:
        사용자에게 입력중이라 표시
    if 국내 뉴스 구독:
        if DB에 등록되어 있지 않다면:
            DB에 유저 정보 등록
            sql 로그 저장
            사용자에게 구독 완료 메시지 보내기
        elif 데베에 데이터가 있다면:
            sql 로그 저장
            test = DB의 유저 정보에서 네이버 뉴스 구독 여부 확인
            if 미구독:
                DB에 있는 유저 정보 네이버 뉴스 구독 업데이트
            	sql 로그 저장
                유저에게 구독 되었다고 알림
            else:
                유저에게 이미 구독중이라고 알림
    elif 네이버 뉴스 구독 해제:
        test = 메시지 보낸 유저 정보 DB에서 받아오기
        if 네이버 뉴스 구독중이 아닐 때:
            유저에게 구독중이 아니라고 알림
            return
        DB에 해당 유저 네이버 뉴스 구독 해제 업데이트
        sql문 로그 저장
        유저에게 구독 해제 알림
    elif investing 뉴스 구독:
        if DB에 유저 정보가 등록되어 있지 않다면
            DB에 유저 정보 등록
            sql문 로그 저장
            유저에게 investing 뉴스 구독 알림
        elif 데베에 데이터가 있다면:
            sql문 로그 저장
            test = DB에 등록된 유저 정보 받아오기
            if 구독중이 아닐때:
                DB에 유저 정보 구독으로 업데이트
                sql문 로그 저장
                유저에게 investing.kr 뉴스 구독 알림
            else:
                유저에게 이미 investing 뉴스 구독중임을 알림
    elif investing 뉴스 구독 해제:
        sql문 로그 저장
        test = DB에서 유저 정보 받오기
        if 미구독:
            유저에게 investing.kr 뉴스 미구독중임을 알림
            return
        DB에 있는 유저 데이터 구독 해제 업데이트
        sql문 로그 저장
        유저에게 investing.kr 뉴스 구독 해제 알림
    elif 단일 종목 구독:
        유저에게 단일 종목 코드 혹은 이름 받기
        kr_stock_message_id에 유저 텔레그램 아이디 저장
    elif data == '6':  # 단일 종목 구독 해제
        유저에게 단일 종목 코드 혹은 이름 받기
        kr_stock_delete_id에 유저 텔레그램 아이디 저장
    elif data == '7':  # 구독중인 뉴스 종목 표시
        sub_stock_list = get_personal_sub(query)로 구독중인 종목 받기
        if 구독중인 종목이 없을 시:
            유저에게 구독중인 종목이 없다고 알림
            return
        유저에게 구독중인 종목 알림
    elif 개발자에게 건의하기:
        건의하고자하는 내용 받기
        dev_message_id에 유저 텔레그램 아이디 저장
```
#### 메시지 핸들링
```{.python}
def get_message(update, context):
    if 개발자에게 하고픈 말 핸들링:
        temp_pid = os.fork()로 자식 프로세스 생성
        if 자식프로세스:
            save_improve(update)로 메시지 저장
            프로세스 종료
        else:
            자식 프로세스 죽을때까지 대기
        dev_message_id에서 방금 핸들링한 유저 아이디 지우기
    elif 국내 개별 주식 삽입 검색:
        ppid = os.fork()로 자식 프로세스 생성
        if 자식프로세스:
            유저에게 잠시만 기다려 달라고 알림
            try:
                user_stock_input = 입력받은 문자열
                if 입력이 종목 코드일때:
                    temp_stock_list = get_stock_id(user_stock_input)로 주식 리스트 받기
                    href = 주식 뉴스 주소
                    stock_name = 주식 이름
                    if 검색 결과가 없을 때:
                        유저에게 검색한 주식이 없다고 알림
                    elif 검색 결과가 하나 일때:
                        if 이미 구독중인 주식이면:
                            유저에게 이미 구독중인 주식이라 알림
                        else:
                            유저에게 해당 종목 뉴스가 구독되었다고 알림
                elif 입력이 종목 이름일때:
                    temp_stock_list = get_stock_id(user_stock_input)로 주식 리스트 받아오기
                    if 검색 결과가 없을 때:
                        temp_name = get_similar_stock_id(user_stock_input)로 비슷한 이름의 주식을 받아옴
                        if 비슷한 이름의 주식이 없을때:
                            유저에게 검색한 주식을 찾을수 없다고 알림
                        else:
                            유저에게 비슷한 주식을 알려줌
                    elif 검색 결과가 하나 일때:
                        stock_number = 주식코드
                        href = 주식 이름
                        if 이미 구독중인 주식이면:
                            유저에게 이미 구독중인 주식임을 알림
                        else:
                            유저에게 해당 주식을 구독했다고 알림
                    else:
                        유저에게 검색 결과로 나온 주식들 리스트를 보냄
            except:
                유저에게 문제가 발생했음을 알림
            finally:
                프로세스를 종료
        else:
            print(자식 프로세스가 생성됬음을 표시)
        kr_stock_message_id에서 방금 핸들링한 유저 아이디를 삭제
    elif 국내 주식 삭제 검색:
        ppid = os.fork()로 자식 프로세스 생성
        if 자식 프로세스이면:
            try:
                유저에게 잠시만 기다려달라고 알림
                user_stock_input = 유저 입력을 받음
                if 입력이 종목 코드일때:
                    temp_stock_list = get_stock_id(user_stock_input)로 주식 리스트 받음
                    if 검색 결과가 없을 때:
                        유저에게 검색한 주식이 없다고 알림
                    elif 검색 결과가 하나 일때:
                        if 구독중인 종목이 아닐 때:
                            유저에게 현재 구독중인 종목이 아니라고 알림
                        else:
                            유저에게 해당 종목을 구독 해제했음을 알림
                elif 입력이 종목 이름일때:
                    temp_stock_list = get_stock_id(user_stock_input)로 주식 리스트 받음
                    if 검색 결과가 없을 때:
                        temp_name = get_similar_stock_id(user_stock_input)로 비슷한 이름의 종목을 받음
                        if 비슷한 이름의 종목이 없을 때:
                            유저에게 검색한 종목이 없음을 알림
                        else:
                            유저에게 비슷한 이름의 종목을 알림
                    elif 검색 결과가 하나 일때:
                        stock_number = 종목코드를 크롤링
                        if 구독중인 종목이 아닐때:
                            유저에게 현제 구독중인 종목이 아님을 알림
                        else:
                           유저에게 해당 종목 관련 뉴스를 구독 해제 했음을 알림
                    else:
                        유저에게 검색 결과로 나온 주식들 리스트를 보냄
            except :
                유저에게 문제가 발생했음을 알림
            finally:
                프로세스를 종료
        else:
            print(자식 프로세스가 생성됬음을 표시)
        kr_stock_delete_id에서 방금 핸들링한 유저 아이디를 삭제
```
#### 개별 한국 주식 구독
```{.python}
def insert_kr_stock(user_stock_input, href, stock_name, update):
    SQL문 로그 저장
    row = DB에 현재 등록하고자 하는 주식 있는지 받아오기
    if DB에 주식 데이터 없을시:
        DB에 주식 데이터 등록
        SQL문 로그 저장
    SQL문 로그 저장
    row = DB에서 사용자 주식 구독 정보 받아오기
    if DB에 사용자가 주식 정보 등록 안했을 때:
        DB에 유저 주식 구독 정보 등록
        SQL문 로그 저장
        return 0
    else:
        return -1로 이미 등록중임을 반환
```
#### 개별 한국 주식 구독 해제
```{.python}
def delete_kr_stock(user_stock_input, update):
    SQL문 로그 저장
    row = DB에 사용자가 개별 주식 구독중인지 데이터 받아오기
    if DB에 주식 데이터 없을시
        return -1로 DB에 주식 데이터 없음을 전달
    해당 유저의 개별 주식 구독 정보를 DB에서 삭제
    SQL문 로그 저장
    return 0
```
#### 주식 정보 웹사이트에서 받아오기
```{.python}
def get_stock_id(value):
    cn = 0
    encode_kr = 주식종목명 인코딩
    html = 주식정보 사이트에서 읽어오기
    soup = 읽어온 정보 파싱
    soup = 파싱된 정보중 주식 정보를 가진 데이터만 따로 저장
    return soup
```
#### 비슷한 이름의 주식 종목 이름 받아오기
```{.python}
def get_similar_stock_id(value):
    encode_kr = 종목명 인코딩
    html = 네이버에서 검색한 종목명으로 재검색
    soup = 읽어온 데이터 파싱
    try:
        soup = 파싱된 데이터중 주식 종목 데이터 저장
        return soup
    except:
        return 'None'으로 비슷한 데이터가 없을을 리턴
```
#### 구독중인 개별 주식 정보 받기
```{.python}
def get_personal_sub(query):
    SQL문 로그 저장
    row = DB에서 사용자가 구독중인 개별 주식 정보 받아오기
    return row
```
#### 메인함수
```{.python}
# main

token_file = 텔레그램 봇 토큰 값 저장 파일 열기
id_file = id 데이터 저장 파일 열기
db_file = db 데이터 저장 파일 열기
my_token = 텔레그램 봇 토큰
test_token = 텔레그램 테스트 봇 토큰
admin_id = 어드민 id
db_ip = DB ip 주소
db_user = DB 유저 id
db_pw = DB pw
db_name = Db 테이블 명
db_port = DB 접속 포트 번호

시그널 핸들러 등록

ttocken = 텔레그램 봇 토큰 등록

updater = 텔레그램 봇 업데이터 등록
dispatcher = 텔레그램 봇 디스패처 등록

start_handler = start 명령어 핸들러 등록
help_handler = help 명령어 핸들러 등록
task_buttons_handler = tasks 명령어 핸들러 등록
button_callback_handler = 버튼 입력 콜백 쿼리 핸들러
message_handler = 메시지 입력 핸들러

각 핸들러 봇에 등록

parent_pid = 현재 프로세서 pid 값
pid = os.fork()
# pid = 1
if 부모 프로세스:
    updater를 통해 메시지 입력 대기
    exit(0)
elif 자식 프로세스:
    SQL문 로그 저장
    test = DB에서 현재 서비스 이용중인 사용자 리스트 받기
    for sid in test:
        temp_individual_list에 사용자 리스트 추가
    SQL문 로그 저장
    test = 현재 국내외 뉴스 구독중인 사용자 리스트 받아오기
    for tid in test:
        try:
            사용자에게 프로그램이 실행되었음을 알려준다
        except telepot.exception.BotWasBlockedError:
            save_err_log()로 에러 메시지 저장
        	관리자에게 에러 발생을 메세지로 전송

    while True:  # 뉴스 크롤링 파트
        crawl_individual_kr()	# 국내 개별 뉴스 크롤링
        crawl_invest(str_url)	# 국제 뉴스 크롤링
        crawl_naver()		# 극내 뉴스 크롤링
        if 개별 뉴스 리스트에 새로운 뉴스 추가 되었을 때 or 처음일 때:
            temp_title_list = 백업 리스트 초기화
            for title in queue_individual_kr:
                temp_title = title에서 한글, 숫자, 영어 제외하고 전부 제거
                temp_title_list에 위의 작업한 제목 저장
            queue_individual_kr_backup = 백업리스트 저장
        if 국제 뉴스 리스트에 새로운 뉴스 추가 되었을 때 or 처음일 때:
            temp_title_list = 백업 리스트 초기화
            for title in queue_popular:
                temp_title = title에서 한글, 숫자, 영어 제외하고 전부 제거
                temp_title_list에 위의 작업한 제목 저장
            queue_popular_backup = 백업리스트 저장
        if 네이버 뉴스 리스트 새로운 뉴스 추가 되었을 때 or 처음일 때:
            temp_title_list = 백업 리스트 초기화
            for title in queue_naver:
                temp_title = title에서 한글, 숫자, 영어 제외하고 전부 제거
                temp_title_list에 위의 작업한 제목 저장
            queue_naver_backup = 백업리스트 저장
        for_the_first = 첫 실행이 아님을 저장
    conn.close()
```
---
### news_compare.py
#### 문장 불필요 요소 제거
```{.python}
def sub_special(s):  
    return 한글, 숫자, 영어 빼고 전부 제거
```
#### 문장 간렬화
```{.python}
def morph_and_stopword(s):
    STOP_WORDS = ['의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']
    tmp = 형태소 분석
    for token in tmp:  
        불용어 제거
    return temp_str
```
#### 최대값 찾기
```{.python}
def max_search(list_s):
    for i in list_s:
        현재 값이 최대값보다 크면 교체
    return maxValue
```
#### 구독중인 개별 주식 정보 받기
```{.python}
def compare_title(title_list, title_str):
    temp_title_list = 타이틀 리스트 저장
    one_title = 문장 간결화
    temp_title_list에 간결화된 문장 저장
    np_arr = 넘파이 어레이로 저장
    코사인 유사도를 이용하여 유사도 검사
    return 가장 유사도가 큰 값을 반환
```
