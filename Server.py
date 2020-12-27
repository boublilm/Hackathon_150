import socket
import time
import threading
import random
from _thread import start_new_thread


class Server():
    def __init__(self, IP, PORT, broadcastPort):
        self.ip = IP
        self.port = PORT
        self.toBroadcast = True
        self.broadcastPort = broadcastPort
        self.num_particants = 0
        self.startTCPServer()
        self.teams = []
        self.scores = [0, 0]
        self.lock = threading.Lock()

    def startTCPServer(self):
        # Starts TCP Server via a thread.
        thread = threading.Thread(target=self.TCPServer)
        thread.start()

    def clientHandler(self, c):
        TeamName = str(c.recv(1024), 'utf-8')
        self.teams += [TeamName]*4
        while self.num_particants < 1:
            time.sleep(0.5)

        c.send(bytes(
            f"Welcome to Keyboard Spamming Battle Royale.\n\
Group 1:\n\
==\n\
{self.teams[0]}\
{self.teams[1]}\
Group 2:\n\
==\n\
{self.teams[2]}\
{self.teams[3]}\
\nStart pressing keys on your keyboard as fast as you can!!", encoding='utf8'))

        index = self.teams.index(TeamName) // 2
        start_time = time.time()
        while time.time() - start_time < 10:
            # data received from client
            data = c.recv(1024)
            if not data:
                continue
            self.scores[index] += 1

        # send back string to client
        winner = 0 if (self.scores[0] > self.scores[1]) else 1
        message = f"Game over!\nGroup 1 typed in {self.scores[0]} characters. Group 2 typed in {self.scores[1]} characters.\nGroup {winner+1} wins!\n\nCongratulations to the winners:\n==\n{self.teams[winner*2]}{self.teams[winner*2+1]}"
        c.send(bytes(message, encoding='utf8'))
        # print(self.scores)
        # connection closed
        c.close()

    def TCPServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.port))
        print(f"Server started, listening on IP address {self.ip}")
        self.startBroadcasting()
        s.listen(4)
        while True:

            # establish connection with client
            c, addr = s.accept()

            self.lock.acquire()
            self.num_particants += 1
            if self.num_particants == 1:
                random.shuffle(self.teams)
            self.lock.release()

            # Start a new thread and return its identifier
            start_new_thread(self.clientHandler, (c,))
        s.close()

    def startBroadcasting(self):
        # Starts Broadcasting via a thread.
        thread = threading.Thread(target=self.broadcast)
        thread.start()

    def stopBroadcasting(self):
        # Sets the broadcast loop's statement to false, thus -> will stop broadcasting.
        self.toBroadcast = False

    def broadcast(self):
        server = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable port reusage
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        server.settimeout(0.2)
        magic_cookie = "feedbeef"
        message_type = "02"
        x = bytes.fromhex(magic_cookie)
        y = bytes.fromhex(message_type)
        z = self.port.to_bytes(2, byteorder='big')
        message = x + y + z

        while self.broadcast:
            server.sendto(message, ('<broadcast>', self.broadcastPort))
            time.sleep(1)
