import socket
import sys
import io
from random import randint

HOST = '192.168.43.56'
PORT = 10000
s = socket.socket()
s.connect((HOST, PORT))

CHUNK_SIZE = 8 * 1024
MSG_SIZE = 4096

print(s)

while 1:
    msg = input("-> ")
    if msg == "close":
       s.close()
       sys.exit(0)

    s.send(msg.encode())

    if msg == 'snap':
        fileSize = int(s.recv(MSG_SIZE).decode())
        print(fileSize)
        recSize = 0
        with open('./test.jpg','wb') as fh:
            while True:
                chunk = s.recv(CHUNK_SIZE)
                recSize = recSize + len(chunk)
                fh.write(chunk)
                percent = int( (recSize / fileSize) * 90 )
                if percent % 10 == randint(0,10) : print(str(percent) + "|" * percent)
                if recSize >= fileSize:
                    print("Received all the bytes")
                    break
                    s.close()


        print("Received!")
