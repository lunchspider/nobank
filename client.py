import socket
import sys

HOST, PORT = "localhost", 0

username = ''
passwd = ''
try:
    HOST     = sys.argv[2]
    HOST     = HOST.split(":")
    PORT     = int(HOST[1])
    HOST     = HOST[0]
    username = sys.argv[4]
    passwd   = sys.argv[6]
except Exception as e:
    raise SyntaxError("""The call to client.py should be:
    python client.py -h <host>:<PORT> -u <username> -p <password>
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
            amount = int(input("The amount you want to send"))
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

