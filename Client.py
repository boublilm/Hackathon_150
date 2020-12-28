import socket
import threading
import sys
import os
import time
import random
import colorama


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
        text = "Client started, listening for offer requests..."
        self.pretty_print(text)
        # Binds client to listen on port self.port. (will be 13117)
        try:
            s.bind(('', self.port))
        except:
            self.listen()
        # Receives Message
        message = s.recvfrom(1024)[0]

        # Message Teardown.
        # magic_cookie = message[:4]
        # message_type = message[4]
        port_tcp = message[5:]
        self.connectTCPServer(int.from_bytes(
            port_tcp, byteorder='big', signed=False))

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]

        print(''.join(colored_chars))

    def connectTCPServer(self, ip_tcp, port_tcp):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to tcp server
        s.connect((self.ip, port_tcp))

        # Sending team name
        s.send(bytes(self.teamName, encoding='utf8'))

        # Receive data from Server
        data = str(s.recv(1024), 'utf-8')
        self.pretty_print(data)

        # Setting blocking to false, Data to none and removing key presses representation
        data = None
        s.setblocking(False)
        os.system("stty raw -echo")
        while True:
            # if data is recieved it will stop and print, else it will send every key press to the server.
            try:
                data = s.recv(1024)
            except:
                pass
            if data:
                os.system("stty -raw echo")
                data = str(data, 'utf-8')
                self.receievedData = True
                self.pretty_print(data)
                break
            else:
                c = sys.stdin.read(1)
                s.send(bytes(c, encoding='utf8'))
        s.close()
