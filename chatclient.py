import socket
import threading
import time
from queue import Queue
import pickle
from tkinter import *
from tkinter import messagebox
import os
import sqlite3


tLock = threading.Lock()
LARGE_FONT = ("Verdana", 12)

db_filename = 'Chat-client.db'
db_is_new = not os.path.exists(db_filename)
db = sqlite3.connect(db_filename,check_same_thread=False)
new_messages = []


class Client(Tk):
    # Create a socket object
    host = socket.gethostname()  # Get local machine name

    def __init__(self, val, *a, **ka):
        self.port = val
        Tk.__init__(self,*a,**ka)
        self.title("Messenger")
        self.container = Frame(self)
        self.container.pack()
        self.create_startpage(val)
        self.resizable(0, 0)

    def create_startpage(self,val):
        self.signin = StartPage(self.container, self)
        self.signin.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.s.connect((socket.gethostname(), self.port))
                break
            except Exception as e:
                print(e)
                time.sleep(5)


    def listener(self,s):
        try:
            while True:
                rec = s.recv(4000)
                new = pickle.loads(rec)
                if new[0] == 1:
                    self.q.put((1, new[1][0].capitalize(), new[1][1]))
                    new_messages.append((new[1][0], 1, new[1][1]))
                elif new[0] == 2:
                    self.users = []
                    for str in new[1]:
                        self.users.append(str.capitalize())
                    self.users.remove(self.client.capitalize())
                    self.mainpage.update()
                    pass
                elif new[0] == 3:
                    print("No such user " + new[1])

        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()
        except ConnectionAbortedError as e:
            print(e)
            pass

    def log_in(self):
        try:
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
                self.client = username.lower()
                self.users = []
                self.to = None
                self.q = Queue()
                self.mainpage = MainPage(self.container, self)
                self.mainpage.grid(row=0, column=0, sticky='nsew')
                self.signin.destroy()
                self.tkraise(self.mainpage)
                lT = threading.Thread(target=self.listener, args=[s], name='Listener')
                lT.daemon = True
                lT.start()
        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()

    def sendit(self):
        s = self.s

        string = self.mainpage.text.get(1.0,'end-1c')
        string = string.strip()
        if string !='' and self.to != None:
            self.q.put((2,'You',string))
            message = (self.to.lower(), string)
            message = pickle.dumps( message, -1)
            s.send(message)
            new_messages.append((self.to,2,string))

            self.mainpage.text.delete(1.0,END)
        pass

    def log_out(self):
        for to, no, message in new_messages:

            db.execute('insert into {}_{} values(?,?)'.format(a.client, to), (no, message))
        try:
            self.s.close()
        except Exception as e:
            print(e)
        db.commit()
        new_messages.clear()
        self.mainpage.destroy()
        self.q.put((-1, 0, 0))
        self.mainpage.chats.clear()
        self.create_startpage(self.port)


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        label_1 = Label(self,text='Username')
        label_2 = Label(self,text='Password')
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self, show="*")
        self.entry_1.bind("<Return>", lambda e: controller.log_in())
        self.entry_2.bind("<Return>", lambda e: controller.log_in())
        label_1.grid(row=0)
        label_2.grid(row=1)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)
        button = Button(self,text='Log in', command=controller.log_in)
        button.grid(row=2,columnspan=2)


class MainPage(Frame,threading.Thread):
    def __init__(self, parent, controller):
        threading.Thread.__init__(self)
        Frame.__init__(self,parent)
        self.controller = controller

        menu = Menu(self,tearoff=0)
        menu.add_command(label=u'Block')

        self.sideframe = Frame(self)
        self.listbox = Listbox(self.sideframe)
        self.listbox.pack(fill=BOTH,expand=True,side=TOP,pady=5)
        self.listbox.bind("<1>",lambda e:self.rename_1(e))
        aqua = self.controller.call('tk', 'windowingsystem') == 'aqua'
        self.listbox.bind('<2>' if aqua else '<3>',  lambda e: self.listbox_menu(e, menu))
        self.listbox.bind("<Key>", self.no_op)
        self.label = Label(self.sideframe,text=self.controller.client.capitalize())
        self.logout = Button(self.sideframe,text="Log Out",command=self.controller.log_out)
        self.logout.pack(side=RIGHT)
        self.label.pack(side=LEFT)
        self.sideframe.grid(row=0,rowspan=3, column=0, sticky='nswe',padx=5,pady=5)
        self.current = Label(self)
        self.current.grid(row=0, column=1, pady=5, )
        self.chats = {}
        self.text = Text(self,font = LARGE_FONT,height=2,width=50)
        self.text.grid(row=2,sticky='nswe',column=1,padx=5,pady=5)
        self.text.bind("<Return>",lambda e:self.controller.sendit())
        self.button = Button(self, text="Send",command=self.controller.sendit)
        self.button.grid(row=2,sticky='w',column=2)
        print(self.controller.winfo_width())
        print(self.controller.winfo_height())
        self.begin = 1
        self.daemon = True
        self.start()

    def listbox_menu(self, event, menu):
        if self.listbox.size() == 0:
            return
        widget = event.widget
        index = widget.nearest(event.y)
        _, yoffset, _, height = widget.bbox(index)
        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            # Outside of widget.
            return
        item = widget.get(index)
        print("Do something with", index, item)
        menu.post(event.x_root, event.y_root)

    def no_op(self,event):
        return "break"

    def run(self):

        while True:
            rec = self.controller.q.get()
            if rec[0]==1:
                try:
                    self.chats[rec[1]]
                    main = self.chats[rec[1]][0]
                except:
                    s = Scrollbar(self)
                    s.grid(row=1, column=3, sticky='ns')
                    main = Text(self, height=10, width=50, font=LARGE_FONT)
                    main.grid(row=1, columnspan=2,column=1, sticky='nswe', padx=5, pady=5)
                    s.config(command=main.yview)
                    main.config(yscrollcommand=s.set)
                    main.lower()
                    s.lower()
                    main.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                    main.tag_config('other', foreground='red')
                    main.tag_config('me', foreground='green', justify=RIGHT, lmargin1=100)
                    main.tag_config('justify', lmargin2=100)
                    self.chats[rec[1]] = (main, s)
                    pass
                main.configure(state='normal')
                main.insert(END, rec[1], 'other')
                main.insert(END, ': ' + rec[2] + '\n')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == 2:
                main = self.chats[self.controller.to][0]
                main.configure(state='normal')
                main.insert(END, rec[1], 'me')
                main.insert(END, ': ' + rec[2] + '\n', 'justify')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == -1:
                break
        pass

    def old_messages(self,dat ,user):

        main = self.chats[user][0]
        for sender, message in dat:
            if sender == 2:
                main.configure(state='normal')
                main.insert(END, 'You', 'me')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
            else:
                main.configure(state='normal')
                main.insert(END, user, 'other')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
                pass
        main.see(END)

        pass

    def rename_1(self,event):

        if self.listbox.size() == 0:
            return
        index = self.listbox.nearest(event.y)
        _, yoffset, _, height = self.listbox.bbox(index)
        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            return
        print(1)
        self.controller.to = self.listbox.get(index)
        self.current.config(text=self.controller.to)
        main = self.chats[self.controller.to][0]
        temp = self.chats[self.controller.to][1]
        main.grid(row=1, columnspan=2,column=1, sticky='nswe', padx=5, pady=5)
        temp.grid(row=1, column=3, sticky='ns')
        temp.lift()
        main.lift()

    def update(self):
        self.listbox.delete(0,END)

        for user in self.controller.users:
            try:
                self.chats[user]
                self.chats[user][0].grid(row=1, columnspan=2,column=1, sticky='nswe', padx=5, pady=5)
                self.chats[user][1].grid(row=1, column=3, sticky='ns')
                self.listbox.insert(END, user)

            except:
                s = Scrollbar(self)
                temp = Text(self, height=10, width=50, font=LARGE_FONT)
                temp.grid(row=1, columnspan=2,column=1, sticky='nswe', padx=5, pady=5)
                s.grid(row=1, column=3,sticky='ns')
                s.config(command=temp.yview)
                temp.config(yscrollcommand=s.set)
                temp.lower()
                s.lower()
                temp.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                temp.tag_config('other', foreground='red')
                temp.tag_config('me', foreground='green', justify=RIGHT, lmargin1=100)
                temp.tag_config('justify', lmargin2=100,lmargin1=100)
                self.chats[user] = (temp, s)
                self.listbox.insert(END, user)
                try:
                    cur = db.cursor()
                    cur.execute("""select * from {}_{}""".format(self.controller.client,user))
                    dat = cur.fetchall()
                    self.old_messages(dat,user)
                    pass
                except:
                    db.execute('create table {}_{}( sender INT, message VARCHAR(40))'.format(self.controller.client, user))

                    pass

        if len(self.controller.users) == 0:
            self.controller.to = None
            self.current.config(text='')
            self.button.configure(state='disabled')
            for a in list(self.chats.keys()):
                self.chats[a][0].grid_forget()
                self.chats[a][1].grid_forget()
            pass
        else:
            if self.controller.to not in self.controller.users:
                self.controller.to = self.listbox.get(0)
                self.current.config(text=self.controller.to)
                self.listbox.activate(0)
                self.chats[self.controller.to][0].grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                self.chats[self.controller.to][1].grid(row=1, column=3, sticky='ns')
                self.chats[self.controller.to][0].lift()
                self.chats[self.controller.to][1].lift()
                self.button.configure(state='normal')
                pass
            else:
                pass
        print(self.controller.to)

if __name__ == '__main__':
    a = Client(12345)
    a.mainloop()
    for to, no, message in new_messages:
        db.execute('insert into {}_{} values(?,?)'.format(a.client, to), (no, message))
    try:
        a.s.close()
    except Exception as e:
        print(e)
    db.commit()
    new_messages.clear()
    db.close()