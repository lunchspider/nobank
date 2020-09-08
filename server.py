import socket
import sys
import threading
import socketserver
import mysql.connector

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        conndb = mysql.connector.connect(
            host = "localhost",
            user = "lunchspider",
            password = "passwd",
            database = "nobank"
            )
        cursor = conndb.cursor()


        query = str(self.request.recv(1024), "utf-8").split("\n")
        username,passwd,task = query
        sql_query = """SELECT *  FROM accounts
        WHERE username=%s AND password=%s"""
        cursor.execute(sql_query,(username,passwd))
        return_query = cursor.fetchall()
        #checking if username and password are correct
        if len(return_query) == 0 :
            self.request.sendall(bytes("error 404","utf-8"))
            return None
        
        available_balance = return_query[0][2]
        self.request.sendall(bytes("ok","utf-8"))

        if (task == "1"):
            obj = str(self.request.recv(1024),"utf-8").split("\n")
            sendtouser,amt = obj
            sql_query = """SELECT * FROM accounts WHERE username=%s"""
            cursor.execute(sql_query,(sendtouser,))
            result_query = cursor.fetchall()
            if len(result_query) == 0:
                self.request.sendall(bytes("incorrect username" , "utf-8"))
                return None
            amt = int(amt)
            if(available_balance < amt):
                self.request.sendall(bytes("insufficient funds","utf-8"))
                return None

            sql_query = """UPDATE accounts SET balance = balance + %s
            WHERE username = %s"""
            cursor.execute(sql_query,(amt , sendtouser))
            sql_query = """UPDATE accounts SET balance = balance - %s
            WHERE username = %s"""
            cursor.execute(sql_query, ( amt , username))
            conndb.commit()
            self.request.sendall(bytes("succesful", "utf-8"))
            return None

        if(task == "2"):
            # checking the balance of a account
            self.request.sendall(bytes(str(available_balance), "utf-8"))
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
