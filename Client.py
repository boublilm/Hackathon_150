import socket
s = socket(AF_INET, SOCK_DGRAM)
s.bind(('127.0.0.1', 13117))
m = s.recvfrom(1024)
print m[0]
