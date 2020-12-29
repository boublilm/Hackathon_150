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
        self.startTCPServer()
        self.teams = []
        self.scores = [0, 0]
        self.lock = threading.Lock()
        self.player_statistics = []
        self.player_key_press = []
        self.start_game = False
        self.game_finished = False

    def startTCPServer(self):
        # Starts TCP Server via a thread.
        thread = threading.Thread(target=self.TCPServer)
        thread.start()

    def clientHandler(self, c):
        TeamName = str(c.recv(1024), 'utf-8')
        self.teams += [TeamName]

        while not self.start_game:
            time.sleep(0.1)

        # setting team names in a variable
        team1 = ''.join(self.teams[:int(len(self.teams)/2)])
        team2 = ''.join(self.teams[int(len(self.teams)/2):])
        # S Sending start message
        c.send(bytes(
            f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n{team1}Group 2:\n{team2}\nStart pressing keys on your keyboard as fast as you can!!",
            encoding='utf8'))

        index = self.teams.index(TeamName) // 2
        team_index = 0 if TeamName in team1 else 1
        # While not past 10 seconds - listen to key presses.
        start_time = time.time()
        while time.time() - start_time < 10:
            # data received from client
            data = c.recv(1024)
            if not data:
                continue
            self.scores[team_index] += 1
            num_key = self.player_statistics[index].get(data, 0) + 1
            self.player_statistics[index][data] = num_key
            self.player_key_press[index] += 1

        # Statistics
        winner = 0 if (self.scores[0] > self.scores[1]) else 1 if self.scores[0] < self.scores[1] else -1
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

        # Game Over Message
        game_finished = f"\nGame over!\n" \
                      f"Group 1 typed in {self.scores[0]} characters. " \
                      f"Group 2 typed in {self.scores[1]} characters.\n"
        if winner < 0:
            results = f"This is a TIE!\n"
        else:
            results = f"Group {winner+1} wins!\n\n" \
                      f"Congratulations to the winners:\n{winner_team}\n"

        global_stat = f"Global Results:\n" \
                      f"\tThe fastest team was {name} with {max_press} characters!\n\n"

        personal = f"Personal Results:\n" \
                   f"\tYou pressed {self.player_key_press[index]} characters\n" \
                   f"\tYour most common character was '{most_common_key}' with {most_common_key_pressed} presses!\n" \
                   f"\tYour least common character was '{least_common_key}' with {least_common_key_pressed} presses.\n\n"

        message = game_finished + results + global_stat + personal

        c.send(bytes(message, encoding='utf8'))
        self.start_game = False
        # connection closed
        c.close()
        self.game_finished = True
        self.default_server()

    def default_server(self):
        self.lock.acquire()
        self.player_key_press = []
        self.player_statistics = []
        self.lock.release()

    def pretty_print(self, data):
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        colored_chars = [random.choice(colors) + char for char in data]

        print(''.join(colored_chars))

    def TCPServer(self):
        while True:
            self.game_finished = False
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.ip, self.port))
            text = f"Server started, listening on IP address {self.ip}"
            self.pretty_print(text)
            self.startBroadcasting()
            s.listen()
            while not self.game_finished:

                # establish connection with client
                c, addr = s.accept()

                self.lock.acquire()
                self.player_key_press.append(0)
                self.player_statistics.append({})
                random.shuffle(self.teams)
                self.lock.release()

                # Start a new thread and return its identifier
                start_new_thread(self.clientHandler, (c,))
            s.close()
            self.pretty_print("Game over, sending out offer requests...")

    def startBroadcasting(self):
        # Starts Broadcasting via a thread.
        thread = threading.Thread(target=self.broadcast)
        thread.start()

    def stopBroadcasting(self):
        # Sets the broadcast loop's statement to false, thus -> will stop broadcasting.
        self.toBroadcast = False

    def broadcast(self):
        start_time = time.time()
        server = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable port reusage
        server.setsockopt(socket.SOL_SOCKET,
                          socket.SO_REUSEADDR, 1)
        # Enable broadcasting mode
        server.setsockopt(socket.SOL_SOCKET,
                          socket.SO_BROADCAST, 1)

        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        server.settimeout(0.2)

        while time.time() - start_time < 10:
            server.sendto(struct.pack('Ibh', 0xfeedbeef, 0x2, self.port), ('<broadcast>', self.broadcastPort))
            time.sleep(1)
        self.start_game = True
