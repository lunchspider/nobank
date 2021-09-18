import socket
import os
import sys
import getpass
from datetime import datetime

HOST, PORT = "localhost", 0

if(len(sys.argv) == 1) :
    # that is if no arguments are given
    raise TypeError("No arguments were given. Try adding --help in the end.")

if(sys.argv[1] == "--help" ):
    help_string = """Client.py is the client program for nobank.
if you have a account:
    python client.py -h <host>:<PORT> -u <username>
or:
    python client.py -h <host>:<PORT> --createaccount"""
    print(help_string)
    sys.exit()
HOST     = sys.argv[2]
#spliting the host and the port
HOST     = HOST.split(":")
PORT     = int(HOST[1])
HOST     = HOST[0]

def send(sock : socket.socket, data : str) -> None:
    data = bytes(data , "utf-8")
    #sending the size of the data
    lenofdata = str(len(data))
    # converting the lenofdata into exact 20 bytes
    lenofdata = (20 - len(lenofdata)) * "0" + lenofdata
    lenofdata = bytes(lenofdata , "utf-8")
    sock.sendall(lenofdata)
    sock.sendall(data)

def recieve(sock : socket.socket) -> str:
    # 20 bytes is enough to represent the lenght of the data
    lenofdata = int(str(sock.recv(20), "utf-8"))
    return str(sock.recv(lenofdata), "utf-8")

if(sys.argv[3] == "--createaccount"):
    first_name = input("Enter the first name of the account holder: ")
    last_name  = input("Enter the last name of the account holder: ")
    username   = input("Enter username(it should be unique): ")
    passwd     = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        while(True):
            #iterating till user give a unique username
            string = username + "\n" + passwd + "\n" + str(0)
            send(sock, string)
            if(recieve(sock) == "username found"):
                print("Username found try something else.")
                username = input("Enter username(it should be unique):")
            else:
                break
        phonenum = input("Enter you phone number:")
        address  = input("Enter you address:")
        passwd   = getpass.getpass()
        userinfo = username + "\n" + passwd + "\n" + first_name + "\n"
        userinfo += last_name + "\n" + phonenum + "\n" + address
        send(sock, userinfo)
        sys.exit()

username = ''
passwd = getpass.getpass()
try:
    username = sys.argv[4]
except Exception as e:
    raise SyntaxError("""The call to client.py should be:
    python client.py -h <host>:<PORT> -u <username> -p
    see python client.py --help for more information.
    """)

def main(task:int):
    
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        string = username + "\n" + passwd + "\n" + str(task)
        #sending all the queries in a string of size 1024 bytes lenght
        send(sock, string)

        everything_ok = recieve(sock)
        if(everything_ok == "error 404"):
            raise NameError("Given username and/or password is wrong.")

        if task == 2:
            #checking balance
            balance = recieve(sock)
            print("Available balance is : ",balance)
            return None
        
        if task == 1:
            #sending money to other person
            sendto = input("Username of the person you want to send money to:")
            amount = int(input("The amount you want to send:"))
            if(amount < 0):
                raise TypeError(f"Cannot send {amount}! Wrong value. ")
            send(sock , sendto + "\n" + str(amount))
            print(recieve(sock))


        if task == 4:
            #adding money to the bank
            inc_balance = int(input("Enter the amount you want to add:"))
            if(inc_balance < 1):
                raise TypeError("Error : Wrong Value: ",inc_balance)
            send(sock, str(inc_balance))
            return None



if __name__ == "__main__":
    while(True): 
        print("Username :",username)
        print("1. Send Money \n2. See Balance\n3. Last Transction")
        print("4. Add Money\n5. Quit")
        response = int(input("Choose a number : "))
        if(response == 5):
            break
        os.system("clear")
        main(response)
   
