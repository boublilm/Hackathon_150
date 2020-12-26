import threading
import socket


def client():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 13117))
    message, address = s.recvfrom(1024)
    print(message)
    megic_cookie = message[:4]
    message_type = message[4]
    port_tcp = message[5:]
    print(int.from_bytes(port_tcp, byteorder='big', signed=False))


def server():
    import socket
    import time

    current_working_ip = '127.0.0.1'
    PORT = 1337
    dest_port = 13117

    print(f"Server started,listening on IP address {current_working_ip}")
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
    z = PORT.to_bytes(2, byteorder='big')
    message = x + y + z

    while True:
        server.sendto(message, ('<broadcast>', dest_port))
        time.sleep(1)


t1 = threading.Thread(target=server,)
t2 = threading.Thread(target=client,)
# starting thread 1
t1.start()
# starting thread 2
t2.start()
# wait until thread 1 is completely executed
t1.join()
# wait until thread 2 is completely executed
t2.join()
