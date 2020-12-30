import socket
import threading
import sys
import os
import struct
import random
import colorama
from select import select
from scapy.arch import get_if_addr
import time


class Client():
    def __init__(self, IP, PORT):
        self.ip = IP
        self.port = PORT
        self.teamName = "#TODO: GET 100 AND GO HOME\n"
        self.broadcastIP = '.'.join(IP.split('.')[:2]) + '.255.255'
        self.listenToBroadcast()

    def listenToBroadcast(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            text = "Client started, listening for offer requests..."
            self.pretty_print(text)
            try:
                # TODO: check if its ok not on localhost
                s.bind((self.broadcastIP, self.port))
            except:
                time.sleep(0.2)
                continue
            # Binds client to listen on port self.port. (will be 13117)
            while True:
                # Receives Message
                try:
                    message, address = s.recvfrom(1024)
                    magic_cookie = message[:4]
                    message_type = message[4]
                    port_tcp = int.from_bytes(
                        message[5:], byteorder='big', signed=False)
                    text = f"Received offer from {address[0]}, attempting to connect..."
                    self.pretty_print(text)
                    if magic_cookie == bytes.fromhex('feedbeef') or message_type == 2:
                        self.connectTCPServer(address[0], port_tcp)
                except:
                    print("Not connecting, Trying another server...")
                    continue
                break
            s.close()

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
                # TODO: CHANGE IP TO NON LOCAL
                s.connect((ip_tcp, port_tcp))
                break
            except:
                return

        # Sending team name
        s.send(bytes(self.teamName, encoding='utf8'))

        # Receive data from Server - start game

        incoming_data = select([s], [], [], 11)
        if incoming_data:
            data = str(s.recv(1024), 'utf-8')
            self.pretty_print(data)
        else:  # server disconnected before game started, we waited for him 11 seconds to start the stuupid game
            s.close()
            return

        # Setting blocking to false, Data to none and removing key presses representation
        data = None
        s.setblocking(False)
        os.system("stty raw -echo")
        start_time = time.time()
        while time.time() - start_time < 11:
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
                rlist, _, _ = select([sys.stdin], [], [], 0.1)
                if rlist:
                    c = sys.stdin.read(1)
                    s.send(bytes(c, encoding='utf8'))
        os.system("stty -raw echo")
        s.close()
        self.pretty_print(
            "Server disconnected, listening for offer requests...")


my_client = Client(get_if_addr('eth1'), 13116)
