from PIL import Image
import socket
import time
from pynput.keyboard import Listener

# Socket connection information
HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

image_numbers = list(range(0, 17)) # image 0 is explanation, others are answers corresponding to the participant images

image_paths_cognitive = [
    # fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_proctor_page_{num}.png" # Triss
    # fr"C:\Users\richy\Downloads\cognitive\images\cognitive_proctor_page_{num}.png" # Richard
    fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_proctor_page_{num}.png" # Chanel
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

        # Show the explanation image first (cognitive_proctor_page_0)
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
    global passthrough, cognitive_started, cognitive_completed, waiting_for_keyboard 

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
        else:
            print("Invalid Input")         
    except AttributeError:
        pass

def collect_user_info():
    global user_data_sent
    while not user_data_sent:
        print("Please enter user data. Note that validity of data is not checked. Please verify all data before confirming.")
        sequence = input("Please enter a sequence number for the participant:")
        age = input("Please enter the participant's age in years:")
        sex = input("Please enter the participant's sex (m or f):")
        print("You entered the following data: \n Sequence:", sequence, "\n Age:", age, " years, \n Sex:", sex)
        if input("\n Is this correct? Enter y if yes, or any other key if no.") == 'y':
            user_data_sent = True
    
    #TODO: In the final version we need more checks to ensure input is valid
    message = sequence + ' ' + age + ' ' + sex + ' ' 
    return message

def eye_tracking_test(response):
    global waiting_for_keyboard
    if response == "Waiting to Start Eye Tracking" or response == "Waiting to start Vertical Test":
        # Show instructions
        #show_image('/Users/test/Documents/HITS/Eye Tracking/Eye Tracking Proctor Images/eyetracking_proctor_0.png') # Triss
        show_image('C:/Users/chane/Desktop/HITS/HITS/Eye Tracking/Eye Tracking Proctor Images/eyetracking_proctor_0.png') # Chanel
        waiting_for_keyboard = True
        listener = Listener(on_press=lambda event: on_press_eye_tracking(event))
        listener.start()

        while waiting_for_keyboard:
                time.sleep(1)
        listener.stop()

        print("Passthrough Current Value:", passthrough)
        return passthrough
    
    elif response == "Finished Vertical Test Videos, Ready to Process":
        print(response)
        print("Instruct the participant to remove the headset. Processing will now begin.") 
        return ("Start Processing")
    
    else:
        print("Error in Eye Tracking Cases or test complete")

def on_press_eye_tracking(key):
    global passthrough, waiting_for_keyboard
    if key.char == 's':
        passthrough = 's'
        waiting_for_keyboard = False
        print("Sending start")
    else:
        print("Invalid Key")
        return eye_tracking_test()
        

def balance_test():
    global balance_completed, balance_started, waiting_for_keyboard, balance_first_test_complete

    balance_started = True
    if balance_completed == False and balance_first_test_complete == False:
        #Show instructions
        show_image('C:/Users/chane/Desktop/HITS/HITS/Balance/Balance Proctor Images/balance_proctor_page_0.png') # Chanel
        # show_image("/Users/test/Documents/HITS/Balance/Balance Proctor Images/balance_proctor_page_0.png") #Triss
        waiting_for_keyboard = True
        listener = Listener(on_press=lambda event: on_press_balance(event))
        listener.start()

        while waiting_for_keyboard:
            time.sleep(1)
        listener.stop()
        balance_first_test_complete = True

    elif balance_completed == False and balance_first_test_complete == True:
        print("First balance test completed. Press 's' to start second test.") 
        show_image('C:/Users/chane/Desktop/HITS/HITS/Balance/Balance Proctor Images/balance_proctor_page_1.png') # Chanel
        # show_image("/Users/test/Documents/HITS/Balance/Balance Proctor Images/balance_proctor_page_1.png") #Triss
        waiting_for_keyboard = True
        listener = Listener(on_press=lambda event: on_press_balance(event))
        listener.start()

        while waiting_for_keyboard:
            time.sleep(1)
        listener.stop()

        balance_completed = True

    else:
        print("Error in Balance Cases")
 
    print("Passthrough Current Value:", passthrough)
    return passthrough

    # Comment the above and uncomment the below to skip balance
    balance_started = True
    balance_completed = True
    return "Balance Skipped"

def on_press_balance(key):
    global passthrough, waiting_for_keyboard
    if key.char == 's':
        passthrough = 's'
        waiting_for_keyboard = False
        print("Sending Start")
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
    elif cognitive_completed == True and balance_completed == False:
        message = balance_test() 
    elif cognitive_completed == True and balance_completed == True:
        message = eye_tracking_test(response)
    else:
        print("All tests complete or an error occured")
        return("Finished") 

    return message

waiting_for_keyboard = False
user_data_sent = False
cognitive_started = False
cognitive_completed = False
balance_started = False
balance_completed = False
response = None
balance_first_test_complete = False

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            message = next_task(response)
            s.sendall(message.encode('utf-8'))
            data = s.recv(1024)
            response = data.decode('utf-8')

except ConnectionRefusedError:
    print("Connection refused. Make Sure Pi script is running.") 
    time.sleep(1)

