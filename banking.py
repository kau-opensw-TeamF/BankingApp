
import random
import sys
import sqlite3

#랜덤 번호 생성을 위한 시드 설정
random.seed()

#sqlite3 DB 연결
conn = sqlite3.connect('card.s3db')#이전에 명명된 db와 연결
cur = conn.cursor() #SQL 스크랩트를 실행하기 위한 커서 객체 생성

# card 테이블이 없는 경우 생성
cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER PRIMARY KEY,number TEXT,pin TEXT,balance INTEGER DEFAULT 0);")

# transactions 테이블이 존재하지 않는 경우 생성
cur.execute("""CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY,
                card_number TEXT,
                transaction_type TEXT,
                amount INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
conn.commit() #DB에 결과 저장


class Card:

    def __init__(self): #인스턴스 속성 초기화
        self.card = ''
        self.pin = ''
        self.login_card = ''
        self.login_pin = ''
        self.row = []
        self.balance = 0
        self.receiver_balance = 0
        
    def create_account(self): #새 계정 생성 후 카드 번호와 핀 생성
        print("Your card has been created")
        print("Your card number:")

        # 랜덤한 카드 번호 생성
        self.card = '400000' + str(random.randint(100000000, 999999999)) 
        print(self.luhn()) #luhn 알고리즘을 통해 검증가능한 유효 카드번호 반환

        #랜덤한 핀 생성
        print("Your card PIN:")
        self.pin = str(random.randint(1000, 9999)) #랜덤한 pin번호 생성
        print(self.pin)

        # 새 계정 정보를 데이터베이스에 삽입
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (self.card, self.pin)) #DB에 카드, pin 정보 추가
        conn.commit() #변경 사항 저장
        
    def log_in(self):
        #카드 번호와 핀을 사용하여 기존 계정에 로그인
        self.login_card = input("Enter your card number:\n")
        self.login_pin = input("Enter your PIN:\n")

        # 입력한 카드 번호와 핀으로 데이터베이스에서 조회
        cur.execute("""SELECT
                            id,
                            number,
                            pin,
                            balance
                        FROM 
                            card
                        WHERE
                            number = ? AND pin = ?;""", (self.login_card, self.login_pin)) #입력받은 정보를 통해 sql문으로 db조회

        self.row = cur.fetchone() #조회 결과를 가져옴
        if self.row: #계정이 존재할 경우
            self.balance = self.row[3] #db의 네번째 요소인 balance(id, number, pin, balance 중 balance)를 이 instance의 balance에 넣음.
            print('\nYou have successfully logged in')
            self.success() #계정 메뉴로 이동

        else:
            print("wrong card number or pin")

        '''elif not self.luhn_2(self.login_card):
            print('Probably you made a mistake in the card number. Please try again!')'''
            
    def success(self): #1.자산확인 2.입금기능 3.송금기능 4.계좌폐쇄 5.로그아웃 0.종료
        while True: #입력받은 숫자에 따라 기능 실행
            print("""\n1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
            i = int(input())
            if i == 1: #잔액 확인
                print('\nBalance: ', self.balance) #현재 내 자산 출력
                print()
            elif i == 2: #입금기능
                print('\nEnter income:')
                amount = int(input())
                self.balance += amount #기존잔고 + 입금액
                # 잔액 업데이트 및 입금 내역 데이터베이스에 기록
                cur.execute("UPDATE card SET balance = ? WHERE number = ?;", (self.balance, self.login_card))
                # 트랜잭션 로그 기록
                cur.execute("INSERT INTO transactions (card_number, transaction_type, amount) VALUES (?, ?, ?);", 
                            (self.login_card, 'deposit', amount))
                conn.commit() #변경 사항 저장
                print('Income was added!')
            elif i == 3: #이체기능
                print('\nTransfer\nEnter card number:')
                receiver_card = input() #돈을 보낼 카드번호를 입력받고 db에 receiver_card에 저장.
                cur.execute("SELECT id, number,pin,balance FROM card WHERE number = ?;", (receiver_card,))

                if not self.luhn_2(receiver_card): #룬2에서 반환받은 값이 false라면
                    print('Probably you made a mistake in the card number. Please try again!')
                elif not cur.fetchone(): #카드번호 자체가 없을시
                    print('Such a card does not exist')
                else:
                    transfer = int(input("Enter how much money you want to transfer:\n")) #송금액 입력
                    if transfer > self.balance:
                        print("Not enough money!") #잔액이 부족할 경우
                    else: #계좌에서 실제로 이체
                        self.balance -= transfer #송금자의 잔액에서 이체 금액 차감
                        cur.execute("UPDATE card SET balance = ? WHERE number = ?;", (self.balance, self.login_card))

                        #수신자의 잔액 업데이트
                        self.receiver_balance -= transfer #수금자 자산총액에서 송금액 추가. DB에 업데이트
                        cur.execute("UPDATE card SET balance = ? WHERE number = ?;", (self.receiver_balance, receiver_card))

                        # 트랜잭션 로그 기록 (송금자)
                        cur.execute("INSERT INTO transactions (card_number, transaction_type, amount) VALUES (?, ?, ?);", 
                                        (self.login_card, 'transfer_out', transfer))                            # 트랜잭션 로그 기록 (수신자)
                        cur.execute("INSERT INTO transactions (card_number, transaction_type, amount) VALUES (?, ?, ?);", 
                                        (receiver_card, 'transfer_in', transfer))
                            
                        conn.commit() #변경 사항 저장
                        print("Success!")
            elif i == 4: #계좌 해지
                cur.execute("DELETE FROM card WHERE number = ?", (self.login_card,)) #sql문으로 해당 카드와 관련된 DB내 모든 정보 삭제
                conn.commit() #변경 사항 저장
                print('\nThe account has been closed!')
                break
            elif i == 5: #로그아웃
                print("\nYou have successfully log out!")
                break
            elif i == 0: #종료
                print("\nBye!")
                conn.close() #데이터베이스 연결 종료
                sys.exit()

    # 룬2 : 카드번호의 유효성. 이 검사를 통과할 시 true, 못하면 false
    def luhn_2(self, num): #Luhn 알고리즘을 사용해 카드번호가 유효성 검사
        num2 = num[:]
        num2 = num2[::-1]
        lst = [int(x) for x in num2]
        s1 = sum(lst[::2])
        for i in range(len(lst)):
            if i % 2 != 0:
                lst[i] = lst[i] * 2
        for i in range(len(lst)):
            if lst[i] > 9:
                lst[i] -= 9
        s2 = sum(lst[1:len(lst):2])

        if (s1 + s2) % 10 == 0:
            return True
        return False
                
    # Defining my luhn algorithm for creating a new card number
    def luhn(self): #Luhn 알고리즘을 사용해 새 카드 번호 생성

        lst2 = [int(x) for x in self.card]
        lst3 = lst2[:]
        
        for i in range(len(lst3)):
            if i % 2 == 0:
                lst3[i] = lst3[i] * 2
            else:
                lst3[i] = lst3[i]
    
        for i in range(len(lst3)):
            if lst3[i] > 9:
                lst3[i] -= 9
            
        tot = sum(lst3)
        count_sum = 0
        while True:
            if (tot + count_sum) % 10 == 0:
                break
            else:
                count_sum += 1
                
        lst2.append(count_sum)
        self.card = (''.join(map(str, lst2)))
        
        return self.card
        
    def menu(self): #메뉴 표시 메소드 1.계좌생성 2.로그인 0.종료
        while True:
            print("""\n1. Create an account
2. Log into account
0. Exit""")
            i = int(input())
            if i == 1:
                self.create_account()
            elif i == 2:
                self.log_in()
            elif i == 0:
                conn.close() #데이터베이스 연결 종료
                print("\nBye!")
                break
            else:
                print("Invalid input")
                
#Card instance 생성 후 menu 메소드 실행
card = Card()
card.menu()