import socket
import sys
import threading
import socketserver
import mysql.connector

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def send(self, data : str) -> None:
        data = bytes(data , "utf-8")
        #sending the size of the data
        lenofdata = str(len(data))
        # converting the lenght into exact 20 bytes
        lenofdata = (20 - len(lenofdata)) * "0" + lenofdata
        lenofdata = bytes(lenofdata , "utf-8")
        self.request.sendall(lenofdata)
        self.request.sendall(data)

    def recieve(self) -> str:
        lenofdata = int(str(self.request.recv(20), "utf-8"))
        print(lenofdata)
        return str(self.request.recv(lenofdata), "utf-8")

    def handle(self):
        conndb = mysql.connector.connect(
            host = "localhost",
            user = "lunchspider",
            password = "archi",
            database = "nobank"
            )
        cursor = conndb.cursor()
        conn = self.recieve().split("\n")
        print(conn)
        username,passwd,task = conn
        # task 0 for creating new account
        # task 1 for sending money
        # task 2 to check available balance
        # task 3 to see last transaction
        # task 4 to add money to the account
        if (task == "0"):
            #creating account
            sql_query = """SELECT *  FROM accounts WHERE username=%s"""
            cursor.execute(sql_query,(username,))
            return_query = cursor.fetchall()
            #checking if username and password are correct
            if len(return_query) == 1 :
                #if username is present in the server
                self.send("username found")
                return None
            self.send("ok")
            userinfo = self.recieve().split("\n")
            sql_query = """INSERT INTO accounts(username, 
            password, first_name,
            last_name, phone_number, address)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            print(userinfo)
            cursor.execute(sql_query, tuple(userinfo))
            conndb.commit()
            return None

        sql_query = """SELECT *  FROM accounts
        WHERE username=%s AND password=%s"""
        cursor.execute(sql_query,(username,passwd))
        return_query = cursor.fetchall()
        #checking if username and password are correct
        # since if username or password are incorrect the result will be a 
        # empty list
        if not return_query:
            self.send("error 404")
            return None
        
        available_balance = return_query[0][2]
        self.send("ok")

        if (task == "1"):
            obj = self.recieve().split("\n")
            sendtouser,amt = obj
            sql_query = """SELECT * FROM accounts WHERE username=%s"""
            cursor.execute(sql_query,(sendtouser,))
            result_query = cursor.fetchall()
            # TODO :> implement a transaction history table here that updates every
            # transaction into a table in the mariadb server 
            if len(result_query) == 0:
                self.send("incorrect username")
                return None
            amt = int(amt)
            if(available_balance < amt):
                self.send("insufficient funds")
                return None

            sql_query = """UPDATE accounts SET balance = balance + %s
            WHERE username = %s"""
            cursor.execute(sql_query,(amt , sendtouser))
            sql_query = """UPDATE accounts SET balance = balance - %s
            WHERE username = %s"""
            cursor.execute(sql_query, ( amt , username))
            conndb.commit()
            sql_query = """"""
            self.send("successful")
            return None

        if(task == "2"):
            # checking the balance of a account
            self.send(str(available_balance))
            return None

        if(task == "4"):
            amount = self.recieve()
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
