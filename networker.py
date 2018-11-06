import communicator
import time

import socket
import pickle
import select

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

coms = communicator.communications()
print("NEW NET CODE BITCHES")

while 1:
    conn, addr = s.accept()
    print("Connection address: ", addr)
    conn.setblocking(0)

    try:
        while 1:
            #rread, rwrite, rerror = \
            #    select.select([conn], [], [])
            #print(int(round(time.time() * 1000)))
            #if not rread:
            #    print("Not blocked")
            for c in [conn]:
                try:
                    command = c.recv(5).decode()
                    print(command)

                    if command == "?":
                        params = coms.get_parameters()
                        c.send(pickle.dumps(params))
                    else:
                        if command != ".":
                            coms.command(command)
                        values = coms.get_data()
                        c.send(pickle.dumps(values))
                except Exception as e:
                    if("Errno 32" in str(e)):
                        raise

            coms.check_data()
            time.sleep(0.010)
    except Exception as e:
        print(e)

#while 1:
#    conn, addr = s.accept()
#    print("Connection address: ", addr)
#
#    try:
#        while 1:
#            command = conn.recv(5).decode()
#            print(command)
#
#            if command == "?":
#                params = coms.get_parameters()
#                conn.send(pickle.dumps(params))
#            else:
#                if command != ".":
#                    coms.command(command)
#                values = coms.get_data()
#                conn.send(pickle.dumps(values))
#    except Exception as e:
#        print(e)
