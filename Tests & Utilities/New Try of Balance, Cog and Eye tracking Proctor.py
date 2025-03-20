from PIL import Image
import socket
import time
from pynput import keyboard

#Socket connection information
HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

#Setting up the array of image numbers for cognitive test
#TODO: Once cognitive test works, make this explicitly for cog images only, generalize image open function
image_numbers = list(range(0, 17)) #image 0 is explination, others are answers corresponding to the participant images

image_paths = [
     fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Triss
    # fr"C:\Users\richy\Downloads\cognitive\images\cognitive_page_{num}.png" # Richard
    # fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Chanel
    for num in image_numbers
]

opened_image = None

def initialize_socket(): #Function to set up initial socket connection
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            return s
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return initialize_socket
    

def send_message(message):
    with s:
        s.sendall(message.encode('utf-8'))

def get_data():
    with s:
        data = s.recv(1024)
        return data.decode('utf-8')


def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()
    opened_image = Image.open(image_path)
    opened_image.show()

def on_press(key):
    global cog_started, cog_completed
    try:
        if key.char == 's' and not cog_started:
            cog_started = True
            print("Test started.")
            # Show the first image
            send_message(key.char)
            response = get_data
            print(f"Received image number: {response}")
            show_image(image_paths[int(response)])
        elif (key.char == 'y' or key.char == 'n') and cog_started:
            # Send the 'y' or 'n' response to the server
            print("sent key:", key)
            send_message(key.char)
            response = get_data
            if (response == 'end'):
                print("Test Complete")
                cog_completed = True
            else:
                print(f"Received image number: {response}")
                show_image(image_paths[int(response)])  # Show the next randomized image
        elif key.char == 'e':
            print("Exiting program...")
            send_message("Exit")
            response = get_data
            print(response)
            # Allows the user to exit the test if 'e' is pressed
            #TODO: make this return in a way that indicates the test did not complete
        else:
            print("Invalid Input")
                
    except AttributeError:
        pass

# Run cognitive test once user info is submitted
def run_cognitive_test():
    global cog_started, image_numbers, cog_completed
    print("Press 's' to start the randomized image sequence.")
    print("Press 'y' or 'n' to open the next image after starting.")
    print("Press 'e' to exit the program.")

    # Show the explanation image first (cognitive_page_0)
    show_image(image_paths[0])

    while not cog_completed:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()


def collect_user_info():
    data_ready = False
    while not data_ready:
        print("Please enter user data. Note that validity of data is not checked. Please verify all data before confirming.")
        sequence = input("Please enter a sequence number for the participant:")
        age = input("Pleae enter the participant's age in years:")
        sex = input("Please enter the participant's sex (m or f):")
        height = input("Please enter the participant's height in cm:") #I will assume this is always 3 digits, stuff will probably break if it isn't
        #line below is for data collection, to be changed in final version
        drunk = input("Please indicate if the participant is drunk or sober (d or s):")
        print("You entered the following data: \n Sequence:", sequence, "\n Age:", age, " years, \n Sex:", sex, "\n Height:", height, " cm \n Drunk/Sober:", drunk,)
        if input("\n Is this correct? Enter y if yes, or any other key if no.") == 'y':
            data_ready = True
    
    #TODO: In the final version we need more checks to ensure input is valid
    send_message(sequence)
    send_message(age)
    send_message(sex)
    send_message(height)
    send_message(drunk)
        
cog_started = False
cog_completed = False
    
s = initialize_socket()

collect_user_info()

run_cognitive_test()

print("Testing Complete")


