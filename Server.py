import socket
import time
import threading
import random
from _thread import start_new_thread
import colorama
import struct


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
        self.player_statistics = [{}, {}, {}, {}]
        self.player_key_press = [0, 0, 0, 0]
        self.start_game = False

    def startTCPServer(self):
        # Starts TCP Server via a thread.
        thread = threading.Thread(target=self.TCPServer)
        thread.start()

    def clientHandler(self, c):
        TeamName = str(c.recv(1024), 'utf-8')
        self.teams += [TeamName]
        while not self.start_game:
            time.sleep(0.5)

        team1 = ''.join(self.teams[:int(len(self.teams)/2)])
        team2 = ''.join(self.teams[int(len(self.teams)/2):])
        c.send(bytes(
            f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{team1}Group 2:\n==\n{team2}\nStart pressing keys on your keyboard as fast as you can!!", encoding='utf8'))

        index = self.teams.index(TeamName) // 2
        start_time = time.time()
        while time.time() - start_time < 10:
            # data received from client
            data = c.recv(1024)
            if not data:
                continue
            self.scores[index] += 1
            num_key = self.player_statistics[index].get(data, 0) + 1
            self.player_statistics[index][data] = num_key
            self.player_key_press[index] += 1

        # send back string to client
        winner = 0 if (self.scores[0] > self.scores[1]) else 1
        winner_team = team1 if (self.scores[0] > self.scores[1]) else team2
        sorted_keys = sorted(
            self.player_statistics[index].items(), key=lambda x: x[1], reverse=True)
        most_common_key = sorted_keys[0][0].decode('utf-8')
        most_common_key_pressed = sorted_keys[0][1]
        least_common_key = sorted_keys[-1][0].decode('utf-8')
        least_common_key_pressed = sorted_keys[-1][1]
        max_press = max(self.player_key_press)
        fastest_typer_index = self.player_key_press.index(max_press)
        name = self.teams[fastest_typer_index].split('\n')[0]
        message = f"\nGame over!\nGroup 1 typed in {self.scores[0]} characters. Group 2 typed in {self.scores[1]} characters.\nGroup {winner+1} wins!\n\nGlobal Results:\nThe fastest team was {name} with {max_press} characters!\n\nPersonal Results:\nYou pressed {self.player_key_press[index]} characters\nYour most common character was '{most_common_key}' with {most_common_key_pressed} presses!\nYour least common character was '{least_common_key}' with {least_common_key_pressed} presses.\n\nCongratulations to the winners:\n==\n{winner_team}"
        c.send(bytes(message, encoding='utf8'))
        self.start_game = False
        # connection closed
        c.close()
        self.lock.acquire()
        self.num_particants -= 1
        self.lock.release()
        self.player_key_press = [0, 0, 0, 0]
        self.player_statistics = [{}, {}, {}, {}]

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]

        print(''.join(colored_chars))

    def TCPServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ip, self.port))
        text = f"Server started, listening on IP address {self.ip}"
        self.pretty_print(text)
        self.startBroadcasting()
        s.listen()
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
        while True:
            if not self.start_game:
                start_time = time.time()
                server = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                # Enable port reusage
                server.setsockopt(socket.SOL_SOCKET,
                                  socket.SO_REUSEPORT, 1)
                # Enable broadcasting mode
                server.setsockopt(socket.SOL_SOCKET,
                                  socket.SO_BROADCAST, 1)

                # Set a timeout so the socket does not block
                # indefinitely when trying to receive data.
                server.settimeout(0.2)
                magic_cookie = "feedbeef"
                message_type = "02"
                x = bytes.fromhex(magic_cookie)
                y = bytes.fromhex(message_type)
                z = self.port.to_bytes(2, byteorder='big')
                message = x + y + z

                while time.time() - start_time < 10:
                    server.sendto(
                        message, ('<broadcast>', self.broadcastPort))
                    time.sleep(1)
                self.start_game = True
