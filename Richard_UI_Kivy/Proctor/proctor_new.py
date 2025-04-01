import socket
import kivy
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import json
from kivy.core.window import Window 

IMAGES = {
    "connecting": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/connecting.png",
    "connected": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/connected.png",
    "mainmenu1": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/mainmenu1.png",
    "cognitive1": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/cognitive1.png",
    "cognitive2": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/cognitive2.png",
    "cognitive3": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/cognitive3.png",
    "cognitive4": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/cognitive4.png",
    "mainmenu2": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/mainmenu2.png",
    "balance1": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/balance1.png",
    "balance2": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/balance2.png",
    "balance3": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/balance3.png",
    "balance4": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/balance4.png",
    "balance5": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/balance5.png",
    "mainmenu3": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/mainmenu3.png",
    "eyetracking1": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/eyetracking1.png",
    "eyetracking2": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/eyetracking2.png",
    "eyetracking3": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/eyetracking3.png",
    "eyetracking4": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/eyetracking4.png",
    "eyetracking5": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/eyetracking5.png",
    "mainmenu4": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/mainmenu4.png",
    "calculating": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/calculating.png",
    "results": "/Users/nguyen/Downloads/Proctor/HITS_Proctor_images/results.png"
}

class ClientApp(App):
    def build(self):
        # Set the window to full screen
        Window.fullscreen = False

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("10.0.0.74", 65432))

        self.layout = FloatLayout()  # Use FloatLayout for absolute positioning
        self.image = Image(source=IMAGES["connecting"], size_hint=(1, 1), allow_stretch=True)
        self.layout.add_widget(self.image)

        self.image.source = IMAGES["connected"]
        self.add_continue_button()

        return self.layout

    def add_continue_button(self):
        self.button = Button(text="Continue", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        self.button.bind(on_press=self.enter_info)
        self.layout.add_widget(self.button)

    def enter_info(self, instance):
        self.layout.clear_widgets()
        self.inputs = {}

        # Title field
        self.layout.add_widget(Label(text="Participant Information", size_hint=(None, None), size=(200, 40), pos_hint={"center_x": 0.5, "top": 0.85}))

        # Name field
        self.layout.add_widget(Label(text="Name", size_hint=(None, None), size=(200, 40), pos_hint={"center_x": 0.2, "top": 0.75}))
        self.inputs["Name"] = TextInput(size_hint=(None, None), size=(400, 30), pos_hint={"center_x": 0.5, "top": 0.74})
        self.layout.add_widget(self.inputs["Name"])

        # Age field
        self.layout.add_widget(Label(text="Age", size_hint=(None, None), size=(200, 40), pos_hint={"center_x": 0.2, "top": 0.65}))
        self.inputs["Age"] = TextInput(size_hint=(None, None), size=(400, 30), pos_hint={"center_x": 0.5, "top": 0.64})
        self.layout.add_widget(self.inputs["Age"])

        # Height field
        self.layout.add_widget(Label(text="Height (cm)", size_hint=(None, None), size=(200, 40), pos_hint={"center_x": 0.17, "top": 0.55}))
        self.inputs["Height (cm)"] = TextInput(size_hint=(None, None), size=(400, 30), pos_hint={"center_x": 0.5, "top": 0.54})
        self.layout.add_widget(self.inputs["Height (cm)"])

        # Sex field (Spinner)
        self.layout.add_widget(Label(text="Sex", size_hint=(None, None), size=(200, 40), pos_hint={"center_x": 0.2, "top": 0.45}))
        self.sex_spinner = Spinner(
            text='Male',  # Default selection
            values=('Male', 'Female'),
            size_hint=(None, None),
            size=(400, 40),
            pos_hint={"center_x": 0.5, "top": 0.45}
        )
        self.layout.add_widget(self.sex_spinner)

        self.continue_button = Button(text="Continue", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        self.continue_button.bind(on_press=self.send_info)
        self.layout.add_widget(self.continue_button)

    def send_info(self, instance):
        # Collect user data, convert sex to 0 (Male) or 1 (Female)
        user_data = {field: self.inputs[field].text for field in self.inputs}
        sex = 0 if self.sex_spinner.text == 'Male' else 1  # Convert sex to 0 or 1
        user_data["Sex"] = sex

        # Send data to the server as JSON
        self.client_socket.sendall(json.dumps(user_data).encode())

        # Update layout and image after sending data
        self.layout.clear_widgets()
        self.image.source = IMAGES["mainmenu1"]
        self.layout.add_widget(self.image)

        start_button = Button(text="Colour Word Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.cognitive1)
        self.layout.add_widget(start_button)

        back_button = Button(text="Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        back_button.bind(on_press=self.delete_csv)
        self.layout.add_widget(back_button)

# Colour Word Test Start --------------------------------------

    def cognitive1(self, instance):
        self.client_socket.sendall("cognitive1".encode())
        self.image.source = IMAGES["cognitive1"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.cognitive2)
        self.layout.add_widget(start_button)

    def cognitive2(self, instance):
        self.client_socket.sendall("cognitive2".encode())
        self.image.source = IMAGES["cognitive2"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        yes_button = Button(text="Yes", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        yes_button.bind(on_press=self.cognitive3)
        self.layout.add_widget(yes_button)
        no_button = Button(text="No", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        no_button.bind(on_press=self.cognitive3)
        self.layout.add_widget(no_button)

    def cognitive3(self, instance):
        self.client_socket.sendall("cognitive3".encode())
        self.image.source = IMAGES["cognitive3"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        yes_button = Button(text="Yes", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        yes_button.bind(on_press=self.cognitive4)
        self.layout.add_widget(yes_button)
        no_button = Button(text="No", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        no_button.bind(on_press=self.cognitive4)
        self.layout.add_widget(no_button)

    def cognitive4(self, instance):
        self.client_socket.sendall("cognitive4".encode())
        self.image.source = IMAGES["cognitive4"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        mainmenu_button = Button(text="Main Menu", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        mainmenu_button.bind(on_press=self.mainmenu2)
        self.layout.add_widget(mainmenu_button)
        redo_button = Button(text="Redo Colour Word Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        redo_button.bind(on_press=self.cognitive1)
        self.layout.add_widget(redo_button)

# Colour Word Test End --------------------------------------
# Balance Test Start --------------------------------------

    def mainmenu2(self, instance):
        self.client_socket.sendall("mainmenu2".encode())
        self.layout.clear_widgets()
        self.image.source = IMAGES["mainmenu2"]
        self.layout.add_widget(self.image)

        start_button = Button(text="Balance Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.balance1)
        self.layout.add_widget(start_button)

    def balance1(self, instance):
        self.client_socket.sendall("balance1".encode())
        self.image.source = IMAGES["balance1"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.balance2)
        self.layout.add_widget(start_button)

    def balance2(self, instance):
        self.client_socket.sendall("balance2".encode())
        self.image.source = IMAGES["balance2"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        time_button = Button(text="End Time", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        time_button.bind(on_press=self.balance3)
        self.layout.add_widget(time_button)

    def balance3(self, instance):
        self.client_socket.sendall("balance3".encode())
        self.image.source = IMAGES["balance3"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.balance4)
        self.layout.add_widget(start_button)
        redo_button = Button(text="Redo Balance Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        redo_button.bind(on_press=self.balance1)
        self.layout.add_widget(redo_button)

    def balance4(self, instance):
        self.client_socket.sendall("balance4".encode())
        self.image.source = IMAGES["balance4"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        time_button = Button(text="End Time", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        time_button.bind(on_press=self.balance5)
        self.layout.add_widget(time_button)

    def balance5(self, instance):
        self.client_socket.sendall("balance5".encode())
        self.image.source = IMAGES["balance5"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        mainmenu_button = Button(text="Main Menu", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        mainmenu_button.bind(on_press=self.mainmenu3)
        self.layout.add_widget(mainmenu_button)
        redo_button = Button(text="Redo Balance Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        redo_button.bind(on_press=self.balance1)
        self.layout.add_widget(redo_button)

# Balance Test End --------------------------------------
# Eye tracking Test Start --------------------------------------

    def mainmenu3(self, instance):
        self.client_socket.sendall("mainmenu3".encode())
        self.layout.clear_widgets()
        self.image.source = IMAGES["mainmenu3"]
        self.layout.add_widget(self.image)

        start_button = Button(text="Eye Movement Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.eyetracking1)
        self.layout.add_widget(start_button)

    def eyetracking1(self, instance):
        self.client_socket.sendall("eyetracking1".encode())
        self.image.source = IMAGES["eyetracking1"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.eyetracking2)
        self.layout.add_widget(start_button)

    def eyetracking2(self, instance):
        self.client_socket.sendall("eyetracking2".encode())
        self.image.source = IMAGES["eyetracking2"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        time_button = Button(text="End Time", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        time_button.bind(on_press=self.eyetracking3)
        self.layout.add_widget(time_button)

    def eyetracking3(self, instance):
        self.client_socket.sendall("eyetracking3".encode())
        self.image.source = IMAGES["eyetracking3"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.eyetracking4)
        self.layout.add_widget(start_button)
        redo_button = Button(text="Redo Eye Movement Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        redo_button.bind(on_press=self.eyetracking1)
        self.layout.add_widget(redo_button)

    def eyetracking4(self, instance):
        self.client_socket.sendall("eyetracking4".encode())
        self.image.source = IMAGES["eyetracking4"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        time_button = Button(text="End Time", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        time_button.bind(on_press=self.eyetracking5)
        self.layout.add_widget(time_button)

    def eyetracking5(self, instance):
        self.client_socket.sendall("eyetracking5".encode())
        self.image.source = IMAGES["eyetracking5"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        mainmenu_button = Button(text="Main Menu", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        mainmenu_button.bind(on_press=self.mainmenu4)
        self.layout.add_widget(mainmenu_button)
        redo_button = Button(text="Redo Eye Movement Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        redo_button.bind(on_press=self.eyetracking1)
        self.layout.add_widget(redo_button)

# Eye tracking Test End --------------------------------------

    def mainmenu4(self, instance):
        self.client_socket.sendall("mainmenu4".encode())
        self.layout.clear_widgets()
        self.image.source = IMAGES["mainmenu4"]
        self.layout.add_widget(self.image)

        start_button = Button(text="Calculate Result", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.calculating)
        self.layout.add_widget(start_button)

    def calculating(self, instance):
        self.image.source = IMAGES["calculating"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        time_button = Button(text="End Time", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        time_button.bind(on_press=self.results)
        self.layout.add_widget(time_button)

    def results(self, instance):
        self.image.source = IMAGES["results"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        save_button = Button(text="Save & Exist", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        restart_button = Button(text="Restart", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        restart_button.bind(on_press=self.restart)
        save_button.bind(on_press=self.save_and_exit)
        self.layout.add_widget(save_button)
        self.layout.add_widget(restart_button)

    def restart(self, instance):
        self.client_socket.sendall("DELETE_CSV".encode())
        self.enter_info(instance)

    def save_and_exit(self, instance):
        self.client_socket.sendall("SAVE_AND_EXIT".encode())
        self.client_socket.close()
        exit()

    def delete_csv(self, instance):
        self.client_socket.sendall("DELETE_CSV".encode())
        self.enter_info(instance)

if __name__ == "__main__":
    ClientApp().run()




