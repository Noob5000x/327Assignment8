import socket
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = input("Enter Host IP Address (for example 127.0.0.1): ")
host_port = int(input("Enter Port Number (1-65535): "))
myTCPSocket.bind((host_ip, host_port)) 
## binds to host's own private ip address and
## chosen port number
myTCPSocket.listen(5)                  
print("Server is listening.")
while True:
  incomingSocket, incomingAddress = myTCPSocket.accept() ## accepts connection
  print("Connected to partner.")
  while True:
    myData = incomingSocket.recv(1024) ## takes msg from client
    if myData:
      response = myData.decode().upper() ## capitalizes msg
      myData = myData.decode()
      print(f"Client's message: {myData}")
      print(f"Server response: {response}")
      myTCPSocket.send(response) ## sends capitalized msg back
    else:
      break
  incomingSocket.close()
