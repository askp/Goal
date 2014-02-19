import socket
import threading
import SocketServer
import time

from ball import BallFinder
from goal import GoalFinder

gf = GoalFinder()
bf = BallFinder()

ball_finding = threading.Event()
goal_finding = threading.Event()

def find_goal():
	while True:
		goal_finding.wait()
		gf.find()

def find_ball():
	while True:
		ball_finding.wait()
		bf.find()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(8) # We only expect 1 byte, but be careful anyway
        # Determine what thread to use in order to get the data requested
        if data[0].lower() == 'g':
            # We want the goal tracking thread
            ball_finding.clear()
            goal_finding.set()
            response = response = '{} {} {}'.format(gf.gRange,gf.angle,gf.Hot)
            print response

        elif data[0].lower() == 'r' or data[0].lower() == 'b':
			bf.setColour(data[0].lower())
			#Catching thread
			goal_finding.clear()
			ball_finding.set()
			response = response = '{} {} {}'.format(bf.xbar,bf.ybar,bf.diam)
        else:
            response = '-999' # Invalid request

        self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "", 4774 # Bind to all address on port 4774

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever, name="tcpserver")
    # Exit the server thread when the main thread terminates
    # Makes breaking out of program with Ctrl-C easier
    server_thread.daemon = True
    server_thread.start()

    goal_thread = threading.Thread(target=find_goal, name = 'finding goal')
    goal_thread.daemon = True
    goal_finding.clear()
    goal_thread.start()

    ball_thread = threading.Thread(target=find_ball, name = 'finding ball')
    ball_thread.daemon = True
    ball_finding.clear()
    ball_thread.start()

    while True:
		pass

        # Infinite loop to keep the main thread running
        # and waiting for connections
        # Makes breaking out of program with Ctrl-C easier
        #pass