from PIL import Image
import socket
import time
from pynput.keyboard import Listener

# Socket connection information
HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# Setting up the array of image numbers for the cognitive test
#TODO: Once cognitive test works, make this explicitly for cog images only, generalize image open function
image_numbers = list(range(0, 4)) # image 0 is explanation, others are answers corresponding to the participant images

image_paths_cognitive = [
     fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Triss
    # fr"C:\Users\richy\Downloads\cognitive\images\cognitive_page_{num}.png" # Richard
    # fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Chanel
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
    global cognitive_started, cognitive_completed, waiting_for_keyboard

    if cognitive_started == True:
        if (response == 'end'):
                print("Cognitive Test Complete")
                cognitive_completed = True
                return "Start Balance"
        else:
            print(f"Received image number: {response}")
            show_image(image_paths_cognitive[int(response)])  # Show the next randomized image

            waiting_for_keyboard = True
            listener = Listener(on_press=lambda event: on_press_cognitive(event))
            listener.start()

            while waiting_for_keyboard:
                time.sleep(1)
            listener.stop()

    elif cognitive_started == False:
        print("Press 's' to start the randomized image sequence.")
        print("Press 'y' or 'n' to open the next image after starting.")
        print("Press 'e' to exit the program.")

        # Show the explanation image first (cognitive_page_0)
        show_image(image_paths_cognitive[0])
        
        waiting_for_keyboard = True
        listener = Listener(on_press=lambda event: on_press_cognitive(event))
        listener.start()

        while waiting_for_keyboard:
                time.sleep(1)
        listener.stop()
        
    print("Returning Passthrough")
    return passthrough

def on_press_cognitive(key):
    global passthrough, cognitive_started, cognitive_completed, waiting_for_keyboard #TODO: Figure out how to do this without this

    waiting_for_keyboard = False

    try:
        if key.char == 's' and not cognitive_started:
            cognitive_started = True
            print("Test started.")
            #return key.char
            passthrough = key.char

        elif (key.char == 'y' or key.char == 'n') and cognitive_started:
            # Send the 'y' or 'n' response to the server
            print("sent key:", key)
            #return(key.char)
            passthrough = key.char

        elif key.char == 'e':
            cognitive_completed = True
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

def eye_tracking_test():
    global waiting_for_keyboard
    #Show instructions
    #show_image('/Users/test/Documents/HITS/Eye Tracking/Eye Tracking Proctor Images/eyetrackingproctor_0.png') # Triss
    show_image('C:/Users/chane/Desktop/HITS/HITS/Eye Tracking/Eye Tracking Proctor Images/eyetrackingproctor_0.png') # Chanel
    waiting_for_keyboard = True
    listener = Listener(on_press=lambda event: on_press_eye_tracking(event))
    listener.start()

    while waiting_for_keyboard:
            time.sleep(1)
    listener.stop()

    print("Passthrough Current Val:", passthrough)
    return passthrough

def on_press_eye_tracking(key):
    global passthrough, waiting_for_keyboard
    if key.char == 's':
        passthrough = 's'
        waiting_for_keyboard = False
        print("sending start")
    else:
        print("Invalid Key")
        return eye_tracking_test()
        

def balance_test():
    global balance_completed, balance_started, waiting_for_keyboard
    '''
    #Show instructions
    show_image('C:/Users/chane/Desktop/HITS/HITS/Balance/Balance Proctor Images/balance_page_0') # Chanel

    waiting_for_keyboard = True
    listener = Listener(on_press=lambda event: on_press_balance(event))
    listener.start()

    balance_started = True
    balance_completed = True

    while waiting_for_keyboard:
            time.sleep(1)
    listener.stop()

    print("Passthrough Current Val:", passthrough)
    return passthrough
    '''
    return "Balance Skipped"

def on_press_balance(key):
    global passthrough, waiting_for_keyboard
    if key.char == 's':
        passthrough = 's'
        waiting_for_keyboard = False
        print("sending start")
    else:
        print("Invalid Key")
        return balance_test()

def next_task(response):
    if user_data_sent == False:
        message = collect_user_info()
    elif user_data_sent == True and cognitive_started == False:
        message = cognitive_test(None)
    elif cognitive_started == True and cognitive_completed == False:
        message = cognitive_test(response)
    elif cognitive_completed == True and balance_started == False:
        message = balance_test() #TODO: Figure out if we need to pass responses
    elif cognitive_completed == True and balance_completed == True:
        message = eye_tracking_test() #TODO: Figure out if we need to pass responses
    else:
        print("All tests complete or error")
        return("finished") #TODO: Actually handle this and check cases

    return message

waiting_for_keyboard = False
user_data_sent = False
cognitive_started = False
cognitive_completed = False
balance_started = False
balance_completed = False
eye_tracking_started = False # we never use this
eye_tracking_completed = False # we never use this
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


