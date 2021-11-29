# pymssql 패키지 import
# -*- coding: utf-8 -*-
import pymssql
 
# MSSQL 접속
# 테스트하는 본인 환경에 맞출것 (단, charset은 건드리면 한글 불가능)
conn = pymssql.connect(host=r"(local)", user='sa', password='1234', database='master', charset='UTF-8')
#conn = pymssql.connect(host=r"(local)", user='madanguser', password='madangpass', database='Madang', charset='UTF-8')
# Connection 으로부터 Cursor 생성
cursor = conn.cursor()

def menu():          # 메뉴 출력
    print("경기 도서관 도서 DB입니다. 원하는 메뉴를 선택하세요.")
    print("1. 책 랭킹")
    print("2. 책 평가")
    print("3. 책 검색")
    print("4. 책 등록")
    print("5. 책 삭제")
    print("6. 로그아웃")
    print("7. 책 대여하기")
    print("8. 책 대여현황")
    print("9. 책 소유 등록")
    print("0. 종료")

def register_menu(): # 가입or로그인 메뉴 출력
    print("계정이 없다면 회원가입을 진행해주세요.")
    print("0. 회원가입")
    print("1. 로그인")
    
def ranking():       # 랭킹 출력
    print("----------책 랭킹----------")
    cursor.execute("""SELECT AVG(Score),Book_ID FROM Evaluate GROUP BY Book_ID,Users_ID ORDER BY AVG(Score) DESC""") # 점수평균오름차순 정렬
    row=cursor.fetchall()
    if row: # 책이 하나라도 등록돼있으면
        i=0
        print("등수\t책이름\t점수")
        while row: # 책이름 점수평균 전부 출력
            if i>=len(row):
                break
            book_id_ranking=row[i][1] # Evalute테이블 i번째의 BookID
            cursor.execute("SELECT Book_Name FROM Book WHERE Book_ID=%d"%(book_id_ranking)) # Book_ID를 이용해 Book테이블에서 책이름 불러오기
            row_book_name=cursor.fetchone()
            print("%d등:\t%s\t%d"%(i+1,row_book_name[0],row[i][0])) # 등수 책이름 평균점수 출력
            i+=1
        input("계속하려면 엔터키를 누르세요...")
    else: # 등록된 책이 없으면
        print("등록된 책이 없습니다.")
        input("계속하려면 엔터키를 누르세요...")

def rate():          # 책 평가
    print("----------책 평가----------")
    while True:
        book_name_rate=input("평가할 책의 이름을 입력하세요.(/back을 입력하면 종료합니다.)")
        if (book_name_rate!="/back"): # /back이 아니면
            cursor.execute("SELECT Book_Name,Book_ID FROM Book WHERE Book_Name = N'%s'" %(book_name_rate)) # 책이름 검색
            row=cursor.fetchone()
            if row: # 책이름 검색결과가 있으면
                while True:
                    user_score=int(input("당신의 점수는?(0~10)")) # 점수 받고
                    if user_score>=0 and user_score<10: # 0~10점 조건 체크
                        book_id_rate=row[1] # 책ID 받아오고
                        cursor.execute("SELECT Users_ID FROM Library_Users WHERE Users_Name = N'%s'" %(NowLoginUser)) # 로그인중인 유저의 UserID를 Users테이블에서 불러오기
                        # NowLoginUser: plz_login()에서 global로 저장된 지금 로그인중인 유저의 이름
                        row=cursor.fetchone()
                        user_id_rate=row[0] # 로그인중인 유저의 UserID
                        count=1 # 평가번호 부여를 위한 카운트
                        while True: # 평가번호가 있는지 0부터 검색
                            cursor.execute("SELECT Eval_Num FROM Evaluate WHERE Eval_Num = %d"%(count))
                            row=cursor.fetchone()
                            if not row: # Eval_Num이 count랑 중복이 안되면
                                eval_num=count
                                break
                            count+=1 # 중복되면 다음count부터 다시검색
                        cursor.execute("INSERT INTO Evaluate VALUES(%d,'%s',%d,%d)"%(eval_num,user_id_rate,book_id_rate,user_score)) # Evaluate테이블에 평가번호 Users_ID Book_ID 점수 값 삽입
                        conn.commit()
                        print("점수가 등록되었습니다.")
                        input("계속하려면 엔터키를 누르세요...")
                        break # 데이터 삽입 성공
                    else: # 점수가 0~10사이가 아님
                        print("점수가 범위를 벗어났습니다.")
                break # 데이터 삽입 성공
            else: # 검색결과 없음
                print("해당 책 이름이 검색되지 않았습니다.")
        else: # /back 입력
            break

def addLib():
    print("----------책 소유 등록----------")
    while True:
        book_name_lib=input("소유를 등록할 책의 이름을 입력하세요.(/back을 입력하면 종료합니다.)")
        if (book_name_lib!="/back"):
            cursor.execute("SELECT Book_ID FROM Book WHERE Book_Name=N'%s'"%(book_name_lib))
            row=cursor.fetchone()
            if not row:
                print("입력된 이름의 책이 없습니다.")
            else:
                break
        else:
            return 0
    count=1 # Have_Num 부여를 위한 카운트
    book_id_lib=row[0]
    while True: # Have_Num이 있는지 0부터 검색
        cursor.execute("SELECT Library_ID FROM Have WHERE Library_ID = %d"%(count))
        row=cursor.fetchone()
        if not row: # Have_Num이 count랑 중복이 안되면
            Have_Num=count
            break
        count+=1 # 중복되면 다음count부터 다시검색
    while True:
        lib_name=input("책을 등록할 도서관의 이름을 입력하세요.")
        cursor.execute("SELECT Library_ID FROM Library WHERE Library_Name='%s'"%(lib_name))
        row_lib=cursor.fetchone()
        if row_lib:
            lib_id=row_lib[0]
            break
        else:
            print("없는 이름입니다.")
            continue
    
    cursor.execute("SELECT Have_Num FROM Have WHERE Library_ID = (SELECT Library_ID FROM Library WHERE Library_Name='%s')"%(lib_name))
    row_have_num=cursor.fetchall()
    if len(row_have_num):
        Holding=len(row_have_num)+1
    else:
        Holding=1
    cursor.execute("INSERT INTO Have VALUES (%d,%d,%d,0,%d)"%(Have_Num,lib_id,book_id_lib,Holding))
    conn.commit()
    print("책 소유 등록이 완료되었습니다.")
    input("계속하려면 엔터키를 누르세요...")

def search():        # 책 검색
    print("----------책 검색----------")
    # 검색키워드 입력 받기
    search_input=input("검색: ")
    # 키워드가 포함된 단어가 있는지 DB에서 검색(%%%s%%는 파이썬에서 %를 제대로 문자로 출력하기 위함)
    cursor.execute("SELECT Book_ID, Book_Name, Writer, Publisher, TopIC FROM Book WHERE Book_Name LIKE N'%%%s%%'" %(search_input))
    # row에 배열형태로 받아오기
    row=cursor.fetchall()
    # 출력
    print("\t책ID\t책이름\t작가\t퍼블리셔 주제\t소유주")
    for i in range(len(row)):
        #afterrow1=row[i][0].encode('ISO-8859-1') # 한글
        #afterrow1=afterrow1.decode('EUC-KR')     # 안돼서
        #afterrow2=row[i][1].encode('ISO-8859-1') # 찾아
        #afterrow2=afterrow2.decode('EUC-KR')     # 봤음
        cursor.execute("SELECT Library_Name FROM Library WHERE Library_ID = (SELECT Library_ID FROM Have WHERE Book_ID=%d)"%(row[i][0]))
        row_libname=cursor.fetchone()
        if row_libname:
            libname=row_libname[0]
        else:
            libname="없음"
            
        print("%d: "%(i+1),end=" ")
        print("\t%s\t%s\t%s\t%s\t%s\t%s"%(row[i][0],row[i][1],row[i][2],row[i][3],row[i][4],libname))
        #print("%s %s %s"%(afterrow1,afterrow2,row[i][2]))
    input("계속하려면 엔터키를 누르세요...")
#search()

def addBook():       # 책 등록
    print("----------책 추가----------")
    
    # 추가할 책 정보 입력
    # book_ID=int(input("추가할 책의 ID를 입력하세요."))
    count=1 # 평가번호 부여를 위한 카운트
    while True: # 평가번호가 있는지 0부터 검색
        cursor.execute("SELECT Book_ID FROM Book WHERE Book_ID = %d"%(count))
        row=cursor.fetchone()
        if not row: # Book_ID가 count랑 중복이 안되면
            book_ID=count
            break
        count+=1 # 중복되면 다음count부터 다시검색
    book_name_add=input("책의 이름을 입력하세요.")
    book_writer=input("책의 작가를 입력하세요.")
    book_publisher=input("책의 퍼블리셔를 입력하세요.")
    book_topic=input("책의 주제를 입력하세요.")
    
    cursor.execute("SELECT Book_ID FROM Book WHERE Book_ID = %d"%(book_ID))# 중복되는 ID의 책이 있는지 검색
    row_id=cursor.fetchall()
    cursor.execute("SELECT Book_Name FROM Book WHERE Book_Name = N'%s'"%(book_name_add))# 중복되는 제목의 책이 있는지 검색
    row_name=cursor.fetchall()
    # 만약 중복되는값이 하나라도 있으면 다시 입력
    if (row_id or row_name):
        print("이미 등록된 책입니다. 다시 입력하세요.")
    else: # 없으면 추가
        cursor.execute("INSERT INTO Book VALUES ('%d',N'%s',N'%s',N'%s',N'%s')"%(book_ID,book_name_add,book_writer,book_publisher,book_topic))
        conn.commit()

# addBook()
# search()

def delBook():       # 책 삭제
    print("----------책 삭제----------")
    while True:
        book_name_del=input("삭제할 책의 이름을 입력하세요.(/back을 입력하면 종료합니다.):")
        if (book_name_del!="/back"):
            cursor.execute("SELECT Book_Name FROM Book WHERE Book_Name=N'%s'"%(book_name_del)) # 책 이름 검색
            row_name_del=cursor.fetchall()
            if row_name_del: # 검색된 책이 있으면
                cursor.execute("SELECT Book_ID FROM Book WHERE Book_Name=N'%s'"%(book_name_del))
                row_id=cursor.fetchone()
                book_id_del=row_id[0]
                # 제약조건으로 인한 연쇄 삭제
                cursor.execute("DELETE FROM Loan WHERE Book_ID='%s'"%(book_id_del))
                cursor.execute("DELETE FROM Evaluate WHERE Book_ID='%s'"%(book_id_del))
                cursor.execute("DELETE FROM Have WHERE Book_ID='%s'"%(book_id_del))
                conn.commit()
                cursor.execute("DELETE FROM Book WHERE Book_Name=N'%s'"%(book_name_del)) # 책 삭제
                conn.commit()
                print("삭제가 완료되었습니다.")
                input("계속하려면 엔터키를 누르세요...")
                break
            else: # 검색된 책이 없으면
                print("없는 이름입니다.") # 다시 입력
        else: # /back 입력
            break
# delBook()
# search()

def plz_login():     # 로그인
    # 로그인 성공시 True반환 실패시 False 반환
    print("----------로그인----------")
    id=input("Id: ")
    password=input("Password: ")
    cursor.execute("SELECT Users_Name FROM Library_Users WHERE Users_ID = '%s' AND PW = '%s'" % (id, password)) # 입력된 id랑 password가 Users 테이블에 있는지 확인
    row=cursor.fetchone()
    if row is None: # Library_Users테이블에 없으면
        print("로그인 실패!")
        return False
    else: # Library_Users테이블에 있으면
        global NowLoginUser # 로그인중인 유저의 이름
        NowLoginUser=row[0] # Library_Users테이블의 Name
        print("%s님이 로그인하였습니다."%(NowLoginUser))
        return True
# plz_login()

def register():      # 가입
    # 가입 성공시 True반환 실패시 False 반환
    print("----------회원 등록----------")
    ID=input("등록할 아이디를 입력:(/back을 입력하면 종료합니다.)")
    cursor.execute("SELECT Users_ID FROM Library_Users WHERE Users_ID = '%s'"%(ID)) # 입력된 ID를 검색
    row=cursor.fetchall()
    if not row: # 중복되는 ID가 없으면
        while(ID!="/back"): # ID입력창에 /back 입력하기 전까지 계속
           PASSWORD=input("등록할 비밀번호 입력:")
           PASSWORD_correct=input("비밀번호 재입력:") # 비밀번호 확인
           if (PASSWORD==PASSWORD_correct): # 비밀번호 확인 성공시
               your_name=input("이름을 입력하세요.")
               your_age=int(input("나이를 입력하세요."))
               cursor.execute("INSERT INTO Library_Users VALUES('%s','%s',N'%s',%d)"%(ID,PASSWORD,your_name,your_age)) # Library_Users 테이블에 정보 삽입
               conn.commit()
               print("%s님의 가입이 완료되었습니다."%(your_name))
               input("계속하려면 엔터키를 누르세요...")
               return True
           else: # 비밀번호 확인 실패시
              print("비밀번호가 일치하지 않습니다.")
              ID=input("등록할 아이디를 입력:(/back을 입력하면 종료합니다.)") # ID 받으면서 가입 처음부터
    else: # 중복되는 ID가 있으면
        print("ID가 중복됩니다.")
        return False
# register()
# plz_login()

def setDate():       # 책 대여
    while True:
        book_name_loan=input("빌릴 책의 이름을 입력하세요(/back을 입력하면 종료합니다.): ")
        if (book_name_loan!="/back"):
            cursor.execute("SELECT Book_ID FROM Book WHERE Book_Name='%s'"%(book_name_loan)) # 책이름으로 책ID검색 아래에서 다시 사용
            row=cursor.fetchall()
            if row: # 검색한 이름의 책이 존재하면
                loan_date=int(input("대여 시작일(yyyymmdd): "))
                deadline=int(input("반납 예정일(yyyymmdd): "))
                cursor.execute("SELECT Users_ID FROM Library_Users WHERE Users_Name='%s'"%(NowLoginUser)) # 현재 로그인한 유저의 이름으로 ID가져옴
                row_userid=cursor.fetchone()
                user_id=row_userid[0]
                book_id=row[0][0] # 위에서 (책이름으로 책ID검색)했던 결과에서 가져오기
                count=1 # 대출번호 부여를 위한 카운트
                while True: # 대출번호가 있는지 0부터 검색
                    cursor.execute("SELECT Loan_Num FROM Loan WHERE Loan_Num = %d"%(count))
                    row=cursor.fetchone()
                    if not row: # Loan_Num이 count랑 중복이 안되면
                        loan_num=count
                        break
                    count+=1 # 중복되면 다음count부터 다시검색
                cursor.execute("INSERT INTO Loan VALUES(%d,N'%s',%d,%d,%d)"%(loan_num,user_id,book_id,loan_date,deadline)) # Loan테이블에 대여정보 추가
                conn.commit()
                print("대여가 완료되었습니다!")
                input("계속하려면 엔터키를 누르세요...")
                break
            else: # 검색한 이름의 책이 없으면
                print("없는 이름입니다.")
        else: # /back 입력시
            break # 메뉴로
# plz_login()
# setDate()

def viewDate():      # 책 대여현황
    cursor.execute("SELECT Loan_Num,Users_ID,Book_ID,Loan_Date,Deadline FROM Loan") # Loan테이블에서 모든정보 가져오기(대출번호,유저아이디,책아이디,빌린날,반납기한)
    row_loan=cursor.fetchall()
    print("\t사람이름\t책이름\t대여시작일\t반납기한")
    for i in range(len(row_loan)): # 대여기록이 있는 책의 개수만큼
        cursor.execute("SELECT Users_Name FROM Library_Users WHERE Users_ID='%s'"%(row_loan[i][1])) # Loan테이블에서 가져왔던 정보(유저ID)로 빌린 사람 이름 가져오기
        row_username=cursor.fetchone()
        cursor.execute("SELECT Book_Name FROM Book WHERE Book_ID=%d"%(row_loan[i][2]))  # Loan테이블에서 가져왔던 정보(책ID)로 빌린 책 이름 가져오기
        row_bookname=cursor.fetchone()
        print("%d:\t%s\t\t%s\t%d\t%d"%(row_loan[i][0],row_username[0],row_bookname[0],row_loan[i][3],row_loan[i][4])) # 이름 책이름 대여일 반납일 출력
    input("계속하려면 엔터키를 누르세요...")
    
# viewDate()

# register()
while True: # 가입 및 로그인
    register_menu()
    registerd=int(input("번호 입력: ")) # 0 회원가입 1 로그인
    if registerd: # 1
        break
    else:         # 0
        register()

input_num=-1 # 반복문의 if문 체크를 위한 초기값 설정

while True: # 메인 기능
    if (input_num=='0'): # 0번입력(종료)시
        break            # 프로그램 종료
    else:
        is_login=plz_login() # 로그인 성공:True 실패:False
        while is_login: # 로그인 성공시 로그아웃하기 전까지
            menu()      # 1랭킹 2평가 3검색 4등록 5삭제 6로그아웃 7대여날짜 8대여현황 9책소유등록 0종료
            input_num=input("번호 입력: ")
            if input_num=='1':
                ranking()
            elif input_num=='2':
                rate()
            elif input_num=='3':
                search()
            elif input_num=='4':
                addBook()
            elif input_num=='5':
                delBook()
            elif input_num=='6':
                is_login=False
            elif input_num=='7':
                setDate()
            elif input_num=='8':
                viewDate()
            elif input_num=='9':
                addLib()
            elif input_num=='0':
                print("%s님 좋은하루 되세요."%(NowLoginUser))
                break
            else: # 0~9사이의 입력이 아니면
                input("다시 입력하세요.")

# SQL문 실행
# cursor.execute('SELECT * FROM Book')
# 커서로 실행한 데이터 하나씩 가져오기
# row = cursor.fetchone()
# 커서로 실행한 데이터 한번에 가져오기
# row = cursor.fetchall()

# 연결 끊기
conn.close()