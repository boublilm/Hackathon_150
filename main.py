import socket
from Server import Server
from Client import Client
import time

my_server = Server('localhost', 1337, 13117)
my_client = Client('localhost', 13117)
my_client.listenToBroadcast()
