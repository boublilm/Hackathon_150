import socket
import threading
import sys
import os
import time
import random
import colorama
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
        text = colorama.Fore.BLUE + "Client started, listening for offer requests..."
        self.pretty_print(text)
        # Binds client to listen on port self.port. (will be 13117)
        s.bind(('', self.port))
        # Receives Message
        message, address = s.recvfrom(1024)

        # Message Teardown.
        magic_cookie = message[:4]
        message_type = message[4]
        port_tcp = message[5:]
        self.connectTCPServer(int.from_bytes(
            port_tcp, byteorder='big', signed=False))

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]

        print(''.join(colored_chars))

    def dataReceive(self, s):
        data = None
        while not self.receievedData:
            data = str(s.recv(1024), 'utf-8')
            if data:
                self.receievedData = True
                os.system("stty -raw echo")
                self.pretty_print(data)

    def connectTCPServer(self, port_tcp):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, port_tcp))
        s.send(bytes(self.teamName, encoding='utf8'))
        data = str(s.recv(1024), 'utf-8')
        self.pretty_print(data)
        thread = threading.Thread(target=self.dataReceive, args=(s,))
        thread.start()
        while not self.receievedData:
            os.system("stty raw -echo")
            c = sys.stdin.read(1)
            s.send(bytes(c, encoding='utf8'))
            os.system("stty -raw echo")
        s.close()
