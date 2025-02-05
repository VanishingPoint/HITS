import socket
import time
import sys
import select

def wait_for_keypress():
    print("Press 's' to start the task.")
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == 's':
                return

def send_start_signal(sock):
    sock.sendall(b'start')

def start_timer():
    for remaining in range(120, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("Time remaining: {:2d} seconds.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rTime is up! Waiting for response from the Pi...\n")

def wait_for_response(sock):
    response = sock.recv(1024)
    print(f"Received response from Pi: {response.decode()}")

def main():
    # Set up the socket connection to the Pi
    pi_address = ('100.120.18.53', 65433)  #TODO: Replace IP address when we switch to local wifi
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(pi_address)

    try:
        wait_for_keypress()
        send_start_signal(sock)
        start_timer()
        wait_for_response(sock)
    finally:
        sock.close()

if __name__ == "__main__":
    main()