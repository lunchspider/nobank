import socket
import sys

HOST, PORT = "localhost", 54929

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
        if task == 2:
            balance = str(sock.recv(1024),"utf-8")
            if(balance == "error 404"):
                raise NameError("Given username and/or password is wrong.")
            print("Available balance is : ",balance)

        if task == 4:
            pass




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

