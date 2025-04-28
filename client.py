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
while msg != "0": ## will keep going to write messages back and forth until msg == 0
    if msg == "0":
        break
    msg = input("Message (0 to quit): ")
    myTCPSocket.send(bytearray(str(msg), encoding='utf-8')) ## sends mgs to server in utf-8
    serverResponse = myTCPSocket.recv(1024)
    if serverResponse:
        print(f"Server: {serverResponse.decode('utf-8')}") ## decodes and prints server response
    else:
        print("Server closed.")
        break
myTCPSocket.close()
