import socketserver
from shared_state import SharedState

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        #print("{} wrote:".format(self.client_address[0]))
        #print(data)
        SharedState.shared_data = SharedState.interpreter(data) 
        #print(SharedState.shared_data)

class UDPReceiver:
    def __init__(self, config): 
        self.udp_server_ip = config['udp']['server_ip']
        self.udp_server_port = int(config['udp']['server_port'])

    def run(self):
        print("Running UDP receiver...")
            
        HOST, PORT = self.udp_server_ip, self.udp_server_port
        with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
            server.serve_forever() # _handle_request_noblock()



