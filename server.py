import socket
import sys
import threading
import socketserver
import mysql.connector

conndb = mysql.connector.connect(
   host = "localhost",
   user = "lunchspider",
   password = "archi",
   database = "nobank"
)
cursor = conndb.cursor()



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        query = str(self.request.recv(1024), "utf-8").split("\n")
        username,passwd,task = query
        if(task == "2"):
            # checking the balance of a account
            sql_query = """SELECT balance FROM accounts 
            WHERE username=%s and password=%s"""
            cursor.execute(sql_query,(username,passwd))
            balance = cursor.fetchall()
            if len(balance) == 0 :
                self.request.sendall(bytes("error 404","utf-8"))
            else :
                self.request.sendall(bytes(str(balance[0][0]), "utf-8"))
            return None 
        if(task == "4"):
            amount = str(self.request.recv(1024),"utf-8")
            sql_query = """UPDATE accounts
            SET balance = balance + %s
            WHERE username = %s and password = %s
            """
            cursor.execute(sql_query,( amount, username, passwd))
            conndb.commit()
            return None

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address
        print(ip,port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        server.serve_forever()
