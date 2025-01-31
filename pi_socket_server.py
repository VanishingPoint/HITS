import socket

s = socket.socket()
host = '100.120.18.53' #ip of raspberry pi, set to my talescale ip for now
#TODO: change this to the actual ip of the pi, which will have to be set as
# a static ip address on a wifi network the pi will create
port = 8085
s.bind((host, port))

s.listen(5)
while True:
  c, addr = s.accept()
  print ('Got connection from',addr)
  c.send('Thank you for connecting')
  c.close()