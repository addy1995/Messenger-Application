import socket               # Import socket module
import threading
import time
from queue import Queue
import pymysql
import pickle
from tkinter import *

tLock = threading.Lock()
LARGE_FONT = ("Verdana", 12)

class Client(Tk):
    # Create a socket object
    host = socket.gethostname()  # Get local machine name

    def __init__(self, val, *a, **ka):
        self.port = val
        Tk.__init__(self,*a,**ka)
        self.title("Messenger")
        self.container = Frame(self)
        self.container.pack()
        self.signin = StartPage(self.container, self)
        self.signin.grid(row=0, column=0, sticky='nsew',padx=5,pady=5)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.resizable(0, 0)
        while True:
            try:
                self.s.connect((socket.gethostname(), self.port))
                break
            except Exception as e:
                print(e)
                time.sleep(5)

    def listener(self,s):

        while True:
            rec = s.recv(4000)
            new = pickle.loads(rec)
            if new[0] == 1:
                self.q.put((1,new[1][0].capitalize(),new[1][1]))

            elif new[0] == 2:

                self.users = []
                for str in new[1]:
                    self.users.append(str.capitalize())
                self.users.remove(self.client.capitalize())

                self.mainpage.update()
                pass

            elif new[0] == 3:
                print("No such user " + new[1])

        pass

    def log_in(self):
        s = self.s
        username = self.signin.entry_1.get()
        password = self.signin.entry_2.get()
        username = username.strip()
        password = password.strip()
        login_details = (username.lower(), password)
        new = pickle.dumps(login_details, -1)
        s.send(new)
        reply = s.recv(1024)
        ans = pickle.loads(reply)
        if ans == 0:
            print("Incorrect Password")
        elif ans == -1:
            print("Username Doesn't Exist")
        elif ans == -2:
            print("Already logged in")
        elif ans == 1:
            print("Connected")
            self.client = username
            self.users = []
            self.to = None
            self.q = Queue()
            self.mainpage = MainPage(self.container, self)
            self.mainpage.grid(row=0, column=0, sticky='nsew')
            self.tkraise(self.mainpage)

            lT = threading.Thread(target=self.listener, args=[s], name='Listener')
            lT.daemon = True

            lT.start()
        pass

    def sendit(self):
        s = self.s

        string = self.mainpage.text.get(1.0,'end-1c')
        string = string.strip()
        if string !='' and self.to != None:
            self.q.put((2,'You',string))
            message = (self.to.lower(), string)
            message = pickle.dumps( message, -1)
            s.send(message)
            self.mainpage.text.delete(1.0,END)
        pass

class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        label_1 = Label(self,text='Username')
        label_2 = Label(self,text='Password')
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self)
        label_1.grid(row=0)
        label_2.grid(row=1)
        self.entry_1.grid(row=0,column=1)
        self.entry_2.grid(row=1, column=1)
        button = Button(self,text='Log in', command=controller.log_in)
        button.grid(row=2,columnspan=2,pady=2)


class MainPage(Frame,threading.Thread):
    def __init__(self, parent, controller):
        threading.Thread.__init__(self)
        Frame.__init__(self,parent)
        self.controller = controller
        self.listbox = Listbox(self)
        self.listbox.grid(rowspan=2, column=0, sticky='nswe',padx=5,pady=5)
        self.listbox.bind("<Double-Button-1>",lambda e:self.rename_1())
        self.chats = {}
        self.text = Text(self,font = LARGE_FONT,height=2,width=50)
        self.text.grid(row=1,sticky='nsw',column=1,padx=5,pady=5)
        self.text.insert(END,'sdfsdf')
        self.button = Button(self, text="Send",command=self.controller.sendit)
        self.button.grid(row=1,sticky='e',column=1)
        print(self.controller.winfo_width())
        print(self.controller.winfo_height())
        self.begin = 1
        self.daemon = True
        self.start()

    def run(self):

        while True:
            rec = self.controller.q.get()
            if rec[0]==1:
                try:
                    self.chats[rec[1]]
                    main = self.chats[rec[1]]
                except:
                    main = Text(self, height=10, width=50, font=LARGE_FONT)
                    main.grid(row=0, column=1, sticky='nswe', padx=5, pady=5)
                    main.lower()
                    main.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                    self.chats[rec[1]] = main
                    pass
                main.configure(state='normal')
                main.tag_config('me', foreground='red')
                temp = main.index(CURRENT)
                main.insert(END,rec[1])
                main.tag_add('me', temp, CURRENT)
                main.insert(END, ': ' + rec[2] + '\n')
                main.configure(state='disabled')
            else:
                main = self.chats[self.controller.to.capitalize()]
                main.configure(state='normal')
                main.tag_config('other', foreground='green')
                temp = main.index(CURRENT)
                main.insert(END, rec[1])
                main.tag_add('other', temp, CURRENT)
                main.insert(END, ': ' + rec[2] + '\n')
                main.configure(state='disabled')
        pass

    def rename_1(self):
        tup = self.listbox.curselection()
        print(1)
        if len(tup)!=0:
            self.controller.to = self.listbox.get(tup[0])
            main = self.chats[self.controller.to]
            main.grid(row=0, column=1, sticky='nswe', padx=5, pady=5)
            main.lift()

    def update(self):
        self.listbox.delete(0,END)
        print(self.controller.to)
        for a in self.controller.users:
            try:
                self.chats[a]
                self.chats[a].grid(row=0, column=1, sticky='nswe', padx=5, pady=5)
            except:
                temp = Text(self, height=10, width=50, font=LARGE_FONT)
                temp.grid(row=0, column=1, sticky='nswe', padx=5, pady=5)
                temp.lower()
                temp.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                self.chats[a] = temp

        for a in self.controller.users:
            self.listbox.insert(END, a)

        if len(self.controller.users) == 0:
            self.controller.to = None
            self.button.configure(state='disabled')
            for a in list(self.chats.keys()):
                self.chats[a].grid_forget()
            pass
        else:
            if self.controller.to not in self.controller.users:
                self.controller.to = self.listbox.get(0)
                self.listbox.activate(0)
                self.chats[self.controller.to].grid(row=0, column=1, sticky='nswe', padx=5, pady=5)
                self.chats[self.controller.to].lift()
                self.button.configure(state='normal')
                pass
            else:
                pass

        print(self.controller.to)

if __name__ == '__main__':
    a = Client(12345)
    a.mainloop()
