from PIL import Image
import socket
import time
from pynput.keyboard import Listener

# Socket connection information
HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# Setting up the array of image numbers for the cognitive test
#TODO: Once cognitive test works, make this explicitly for cog images only, generalize image open function
image_numbers = list(range(0, 17)) # image 0 is explanation, others are answers corresponding to the participant images

image_paths = [
    # fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Triss
    # fr"C:\Users\richy\Downloads\cognitive\images\cognitive_page_{num}.png" # Richard
     fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Chanel
    for num in image_numbers
]

opened_image = None
    
def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()
    opened_image = Image.open(image_path)
    opened_image.show()

def cognitive_test(response):
    global cog_started, cog_completed, waiting_for_keyboard

    if cog_started == True:
        if (response == 'end'):
                print("Cognitive Test Complete")
                cog_completed = True
                return 0 #TODO: Do something here
        else:
            print(f"Received image number: {response}")
            show_image(image_paths[int(response)])  # Show the next randomized image

            waiting_for_keyboard = True
            listener = Listener(on_press=lambda event: on_press(event))
            listener.start()

            while waiting_for_keyboard:
                time.sleep(1)
            listener.stop()

    elif cog_started == False:
        print("Press 's' to start the randomized image sequence.")
        print("Press 'y' or 'n' to open the next image after starting.")
        print("Press 'e' to exit the program.")

        # Show the explanation image first (cognitive_page_0)
        show_image(image_paths[0])
        
        waiting_for_keyboard = True
        listener = Listener(on_press=lambda event: on_press(event))
        listener.start()

        while waiting_for_keyboard:
                time.sleep(1)
        listener.stop()
        
    print("Returning Passthrough")
    return passthrough

def on_press(key):
    global passthrough, cog_started, cog_completed, waiting_for_keyboard #TODO: Figure out how to do this without this

    waiting_for_keyboard = False

    try:
        if key.char == 's' and not cog_started:
            cog_started = True
            print("Test started.")
            #return key.char
            passthrough = key.char

        elif (key.char == 'y' or key.char == 'n') and cog_started:
            # Send the 'y' or 'n' response to the server
            print("sent key:", key)
            #return(key.char)
            passthrough = key.char

        elif key.char == 'e':
            cog_completed = True
            print("Exiting program...")
            #return("Exit")
            passthrough = "Exit"

            # Allows the user to exit the test if 'e' is pressed
            #TODO: make this return in a way that indicates the test did not complete
        else:
            print("Invalid Input")
            #TODO: Handle this in some way
                
    except AttributeError:
        pass


def collect_user_info():
    global user_data_sent
    while not user_data_sent:
        print("Please enter user data. Note that validity of data is not checked. Please verify all data before confirming.")
        sequence = input("Please enter a sequence number for the participant:")
        age = input("Pleae enter the participant's age in years:")
        sex = input("Please enter the participant's sex (m or f):")
        height = input("Please enter the participant's height in cm (3 digits):") #I will assume this is always 3 digits, stuff will probably break if it isn't
        # The line below is for data collection, to be changed in final version
        drunk = input("Please indicate if the participant is drunk or sober (d or s):")
        print("You entered the following data: \n Sequence:", sequence, "\n Age:", age, " years, \n Sex:", sex, "\n Height:", height, " cm \n Drunk/Sober:", drunk,)
        if input("\n Is this correct? Enter y if yes, or any other key if no.") == 'y': #Chanel: If incorrect does the while loop keep executing? 
            user_data_sent = True
    
    #TODO: In the final version we need more checks to ensure input is valid
    message = sequence + ' ' + age + ' ' + sex + ' ' + height + ' ' + drunk
    return message

def eye_track_main(response):
    time.sleep(1) #TODO: Do something here

def balance_main(response):
    time.sleep(1) #TODO: Do something here

def next_task(response):
    if user_data_sent == False:
        message = collect_user_info()
    elif user_data_sent == True and cog_started == False:
        message = cognitive_test(None)
    elif cog_started == True and cog_completed == False:
        message = cognitive_test(response)
    elif cog_completed == True and balance_started == False:
        message = balance_main() #TODO: Figure out if we need to pass responses
    elif cog_completed == True and balance_completed == True and eye_track_started == False:
        message = eye_track_main() #TODO: Figure out if we need to pass responses
    else:
        print("All tests complete or error")
        return("finished") #TODO: Actually handle this and check cases

    return message

user_data_sent = False
cog_started = False
cog_completed = False
balance_started = False
balance_completed = False
eye_track_started = False
eye_track_completed = False
response = None

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            message = next_task(response)
            s.sendall(message.encode('utf-8'))
            data = s.recv(1024)
            response = data.decode('utf-8')

except ConnectionRefusedError:
    print("Connection refused. Make Sure Pi script is running.") #TODO: Retry connection automatically
    time.sleep(1)


