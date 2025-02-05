import socket
import serial

HOST = '100.120.18.53' #TODO: Change this when we go to local wifi
PORT = 65433      # Port to listen on

def main():
    # Set up the serial connection to the Arduino
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust as necessary
    ser.reset_input_buffer()

    # Set up the socket server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data.decode('utf-8') == 'start':
                    # Send start signal to Arduino
                    ser.write(b'start\n')
                    print("Sent 'start' to Arduino")

                    # Wait for response from Arduino
                    while True:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').rstrip()
                            print(f"Received from Arduino: {line}")
                            try:
                                # Try to convert the line to a float
                                value = float(line)
                                # Send the value to the client
                                conn.sendall(str(value).encode('utf-8'))
                                break
                            except ValueError:
                                # If conversion fails, continue waiting for a valid float
                                continue

if __name__ == '__main__':
    main()