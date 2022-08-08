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
        shared = SharedState.interpreter(data)

        try:
            SharedState.statistics.save_message(data)
        except Exception e:
            print("Stat logging failed:", e)

        shared = SharedState.modifier(shared)
        SharedState.shared_data = shared

        #print(SharedState.shared_data)
        #SharedState.logging.info(data)   

class UDPReceiver:
    def __init__(self, config): 
        self.udp_server_ip = config['udp']['server_ip']
        self.udp_server_port = int(config['udp']['server_port'])

    def run(self):
        print("Running UDP receiver...")
            
        HOST, PORT = self.udp_server_ip, self.udp_server_port
        with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
            server.serve_forever() # _handle_request_noblock()



