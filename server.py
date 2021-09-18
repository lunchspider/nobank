#!/usr/bin/python3
# author Aman Sharm
import socket
import sys
import threading
import socketserver
import sys
import mysql.connector

class ClientHandler(socketserver.BaseRequestHandler):
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
            # TODO :> implement a transaction history table 
            #here that updates every
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
            sql_query = """INSERT INTO transaction(trans_id, from_user
            ,to_user, amount, trans_time, trans_date)
            VALUES(%s, %s, %s, %s, %s, %s)"""
            import uuid, datetime
            trans_id = str(uuid.uuid4())[:32]
            trans_time = datetime.datetime.utcnow()
            cursor.execute(sql_query, (trans_id, username, sendtouser, 
                amt, trans_time.time(), trans_time.date()))
            conndb.commit()
            self.send(f"successful, id : {trans_id}")
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
    if sys.argv[1] == "--setup":
        # running setup script
        conndb = mysql.connector.connect(
                host = "localhost",
                user = "lunchspider",
                password = "archi",
                )
        cursor = conndb.cursor()
        sql_query = """
        CREATE DATABASE IF NOT EXISTS nobank;
        USE nobank;
        CREATE TABLE IF NOT EXISTS  accounts(
            username char(45) NOT NULL PRIMARY KEY,
            password varchar(50) NOT NULL,
            balance bigint(20) UNSIGNED,
            first_name varchar(26),
            last_name varchar(15),
            phone_number char(15),
            address varchar(100)
        );
        """
        cursor.execute(sql_query)
        conndb.commit()

    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    with server:
        ip, port = server.server_address
        print(ip,port)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("run --startup first to run the script")
        print("Server loop running in thread:", server_thread.name)
        server.serve_forever()
