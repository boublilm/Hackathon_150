import socket
import time
import threading


class Server():
    def __init__(self, IP, PORT, broadcastPort):
        self.ip = IP
        self.port = PORT
        self.toBroadcast = True
        self.broadcastPort = broadcastPort

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
