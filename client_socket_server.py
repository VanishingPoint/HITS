import socket               

s = socket.socket()        
host = '100.120.18.53'# ip of raspberry pi
#TODO: Match the ip in the server script once changed
port = 8085               
s.connect((host, port))
print(s.recv(1024))
s.close()