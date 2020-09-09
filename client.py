import socket
import sys
import getpass

HOST, PORT = "localhost", 0
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
            sock.sendall(bytes(string, "utf-8"))
            if(str(sock.recv(100),"utf-8")== "username found"):
                print("Username found try something else.")
                username = input("Enter username(it should be unique):")
            else:
                break
        phonenum = input("Enter you phone number:")
        address  = input("Enter you address:")
        passwd   = getpass.getpass()
        userinfo = username + "\n" + passwd + "\n" + first_name + "\n"
        userinfo += last_name + "\n" + phonenum + "\n" + address
        sock.sendall(bytes(userinfo ,"utf-8"))

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
        sock.sendall(bytes(string, "utf-8"))

        everything_ok = str(sock.recv(1024), "utf-8")
        if(everything_ok == "error 404"):
            raise NameError("Given username and/or password is wrong.")

        if task == 2:
            #checking balance
            balance = str(sock.recv(1024),"utf-8")
            print("Available balance is : ",balance)
            return None
        
        if task == 1:
            #sending money to other person
            sendto = input("Username of the person you want to send money to:")
            amount = int(input("The amount you want to send:"))
            if(amount < 0):
                raise TypeError(f"Cannot send {amount}! Wrong value. ")
            sock.sendall(bytes(sendto + "\n" + str(amount) , "utf-8"))
            print(str(sock.recv(1024),"utf-8"))


        if task == 4:
            #adding money to the bank
            inc_balance = int(input("Enter the amount you want to add:"))
            if(inc_balance < 1):
                raise TypeError("Error : Wrong Value: ",inc_balance)
            sock.sendall(bytes(str(inc_balance),"utf-8"))
            return None



if __name__ == "__main__":
    print("Logging in...")
    print("Username :",username)
    while(True):
        print("1. Send Money \n2. See Balance\n3. Last Transction")
        print("4. Add Money\n5. Quit")
        response = int(input("Choose a number : "))
        if(response == 5):
            break
        main(response)

