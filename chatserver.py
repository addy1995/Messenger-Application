import socket               # Import socket module
import os
import pickle
import sqlite3
import threading

clients = []
new = []
tLock = threading.Lock()

server_IP = ''  # Set Server IP here

db_filename = 'Chat-server.db'
schema_filename = 'create_schema.sql'

db_is_new = not os.path.exists(db_filename)

if db_is_new:
    print("First Add user through add_user.py")
    exit()


db = sqlite3.connect(db_filename,check_same_thread=False)
cursor = db.cursor()
sql = "SELECT * FROM CREDENTIALS"
cursor.execute(sql)
users_list = cursor.fetchall()


print(users_list)

def notify(option=None,user=None, c=None):
    if option == 0:
        dat = pickle.dumps((2, new), -1)
        for client in clients:
            if client[1]!=c:
                try:
                    client[1].send(dat)
                except Exception as e:
                    print(e,'first')

            pass
    elif option == 1:
        dat = pickle.dumps((4, user), -1)
        try:
            c.send(dat)
        except Exception as e:
            print(e, 'second')

        pass
    else:
        dat = pickle.dumps((3, user),-1)
        try:
            c.send(dat)
        except Exception as e:
            print(e, 'third')

def accepting(s, name):
    while True:
        try:
            c, addr = s.accept()
            print('Got connection from', addr, name)
            ans = 0

            while ans != 1:
                login_details = c.recv(1024)
                login_details = pickle.loads(login_details)
                ans = authenticating(login_details)
                tLock.acquire()
                if login_details[0] in new:
                    ans = -2

                c.send(pickle.dumps(ans,-1))
                if ans == 1:
                    clients.append((login_details[0],c))
                    new.append(login_details[0])

                tLock.release()

        except Exception as e:
            print(e,'fourth')
            continue
            pass

        finally:
            pass
        tLock.acquire()
        print(login_details[0] + ' Connected')
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM {}_blocked_users".format(login_details[0]))
            notify(1,(new,cursor.fetchall()),c)
            notify(0,None,c)
        except Exception as e:
            db.execute("CREATE TABLE {}_blocked_users(username VARCHAR(4000) NOT NULL PRIMARY KEY)".format(login_details[0]))
            notify(0, None, c)
            print(e, 'fifth')

        tLock.release()
        string = ''
        try:
            while True:
                rec = c.recv(4000)

                arr = rec.split(b'.')
                for val in range(len(arr)-1):
                    string = pickle.loads(arr[val] + b'.')
                    tLock.acquire()
                    if string[0] == 1:
                        if string[1] not in new:
                            notify(2,string[1], c)
                        else:
                            for client in clients:
                                if client[1] != c and client[0]==string[1]:
                                    newdat = pickle.dumps((1,(login_details[0],string[2])),-1)
                                    client[1].send(newdat)
                    elif string[0] == 2:
                        op = (string[1],)
                        try:
                            db.execute("INSERT INTO {}_blocked_users VALUES( ? )".format(login_details[0]),op)
                            db.commit()
                        except:
                            pass
                        pass
                    else:
                        op = (string[1],)
                        try:
                            db.execute("DELETE FROM {}_blocked_users WHERE username = ?".format(login_details[0]),op)
                            db.commit()
                        except:
                            pass
                    tLock.release()
        except Exception as e:
            tLock.acquire()
            clients.remove((login_details[0],c))
            new.remove(login_details[0])
            notify(0, None, c)
            tLock.release()
            print(login_details[0] + ' disconnected')
            print(e, 'sixth')
            pass

        finally:
            c.close()  # Close the connection



def authenticating(login_details):
    for user in users_list:
        if user[0].lower() == login_details[0]:
            if user[1] == login_details[1]:
                return 1
            else:
                return 0
    return -1


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((server_IP, port))        # Bind to the port
s.listen(100)               # Now wait for client connection.

aT = []
for i in range(10):
    aT.append(threading.Thread(target=accepting , args=[s,i]))
    aT[i].start()


