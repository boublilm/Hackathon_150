import socket
import time

current_working_ip = '127.0.0.1'
PORT = 24
dest_port = 13117

print(f"Server started,listening on IP address {current_working_ip}")
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
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
