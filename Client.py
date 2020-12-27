import socket
import threading


class Client():
    def __init__(self, IP, PORT):
        self.ip = IP
        self.port = PORT

    def listenToBroadcast(self):
        # Creates a thread to start listening for broadcasts.
        thread = threading.Thread(target=self.listen)
        thread.start()

    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Binds client to listen on port self.port. (will be 13117)
        s.bind(('', self.port))

        # Receives Message
        message, address = s.recvfrom(1024)
        print(message)

        # Message Teardown.
        magic_cookie = message[:4]
        message_type = message[4]
        port_tcp = message[5:]
        print(int.from_bytes(port_tcp, byteorder='big', signed=False))
