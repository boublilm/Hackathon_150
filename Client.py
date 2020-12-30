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
        self.teamName = "#TODO: GET 100 AND GO HOME"
        self.broadcastIP = '.'.join(IP.split('.')[:2]) + '.255.255'
        self.listenToBroadcast()

    def listenToBroadcast(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            text = "Client started, listening for offer requests..."
            self.pretty_print(text)
            try:
                s.bind((self.broadcastIP, self.port))
            except:
                s.close()
                time.sleep(0.2)
                continue

            # Binds client to listen on port self.port. (will be 13117)
            while True:
                try:  # Receives Message
                    message, address = s.recvfrom(1024)
                    magic_cookie, message_type, port_tcp = struct.unpack(">IbH", message)

                    text = f"Received offer from {address[0]}, attempting to connect..."
                    self.pretty_print(text)
                    # Drop message if magic cookie is wrong \ not type 2
                    if magic_cookie == bytes.fromhex('feedbeef') or message_type == 2:
                        s.close()
                        self.connectTCPServer(address[0], port_tcp)
                except:
                    time.sleep(0.2)
                    continue
                break

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]
        print(''.join(colored_chars))


    def connectTCPServer(self, ip_tcp, port_tcp):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(11)
        try: # connect to server via TCP
            s.connect((ip_tcp, port_tcp))
        except:
            return

        # Sending team name
        s.send(bytes(self.teamName + "\n", encoding='utf8'))

        # Receive data from Server - StartGame message
        incoming_data, a, b = select([s], [], [], 11)
        if incoming_data:
            data = str(s.recv(1024), 'utf-8')
            self.pretty_print(data)
        else:  # server disconnected before game started, we waited for him 11 seconds to start the stuupid game
            s.close()
            return

        # Playing
        data = None
        s.setblocking(False) # don't wait while s.recv
        os.system("stty raw -echo")  # removing key presses representation
        start_time = time.time()
        while time.time() - start_time < 11: # we wan't timeout in case server stops in the middle
            try: # check if EndGame packet received from server
                data = s.recv(1024)
            except:
                pass
            if data:  # server sent EndGame packet
                os.system("stty -raw echo")
                data = str(data, 'utf-8')
                self.pretty_print(data)
                break
            else:  # still typing
                character_coming, _, _ = select([sys.stdin], [], [], 0.1)
                if character_coming:
                    c = sys.stdin.read(1)
                    s.send(bytes(c, encoding='utf8'))

        # Game over
        os.system("stty -raw echo")
        s.close()
        self.pretty_print("Server disconnected, listening for offer requests...")


my_client = Client(get_if_addr('eth1'), 13117)
