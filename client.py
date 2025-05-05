import socket

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ipadd = input("IP Address of server (i.e. 127.0.0.1): ")
srvport = int(input("Server Port (1-65535): "))
try:
    myTCPSocket.connect((ipadd, srvport)) ## uses user input of server's ip_address
                                        ## and chosen port number
    print("Connected to server.")
except socket.error as e:
    print("Connection failed: ", e) ## error if not able to connect
    exit()
msg = ""
while True: ## will keep going to write messages back and forth until msg == 0
    msg = input("""Message Database (0 to quit, 1-3 to ask database queries):
1.) What is the average moisture inside my kitchen fridge in the past three hours?
2.) What is the average water consumption per cycle in my smart dishwasher?
3.) Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?\n""")
    print("Client message to database:")
    if msg == "1":
        print("What is the average moisture inside my kitchen fridge in the past three hours?")
    elif msg == "2":
        print("What is the average water consumption per cycle in my smart dishwasher?")
    elif msg == "3":
        print("Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
    elif msg == "0":
        print("Client closes.")
        break
    else:
        print("Sorry, this query cannot be processed. Please try one of the following: [1, 2, 3].")
        continue
    myTCPSocket.send(bytearray(str(msg), encoding='utf-8')) ## sends mgs to server in utf-8
    serverResponse = myTCPSocket.recv(1024)
    if serverResponse:
        print(f"Server: {serverResponse.decode('utf-8')}\n") ## decodes and prints server response
    else:
        print("Server closed.")
        break
myTCPSocket.close()
