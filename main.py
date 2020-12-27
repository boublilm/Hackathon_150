import socket
from Server import Server
from Client import Client

my_server = Server('127.0.0.1', 1337, 13117)
my_client = Client('127.0.0.1', 13117)
my_server.startBroadcasting()
my_client.listenToBroadcast()
