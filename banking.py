import random
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox
random.seed()

#sqlite3 DB
conn = sqlite3.connect('card.s3db') #이전에 명명된 db와 연결
cur = conn.cursor() #cursor object 생성으로 sql script 동작
# cur.execute("DROP TABLE card")
# card 테이블이 없는 경우 생성
cur.execute("""
CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT,balance INTEGER DEFAULT 0
    );""")
conn.commit() #DB에 결과 저장


class Card:

    def __init__(self, root): #생성자 card의 instance attribute : card, pin, login_card, login_pin, row, balance, receiver_balance 값 초기화
        self.root = root
        self.root.title("OpenSourceSW Team F")
        self.root.geometry("500x300")
        self.root.resizable(width=False, height=False)
        self.card = ''
        self.pin = ''
        self.login_card = ''
        self.login_pin = ''
        self.row = []
        self.balance = 0
        self.receiver_balance = 0
        self.language = 'en'
        self.messages = {
            'en': {
                'select_fucntion': "Select a function",
                #'welcome': "\n1. Create an account\n2. Log into account\n9. Switch Language\n0. Exit",
                'createaccbtn' : "Create an account",
                'loginbtn' : "Log into account",
                'exitbtn' : "Exit",
                'menu': "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n9. Switch Language\n0. Exit",
                'create_card': "Your card has been created\nYour card number:",
                'create_pin': "Your card PIN:",
                'enter_card': "Enter your card number:",
                'enter_pin': "Enter your PIN:",
                'login_success': "\nYou have successfully logged in",
                'login_failure': "Wrong card number or PIN",
                'balance': '\nBalance: ',
                'enter_income': '\nEnter income:',
                'income_added': 'Income was added!',
                'transfer': '\nTransfer\nEnter card number:',
                'mistake_card_number': 'Probably you made a mistake in the card number. Please try again!',
                'no_card': 'Such a card does not exist.',
                'enter_transfer_amount': "Enter how much money you want to transfer:\n",
                'not_enough_money': "Not enough money!",
                'transfer_success': "Success!",
                'account_closed': '\nThe account has been closed!',
                'logout_success': "\nYou have successfully logg out!",
                'bye': "\nBye!",
                'invalid_input': "Invalid input",
            },
            'ko': {
                'select_fucntion': "기능을 선택하세요.",
                'welcome': "\n1. 계좌 생성\n2. 로그인\n9. 영한 변환\n0. 종료",
                'menu': "\n1. 잔액 확인\n2. 수입 추가\n3. 이체\n4. 계좌 폐쇄\n5. 로그아웃\n9. 영한 변환\n0. 종료",
                'create_card': "카드가 생성되었습니다\n카드 번호:",
                'create_pin': "카드 PIN:",
                'enter_card': "카드 번호를 입력하세요:",
                'enter_pin': "PIN을 입력하세요:",
                'login_success': "\n성공적으로 로그인했습니다",
                'login_failure': "잘못된 카드 번호 또는 PIN",
                'balance': '\n잔액: ',
                'enter_income': '\n수입을 입력하세요:',
                'income_added': '수입이 추가되었습니다!',
                'transfer': '\n이체\n카드 번호를 입력하세요:',
                'mistake_card_number': '카드 번호에 실수가 있는 것 같습니다. 다시 시도하세요!',
                'no_card': '존재하지 않는 카드입니다.',
                'enter_transfer_amount': "이체할 금액을 입력하세요:\n",
                'not_enough_money': "잔액이 부족합니다!",
                'transfer_success': "성공!",
                'account_closed': '\n계좌가 폐쇄되었습니다!',
                'logout_success': "\n성공적으로 로그아웃했습니다!",
                'bye': "\n안녕!",
                'invalid_input': "잘못된 입력",
            }
        }
        
        # 실행부분을 init으로 옮겨야 함. main에서 실행할 수 없음.
        self.main_window()
        
       
    def translate(self, message):
        return self.messages[self.language][message]
    #en기본언어 ko변경 감지시 switch
    def switch_language(self):
        self.language = 'ko' if self.language == 'en' else 'en'
        messagebox.showinfo("info","language has been changed to english")
        
    def create_account(self): #카드번호 생성
        print(self.translate('create_card'))
        # 랜덤한 카드 번호 생성
        self.card = '400000' + str(random.randint(100000000, 999999999)) 
        print(self.luhn()) #luhn을 통해 검증가능한 유효 카드번호 반환
        print(self.translate('create_pin'))
        self.pin = str(random.randint(1000, 9999)) #랜덤한 pin번호 생성
        print(self.pin)
        # 생성된 계정 정보를 데이터베이스에 삽입
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (self.card, self.pin)) #DB에 카드, pin 정보 추가
        conn.commit() # 저장    
        
    def destroy_window(self): # gui 에서 화면을 지우는 코드. 처음 화면 초기화 시에 사용
        for kidwin in self.root.winfo_children():
            kidwin.destroy()
    
    def main_window(self):
        self.destroy_window()
        
        # 그리드 행과 열 구성
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        tk.Label(self.root, text=self.translate('select_fucntion')).grid(row=0, column=1, pady=10)

        
        button1 = tk.Button(self.root, text=self.translate('createaccbtn'), command=self.create_account, width=20, height=10)
        button2 = tk.Button(self.root, text=self.translate('loginbtn'), command=self.log_in, width=20, height=10)
        button3 = tk.Button(self.root, text=self.translate('exitbtn'), command=self.exit, width=20, height=10)
        button4 = tk.Button(self.root, text="Admin", command=self.admin_menu, width=5, height=2)
        button5 = tk.Button(self.root, text=f"Switch Language", command=self.switch_language, width=4, height=2)
        
        button1.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        button2.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        button3.grid(row=1, column=2, padx=10, pady=10, sticky='nsew')
        button4.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        button5.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # 그리드 행과 열 구성 조정
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
    
    def exit(self): #모든 창을 닫는 코드s
        conn.close()
        messagebox.showinfo("info","See you Next time!")
        self.destroy_window()
        root.destroy()
        sys.exit()
        
    def show_account(self, account, pin):
        label_account = tk.Label(self.root, text=f"Account : {account}")
        label_pin = tk.Label(self.root, text=f"Pin : {pin}")
        label_account.grid(row=3, column=1, pady=2)
        label_pin.grid(row=4, column=1, pady=3)
        
    def create_account(self):
        # 랜덤한 카드 번호 생성
        self.card = '400000' + str(random.randint(100000000, 999999999))
        new_account = self.luhn()
        # 랜덤한 PIN 번호 생성
        self.pin = str(random.randint(1000, 9999))
        
        self.show_account(new_account, self.pin)
        
        # 생성된 계정 정보를 데이터베이스에 삽입
        cur.execute(f"INSERT INTO card (number, pin) VALUES (?, ?)", (self.card, self.pin)) # DB에 카드, pin 정보 추가
        conn.commit() # 저장
        
    def log_in(self): #카드번호와 PIN을 받아서 sql문으로 검색, 검색된 경우 sucess문으로 넘어감 
        self.login_attempts = 0  # 로그인 시도 횟수 초기화
        #self.login_card = input("Enter your card number:\n")
        #self.login_pin = input("Enter your PIN:\n")
        login_win = tk.Toplevel(self.root)
        login_win.title("Log In")
        login_win.geometry("350x200")
        #self.root.wait_window()
        login_win.grab_set()
        tk.Label(login_win, text="Enter your card number:").pack(pady=5)
        self.card_input = tk.Entry(login_win,width=20)
        self.card_input.pack(pady=5)
        tk.Label(login_win, text="Enter your pin number:").pack(pady=5)
        self.pin_input = tk.Entry(login_win,width=20)
        self.pin_input.pack(pady=5) 
        tk.Button(login_win,text="Log In",command=lambda:self.check_login(login_win)).pack(pady=10)
    
        
    def check_login(self,login_win):
        self.login_card = self.card_input.get()
        self.login_pin = self.pin_input.get()
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
        #login_win.destroy() #디버깅용 코드. 아랫줄도
        #self.success() #로그인 성공시 메뉴 
        
        if self.row: #계정 존재시 로그인 성공
            self.balance = self.row[3] #db의 네번째 요소인 balance(id, number, pin, balance 중 balance)를 이 instance의 balance에 넣음.
            print('\nYou have successfully logged in')
            login_win.destroy()
            self.success() #로그인 성공시 메뉴 

        else:
            #print("wrong card number or pin")
            self.login_attempts += 1
            if (self.login_attempts >= 5): #로그인 실패 횟수가 5번이 넘어가면 종료, 악의적 로그인 시도의 차단.
                messagebox.showerror("error","Too many failed login attempts. program will exit.")
                sys.exit()
            messagebox.showerror("error",f"wrong card number or pin. {5-self.login_attempts} attempts left.")
        '''elif not self.luhn_2(self.login_card):
                print('Probably you made a mistake in the card number. Please try again!') '''
        

    
    '''    
    def log_in(self): #카드번호와 PIN을 받아서 sql문으로 검색, 검색된 경우 sucess문으로 넘어감

        login_attempts = 0  # 로그인 시도 횟수 초기화
    
        while login_attempts < 5:
            self.login_card = input("Enter your card number:\n")
            self.login_pin = input("Enter your PIN:\n")
        
            cur.execute("""SELECT
                            id,
                            number,
                            pin,
                            balance
                        FROM 
                            card
                        WHERE
                            number = ? AND pin = ?;""", (self.login_card, self.login_pin)) #입력받은 정보를 통해 sql문으로 db조회

            self.row = cur.fetchone() #만약 cur에 입력받은게 있으면 그 값을 가져오고, 없다면 NULL을 가져옴
            if self.row: #계정 존재시 로그인 성공
                self.balance = self.row[3] #db의 네번째 요소인 balance(id, number, pin, balance 중 balance)를 이 instance의 balance에 넣음.
                print('\nYou have successfully logged in')
                self.success() #로그인 성공시 메뉴
                return

            else:
                login_attempts += 1 
                print("Wrong card number or PIN")
                if login_attempts >= 5: #로그인 실패 횟수가 5번이 넘어가면 종료, 악의적 로그인 시도의 차단.
                    print("Too many failed login attempts. program will exit.")
                    conn.close()
                    sys.exit() 
        '''

                            

                
    def success(self): #1.자산확인 2.입금기능 3.송금기능 4.계좌폐쇄 5.로그아웃 0.종료
        myaccount = tk.Toplevel(root)
        myaccount.title("My Account")
        myaccount.geometry("350x600")
        myaccount.resizable(width=False, height=False)
        myaccount.grab_set()
        myaccount.protocol('WM_DELETE_WINDOW', lambda:self.logout(myaccount))
        
        
        #self.root.wait_window()
        tk.Button(myaccount,text="0. exit",command=self.exit).grid(row=5,column=5,pady=20)
        tk.Button(myaccount,text="1. Balance",command=lambda:self.mybalance(myaccount)).grid(row=10,column=5,pady=20)
        tk.Button(myaccount,text="2. Add income",command=lambda:self.addincome(myaccount)).grid(row=15,column=5,padx = 10, pady=20)
        tk.Button(myaccount,text="3. Do transfer",command=lambda:self.transfer(myaccount)).grid(row=20,column=5,padx = 10,pady=20)
        tk.Button(myaccount,text="4.Close account",command=lambda:self.closeaccount(myaccount)).grid(row=25,column=5,padx = 10,pady=20)
        tk.Button(myaccount,text="5. Log out",command=lambda:self.logout(myaccount)).grid(row=30,column=5,pady=20)
    
    def mybalance(self, myaccount):
        if not hasattr(self, 'balance_label'):
            self.balance_label = tk.Label(myaccount, text=f"Balance: {self.balance}", width=20)
            self.balance_label.grid(row=10,column=10,padx = 10, pady=20)
        else:
            self.balance_label.config(text=f"Balance: {self.balance}")
    
    def addincome(self,myaccount):
        if not hasattr(self,'add_label'):
        #mybalwin = tk.Toplevel(myaccount)
            self.add_label = tk.Label(myaccount,text="Add income: ").grid(row=12,column=10)
            add = tk.Entry(myaccount,width=15)
            add.grid(row=15,column=10)
            tk.Button(myaccount,text="Add",command = lambda:self.addmethod(myaccount,add)).grid(row=16,column=10)
    def addmethod(self,myaccount,add):       
        try:
            income = int(add.get())
            self.balance += income
            cur.execute(f'UPDATE card SET balance = {self.balance} WHERE number = {self.login_card};')
            conn.commit() #DB저장
            messagebox.showinfo("Info",f"Income has been added! your balance : {self.balance}")
            #self.balance_label.config(text=f"Balance: {self.balance}")
            self.mybalance(myaccount)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid integer.")
        #tk.Button(myaccount,text="addincome",command=lambda:self.mybalance(myaccount)).pack(5)
        
        
    def transfer(self,myaccount):
        if not hasattr(self,'tf_label'):
            #로직 : receiver_card 번호 입력받고,  송금액 입력받고, 실제로 구현해서 보여주기. 내 계좌 변동도 보여주기.
            self.tf_label = tk.Label(myaccount,text="Transfer Enter Card Number").grid(row=18,column=10)
            receivecard = tk.Entry(myaccount,width=20)
            receivecard.grid(row=20,column=10)
            tk.Button(myaccount,text="Enter",command=lambda:self.transfermethod(myaccount,receivecard)).grid(row=22,column=10)
    def transfermethod(self,myaccount,receivecard):
        try:
            self.receiver_card = str(receivecard.get())
            cur.execute(f'SELECT id, number,pin,balance FROM card WHERE number = {self.receiver_card};')
            if not self.luhn_2(self.receiver_card): #룬2에서 반환받은 값이 false라면
                messagebox.showerror("error:numbermistake",'Probably you made a mistake in the card number. Please try again!')
            elif not cur.fetchone(): #카드번호 자체가 없을시
                messagebox.showerror("error:numbernull",'Such a card does not exist.')
            else:
                tfwin = tk.Toplevel(myaccount)
                tfwin.geometry("700x150")
                tfwin.grab_set()
                #myaccount.wait_window()
                #self.root.wait_window()
                label = tk.Label(tfwin,text="Enter how much money you want to transfer").pack()
                tfmoney = tk.Entry(tfwin,width=20)
                tfmoney.pack(pady=10)
                tk.Button(tfwin,text="Enter",command=lambda:self.tfmoneycheck(tfmoney)).pack()
        except ValueError:
            messagebox.showerror("error","error")
    def tfmoneycheck(self,tfmoney):
        try:
            tfmoney = int(tfmoney.get())
            if tfmoney > self.balance:
                messagebox.showerror("Error","Not Enough Money!")
            else:
                self.balance -= tfmoney #송금자 자산총액에서 송금액 제외. DB에 업데이트
                cur.execute(f'UPDATE card SET balance = {self.balance} WHERE number = {self.login_card};')
                self.receiver_balance += tfmoney #수금자 자산총액에서 송금액 추가. DB에 업데이트
                cur.execute(f'UPDATE card SET balance = {self.receiver_balance} WHERE number = {self.receiver_card};')
                cur.execute(f'SELECT * FROM card WHERE number = {self.login_card}') #송금자 카드번호를 기반으로 DB내 모든 정보 조회
                messagebox.showinfo("info",f"success! My balance : {self.balance}")
                conn.commit()
        except ValueError:
            messagebox.showerror("Error","Invalid integer input")

    def closeaccount(self,myaccount):
        closewin = tk.Toplevel(myaccount)
        closewin.geometry("300x90")
        closewin.resizable(width=False, height=False)
        closewin.grab_set()
        #self.root.wait_window()
        label = tk.Label(closewin,text="Do you want to Delete this account?")
        label.pack()
        tk.Button(closewin,text="yes",command=lambda:self.deleteaccount(myaccount),width=10,height=2).pack(side = "bottom",pady=10)
        
    def deleteaccount(self,myaccount):
        cur.execute(f"DELETE FROM card WHERE number = {self.login_card}") #sql문으로 해당 카드와 관련된 DB내 모든 정보 삭제
        conn.commit()
        messagebox.showinfo("info","The account has been deleted!")
        self.logout(myaccount)
 
    def logout(self,myaccount):
        #messagebox.showinfo("info","You have successfully log out!")
        messagebox.showinfo("info", "You have successfully logged out!")
        
        # 로그인 정보 초기화
        self.login_card = ''
        self.login_pin = ''
        self.row = []
        self.balance = 0
        self.receiver_balance = 0
        if hasattr (self,'balance_label'): del self.balance_label
        if hasattr (self,'tf_label'): del self.tf_label
        if hasattr (self,'add_label'): del self.add_label
        # 초기 화면으로 돌아가기
        myaccount.destroy()
    
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
        
        self.admin_password = 1000 #비밀번호는 1000
        adminlogin = tk.Toplevel(root)
        adminlogin.title("Admin Login")
        adminlogin.geometry("300x100")
        
        adminlogin.grab_set()
        
        tk.Label(adminlogin, text="Enter Admin Password:").pack(pady=5)
        input_password = tk.Entry(adminlogin, width=20)
        input_password.pack(pady=5)
        tk.Button(adminlogin, width = 5,text="Enter", command=lambda:self.check_admin(adminlogin, input_password)).pack(pady=10)
        
        #input_password = int(input("password: "))
        
    def check_admin(self,adminlogin, input_password):
        try:
            input_password = int(input_password.get())
            if self.admin_password == input_password:
                adminwin = tk.Tk()
                adminwin.title("Admin Menu")
                adminwin.geometry("200x300")
                adminwin.resizable(width=False, height=False)
                #admin 기능 버튼 추가
                tk.Button(adminwin,text="View all accounts",command=lambda:self.showallacounts(adminwin)).grid(row=5,column=10,padx = 40,pady=20)
                tk.Button(adminwin,text="Delete an account",command=lambda:self.deleteaccountcheck(adminwin)).grid(row=10,column=10,padx = 40,pady=20)
                tk.Button(adminwin,text="Back to main menu",command=lambda:self.adminwin.destroy).grid(row=15,column=10,padx = 40,pady=20)

                adminlogin.destroy()
            else:
                messagebox.showerror("Error","Wrong password")
        except ValueError:
            messagebox.showerror("Error","Invalid integer input")
        
    def showallacounts(self,adminwin):
        #전체 계좌 목록 조회. 
        
        #새 창 열기
        allaccounts = tk.Toplevel(adminwin)
        allaccounts.title("All Accounts")
        allaccounts.geometry("800x500")
        
        cur.execute("SELECT id, number, pin, balance FROM card;")
        accounts = cur.fetchall()
        #print("\nAll Accounts:")
        for account in accounts:
            tk.Label(allaccounts,text=f"ID: {account[0]}, Number: {account[1]}, PIN: {account[2]}, Balance: {account[3]}").pack(pady=5)
            #print(f"ID: {account[0]}, Number: {account[1]}, PIN: {account[2]}, Balance: {account[3]}")
    
    def deleteaccountcheck(self,adminwin):
        #특정 계정 삭제 
        delaccwin = tk.Toplevel(adminwin)
        delaccwin.title("Delete Account")
        delaccwin.geometry("300x100")
        #d  elaccwin.grab_set()
        
        tk.Label(delaccwin, text="Enter card number to delete:").pack(pady=5)
        delaccount = tk.Entry(delaccwin, width=20)
        delaccount.pack(pady=5)
        tk.Button(delaccwin, text="Delete", command=lambda:self.deleteaccount(delaccount,delaccwin),width=5).pack(pady=10)
    def deleteaccount(self,delaccount,delaccwin):
        try:
            delete_card = delaccount.get()
            cur.execute("SELECT * FROM card WHERE number = ?;",(delete_card,))
            if cur.fetchone():
                delaccwin.destroy()
                cur.execute("DELETE FROM card WHERE number = ?;",(delete_card,))
                conn.commit()
                messagebox.showinfo("info","The account has been deleted!")
            else:
                print("Such a card does not exist.")
        except ValueError:
            messagebox.showerror("Error",self.translate('invalid_input'))
     
            '''     while (admin_password == input_password): 
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
                cur.execute("SELECT * FROM card WHERE number = ?;",(delete_card))
                if cur.fetchone():
                    cur.execute("DELETE FROM card WHERE number = ?;",(delete_card))
                    conn.commit()
                    print("The account has been deleted!")
                else:
                    print("Such a card does not exist.")
            elif i == 0: # 관리자 기능 종료
                break
            else:
                print(self.translate('invalid_input'))'''
       


    def menu(self): #메뉴 표시 메소드 1.계좌생성 2.로그인 9.영한변환 0.종료
        while True:
            print(self.translate('welcome'))

            i = int(input())
            if i == 1:
                self.create_account()
            elif i == 2:
                self.log_in()

            elif i == 3:
                self.admin_menu()

            elif i == 9:
                self.switch_language()

            elif i == 0:
                conn.close()
                print(self.translate('bye'))
                break
            else:
                print(self.translate('invalid_input'))
                

#instance 생성 후 menu 메소드 실행

root = tk.Tk()
card = Card(root)
root.mainloop()
#card.menu()