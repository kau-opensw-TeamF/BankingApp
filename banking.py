
import random
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox
random.seed()

#sqlite3 DB
conn = sqlite3.connect('card.s3db')#이전에 명명된 db와 연결
cur = conn.cursor() #cursor object 생성으로 sql script 동작
# cur.execute("DROP TABLE card")
# card 테이블이 없는 경우 생성
cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER PRIMARY KEY,number TEXT,pin TEXT,balance INTEGER DEFAULT 0);")
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
        
        
        # 실행부분을 init으로 옮겨야 함. main에서 실행할 수 없음.
        self.main_window()
        
        
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

        tk.Label(self.root, text="기능을 선택해주세요").grid(row=0, column=1, pady=10)

        
        button1 = tk.Button(self.root, text="1. Create account", command=self.create_account, width=20, height=10)
        button2 = tk.Button(self.root, text="2. Log in", command=self.log_in, width=20, height=10)
        button3 = tk.Button(self.root, text="3. Exit", command=self.exit, width=20, height=10)

        button1.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        button2.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        button3.grid(row=1, column=2, padx=10, pady=10, sticky='nsew')


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
        
        #self.login_card = input("Enter your card number:\n")
        #self.login_pin = input("Enter your PIN:\n")
        login_win = tk.Toplevel(self.root)
        login_win.title("Log In")
        login_win.geometry("350x200")
        
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
            messagebox.showerror("error","wrong card number or pin")
        '''elif not self.luhn_2(self.login_card):
                print('Probably you made a mistake in the card number. Please try again!') '''

                
    def success(self): #1.자산확인 2.입금기능 3.송금기능 4.계좌폐쇄 5.로그아웃 0.종료
        myaccount = tk.Toplevel(root)
        myaccount.title("My Account")
        myaccount.geometry("350x600")
        myaccount.resizable(width=False, height=False)
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
        
    



#instance 생성 후 menu 메소드 실행

root = tk.Tk()
card = Card(root)
root.mainloop()
#card.menu()