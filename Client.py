import scapy.all as scapy
from scapy.layers.inet import IP, UDP
scapy.srloop(IP(dst="127.0.0.1")/UDP(dport=80))
