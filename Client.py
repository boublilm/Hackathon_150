import socket
import threading
import sys
import os
import time
from termcolor import colored, cprint


class Client():
    def __init__(self, IP, PORT):
        self.ip = IP
        self.port = PORT
        self.teamName = "Bullshit-Name\n"
        self.receievedData = False

    def listenToBroadcast(self):
        # Creates a thread to start listening for broadcasts.
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Binds client to listen on port self.port. (will be 13117)
        s.bind(('', self.port))
        # print()
        cprint("Client started, listening for offer requests...",
               'green', 'on_magenta')

        # Receives Message
        message, address = s.recvfrom(1024)

        # Message Teardown.
        magic_cookie = message[:4]
        message_type = message[4]
        port_tcp = message[5:]
        self.connectTCPServer(int.from_bytes(
            port_tcp, byteorder='big', signed=False))

    def dataReceive(self, s):
        data = None
        while not self.receievedData:
            data = str(s.recv(1024), 'utf-8')
            if data:
                self.receievedData = True
                os.system("stty -raw echo")
                cprint(data, 'cyan', 'on_red', attrs=['bold'])

    def connectTCPServer(self, port_tcp):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, port_tcp))
        s.send(bytes(self.teamName, encoding='utf8'))
        data = str(s.recv(1024), 'utf-8')
        cprint(data, 'cyan', 'on_red', attrs=['bold'])
        thread = threading.Thread(target=self.dataReceive, args=(s,))
        thread.start()
        while not self.receievedData:
            os.system("stty raw -echo")
            c = sys.stdin.read(1)
            s.send(bytes(c, encoding='utf8'))
            os.system("stty -raw echo")
        s.close()
