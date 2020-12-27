import socket
import threading


class Client():
    def __init__(self, IP, PORT):
        self.ip = IP
        self.port = PORT

    def listenToBroadcast(self):
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.port))
        message, address = s.recvfrom(1024)
        print(message)
        megic_cookie = message[:4]
        message_type = message[4]
        port_tcp = message[5:]
        print(int.from_bytes(port_tcp, byteorder='big', signed=False))
