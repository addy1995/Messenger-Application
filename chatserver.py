import socket               # Import socket module
import time
import os
import pickle
import sqlite3
import threading

clients = []
new = []
tLock = threading.Lock()

db_filename = 'Chat-server.db'
schema_filename = 'create_schema.sql'

db_is_new = not os.path.exists(db_filename)

if db_is_new:
    print("First Add user through add_user.py")
    exit()


db = sqlite3.connect(db_filename)
cursor = db.cursor()
sql = "SELECT * FROM CREDENTIALS"
cursor.execute(sql)
users_list = cursor.fetchall()
db.close()

print(users_list)


def notify(gone, c = None):
    print(new)

    if c is not None:
        dat = pickle.dumps((3, gone),-1)
        c.send(dat)
    else:
        dat = pickle.dumps((2, new), -1)
        for client in clients:

            client[1].send(dat)
            pass


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
                print(ans)
                if login_details[0] in new:
                    ans = -2

                c.send(pickle.dumps(ans,-1))
                if ans == 1:
                    clients.append((login_details[0],c))

                    new.append(login_details[0])
                    notify(login_details[0])
                tLock.release()

        except Exception as e:
            print(e)
            continue
            pass

        finally:
            pass

        print(login_details[0] + ' Connected')

        string = ''
        try:
            while True:
                string = c.recv(4000)
                string = pickle.loads(string)
                tLock.acquire()
                if string[0] not in new:
                    notify(string[0], c)
                else:
                    for client in clients:
                        if client[1] != c and client[0]==string[0]:
                            newdat = pickle.dumps((1,(login_details[0],string[1])),-1)
                            client[1].send(newdat)
                tLock.release()

        except ConnectionResetError as cre:

            tLock.acquire()
            clients.remove((login_details[0],c))
            new.remove(login_details[0])
            notify(login_details[0])
            tLock.release()
            print(login_details[0] + ' disconnected')
            pass
        except Exception as e:
            print(e)
        finally:
            c.close()  # Close the connection
    s.close()


def authenticating(login_details):
    for user in users_list:
        if user[0].lower()==login_details[0]:
            if user[1]==login_details[1]:
                return 1
            else:
                return 0
    return -1


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
s.listen(10)               # Now wait for client connection.

aT = []
for i in range(10):
    aT.append(threading.Thread(target=accepting , args=[s,i]))
    aT[i].start()
