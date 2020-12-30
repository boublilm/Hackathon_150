import socket
from select import select
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('', 4000))
incoming_data = select([s], [], [], 11)
if incoming_data:
    data = str(s.recv(1024), 'utf-8')
    self.pretty_print(data)
else:  # server disconnected before game started, we waited for him 11 seconds to start the stuupid game
    s.close()
    print("11 seconds over")
