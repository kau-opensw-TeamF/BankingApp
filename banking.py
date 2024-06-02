
import random
import sys
import sqlite3
random.seed()

#sqlite3 DB
conn = sqlite3.connect('card.s3db')#이전에 명명된 db와 연결
cur = conn.cursor() #cursor object 생성으로 sql script 동작
# cur.execute("DROP TABLE card")
# card 테이블이 없는 경우 생성
cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER PRIMARY KEY,number TEXT,pin TEXT,balance INTEGER DEFAULT 0);")
conn.commit() #DB에 결과 저장


class Card:

    def __init__(self): #생성자 card의 instance attribute : card, pin, login_card, login_pin, row, balance, receiver_balance 값 초기화
        self.card = ''
        self.pin = ''
        self.login_card = ''
        self.login_pin = ''
        self.row = []
        self.balance = 0
        self.receiver_balance = 0
        
    def create_account(self): #카드번호 생성
        print("Your card has been created")
        print("Your card number:")
        # 랜덤한 카드 번호 생성
        self.card = '400000' + str(random.randint(100000000, 999999999)) 
        print(self.luhn()) #luhn을 통해 검증가능한 유효 카드번호 반환
        print("Your card PIN:")
        self.pin = str(random.randint(1000, 9999)) #랜덤한 pin번호 생성
        print(self.pin)
        # 생성된 계정 정보를 데이터베이스에 삽입
        cur.execute(f"""INSERT INTO card (number, pin) VALUES ({self.card}, {self.pin});""") #DB에 카드, pin 정보 추가
        conn.commit() # 저장
        
    def log_in(self): #카드번호와 PIN을 받아서 sql문으로 검색, 검색된 경우 sucess문으로 넘어감

        self.login_card = input("Enter your card number:\n")
        self.login_pin = input("Enter your PIN:\n")

        cur.execute(f"""SELECT
                            id,
                            number,
                            pin,
                            balance
                        FROM 
                            card
                        WHERE
                            number = {self.login_card}
                            AND pin = {self.login_pin}
                        ;""") #입력받은 정보를 통해 sql문으로 db조회

        self.row = cur.fetchone() #만약 cur에 입력받은게 있으면 그 값을 가져오고, 없다면 NULL을 가져옴
        if self.row: #계정 존재시 로그인 성공
            self.balance = self.row[3] #db의 네번째 요소인 balance(id, number, pin, balance 중 balance)를 이 instance의 balance에 넣음.
            print('\nYou have successfully logged in')
            self.success() #로그인 성공시 메뉴

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
            if i == 1: #자산확인
                print('\nBalance: ', self.balance) #현재 내 자산 출력
                print()
            elif i == 2: #입금기능
                print('\nEnter income:')
                amount = int(input())
                self.balance += amount #기존잔고 + 입금액
                # 잔액 업데이트 및 입금 내역 데이터베이스에 기록
                cur.execute(f'UPDATE card SET balance = {self.balance} WHERE number = {self.login_card};')
                conn.commit() #DB저장
                print('Income was added!')
            elif i == 3: #송금기능
                print('\nTransfer\nEnter card number:')
                receiver_card = input() #돈을 보낼 카드번호를 입력받고 db에 receiver_card에 저장.
                cur.execute(f'SELECT id, number,pin,balance FROM card WHERE number = {receiver_card};')

                if not self.luhn_2(receiver_card): #룬2에서 반환받은 값이 false라면
                    print('Probably you made a mistake in the card number. Please try again!')
                elif not cur.fetchone(): #카드번호 자체가 없을시
                    print('Such a card does not exist.')
                else:
                    transfer = int(input("Enter how much money you want to transfer:\n")) #송금액 입력
                    if transfer > self.balance:
                        print("Not enough money!") #송금액이 자산총액보다 많을 경우
                    else: #계좌에서 실제로 이체
                        self.balance -= transfer #송금자 자산총액에서 송금액 제외. DB에 업데이트
                        cur.execute(f'UPDATE card SET balance = {self.balance} WHERE number = {self.login_card};')
                        self.receiver_balance += transfer #수금자 자산총액에서 송금액 추가. DB에 업데이트
                        cur.execute(f'UPDATE card SET balance = {self.receiver_balance} WHERE number = {receiver_card};')
                        cur.execute(f'SELECT * FROM card WHERE number = {self.login_card}') #송금자 카드번호를 기반으로 DB내 모든 정보 조회
                        print(cur.fetchone())
                        print("Success!")
                        conn.commit()

            elif i == 4: #계좌폐쇄
                cur.execute(f"DELETE FROM card WHERE number = {self.login_card}") #sql문으로 해당 카드와 관련된 DB내 모든 정보 삭제
                conn.commit()
                print('\nThe account has been closed!')
                break
            elif i == 5: #로그아웃
                print("\nYou have successfully log out!")
                break
            elif i == 0: #종료
                print("\nBye!")
                conn.close()
                sys.exit()

    # 룬2 : 카드번호의 유효성. 이 검사를 통과할 시 true, 못하면 false
    def luhn_2(self, num): #Luhn 알고리즘을 사용해 카드번호가 유효한지 판단
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
    def luhn(self): #Luhn 알고리즘을 사용해 새 카드번호를 정의하는 메소드

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
        
    def admin_menu(self): #관리자 기능 메소드 1.전체 계좌 목록 조회 2.특정 계좌 삭제 0.관리자 기능 종료
        
        admin_password = 1000 #비밀번호는 1000
        input_password = int(input("password: "))
        
        while (admin_password == input_password): 
            print("""\nAdmin Menu
1. View all accounts
2. Delete an account
0. Back to main menu""")
            i = int(input())
            if i == 1:  # 전체 계좌 목록 조회
                cur.execute("SELECT id, number, pin, balance FROM card;")
                accounts = cur.fetchall()
                print("\nAll Accounts:")
                for account in accounts:
                    print(f"ID: {account[0]}, Number: {account[1]}, PIN: {account[2]}, Balance: {account[3]}")
            elif i == 2:  # 특정 계정 삭제
                print('\nEnter card number to delete:')
                delete_card = input()
                cur.execute(f"SELECT * FROM card WHERE number = {delete_card};")
                if cur.fetchone():
                    cur.execute(f"DELETE FROM card WHERE number = {delete_card}")
                    conn.commit()
                    print("The account has been deleted!")
                else:
                    print("Such a card does not exist.")
            elif i == 0: # 관리자 기능 종료
                break
            else:
                print("Invalid input")
        
    def menu(self): #메뉴 표시 메소드 1.계좌생성 2.로그인 0.종료
        while True:
            print("""\n1. Create an account
2. Log into account
3. Adimin menu 
0. Exit""")
            i = int(input())
            if i == 1:
                self.create_account()
            elif i == 2:
                self.log_in()
            elif i == 3:
                self.admin_menu()
            elif i == 0:
                conn.close()
                print("\nBye!")
                break
            else:
                print("Invalid input")
                

#instance 생성 후 menu 메소드 실행
card = Card()
card.menu()