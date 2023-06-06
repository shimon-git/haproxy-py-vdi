import select
import socket
import os
import subprocess
from servers import servers
from logger import Logger


class CustomSocket():
    def __init__(self):
        self.server_manager = servers()
        self.logger = Logger()
        self.log = self.logger.setup_logger()
    def socket_server(self,host, port):
        address_in_use = True
        while address_in_use:
            try:
                pid = subprocess.check_output(["lsof", "-t", "-i", f":{port}"], universal_newlines=True).strip()
                if pid:
                    os.kill(int(pid), 9)
            except subprocess.CalledProcessError:
                pass
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((host, port))
                address_in_use = False
                server_socket.listen(10)
                client_sockets = [server_socket] 
                self.log
            except OSError:
                pass   
        while True:
            readable, _, _ = select.select(client_sockets, [], [])
            for sock in readable:
                if sock is server_socket:
                    client_socket, client_address = server_socket.accept()
                    client_sockets.append(client_socket)
                    self.log.info(f"python socket: New connection from {client_address[0]}:{client_address[1]}")
                else:
                    try:
                        data = sock.recv(1024).decode()
                        self.server_manager.start_server(data)
                        if data:
                            self.log.info(f"python socket: Received data: {data.strip()} from {sock.getpeername()[0]}:{sock.getpeername()[1]}")
                            response = 'sucsses'
                            sock.send(response.encode())
                        else:
                            self.log.info(f"python socket: Connection closed by {sock.getpeername()[0]}:{sock.getpeername()[1]}")
                            client_sockets.remove(sock)
                            sock.close()
                    except OSError as e:
                        client_sockets.remove(sock)
                        sock.close()
                        break


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8888
    CustomSocket().socket_server(host, port)
