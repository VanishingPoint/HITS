import socket               

s = socket.socket()        
host = ''# ip of raspberry pi
#TODO: Match the ip in the server script once changed
port = 12345               
s.connect((host, port))
print(s.recv(1024))
s.close()