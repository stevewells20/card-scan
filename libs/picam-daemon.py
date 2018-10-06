import threading
import os, io, base64, time, socket, picamera, daemon

MAX_LENGTH = 4096 # max length of any possible entry from "client"
CHUNK_SIZE = 8 * 1024

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # setup socket
PORT = 10000 # port 10000
HOST = '192.168.43.56' # runs on local host

serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # this allows us to override port, prevents error
serversocket.bind((HOST, PORT)) # lock server to this port and host
serversocket.listen(10) # max 10 clients

# Waits for commands, such as "snap" and "ack"
# Runs over "sockets"
def handle(clientsocket):
    while 1:
        buf = clientsocket.recv(MAX_LENGTH).decode()
        print(buf)
        # Receive the SNAP command. Take a picture with PiCam.
        if buf == 'snap':
            print("Client sent: 'snap'")
            start = time.time()

            # Create IO buffer for in memory picture storage
            imgBuf = io.BytesIO()

            camera.capture(imgBuf, format='jpeg')
            print('Picture Taken!')

            # Need to remove file saving in favor of socket.send()
            with open('/home/pi/card-cap/test.jpg','wb') as fh:
                fh.write(imgBuf.getvalue())
            print('Picture Saved!')

            bufSize = imgBuf.seek(0, io.SEEK_END)
            clientsocket.send(str(bufSize).encode())

            bufSent = 0
            with open('/home/pi/card-cap/test.jpg','rb') as fh2:
                while bufSent < bufSize:
                    bufSent = bufSent + clientsocket.send(fh2.read(MAX_LENGTH))
                    # print("{}/{}".format(bufSent, bufSize))

            finish = start - time.time()
            print(finish)

        if buf == 'ack':
            print ('Ping: Hello!')

        if len(buf) == 0: break

# Camera is always loaded here
# The "magic" is in the camThread, this allows a picture to be captured, then it gracefully closed the camera connection and reopens it. This produces very fast captures (54ms vs 1.5s!)
while 1:
    # setup camera
    camera = picamera.PiCamera()
    #camera.resolution = (640, 480)
    camera.resolution = (2592, 1944)
    #camera.zoom = (0.2, 0.2, 1.0, 1.0)
    camera.exposure_mode = 'sports'
    print('Camera server running')

    # accept connections from outside, in order to receive commands
    (clientsocket, address) = serversocket.accept()
    ct = threading.Thread(target=handle, args=(clientsocket,))
    ct.run() # this can be run(), because it can be scaled.

    print('Camera thread starting.')
    camThread = threading.Thread()
    while camThread.is_alive():
        camThread.join(1)
    camThread.run() # this must be start(), otherwise PiCam will crash. This is because PiCam cannot receive more than 1 connection.
    print('Camera thread ended')
    camera.close() # Gracefully close PiCam if client disconnects
