import scapy.all as scapy
from scapy.layers.inet import IP, UDP
IPa = 123  # TODO: instert IP.
print(f"Server started,listening on IP address {IPa}")
scapy.srloop(IP(dst="127.0.0.1")/UDP(dport=80))
