import socket
import threading
import sys
import os
import struct
import random
import colorama


class Client():
    def __init__(self, IP, PORT):
        self.ip = IP
        self.port = PORT
        self.teamName = "Bullshit-Name\n"

    def listenToBroadcast(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        text = "Client started, listening for offer requests..."
        self.pretty_print(text)
        # Binds client to listen on port self.port. (will be 13117)
        while True:
            try:
                s.bind(('', self.port))  # TODO: check if its ok not on localhost
            except:
                continue
            # Receives Message
            message, address = s.recvfrom(1024)
            try:
                magic_cookie, message_type, port_tcp = struct.unpack('Ibh', message)
                text = f"Received offer from {address[0]}, attempting to connect..."
                self.pretty_print(text)
            except:
                continue

            if magic_cookie != 0xfeedbeef: continue
            break

        self.connectTCPServer(address[0], port_tcp)

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]

        print(''.join(colored_chars))

    def connectTCPServer(self, ip_tcp, port_tcp):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to tcp server
        while True:
            try:
                s.connect(('localhost', port_tcp))  # TODO: CHANGE IP TO NON LOCAL
                break
            except:
                pass  # TODO: DONT GET INTO INFINITE LOOP!

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
                self.pretty_print(data)
                break
            else:
                c = sys.stdin.read(1)
                s.send(bytes(c, encoding='utf8'))

        s.close()
