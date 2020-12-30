from Server import Server
from Client import Client
from scapy.arch import get_if_addr
# TODO: IP by eth1, eth2
my_server = Server(get_if_addr('eth1'), 2025, 13117)
my_client = Client(get_if_addr('eth1'), 13117)
