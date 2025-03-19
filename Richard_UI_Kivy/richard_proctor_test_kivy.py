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
    "connecting": "/Users/nguyen/Downloads/Participant_Test/Test images/connecting.png",
    "connected": "/Users/nguyen/Downloads/Participant_Test/Test images/connected.png",
    "mainmenu": "/Users/nguyen/Downloads/Participant_Test/Test images/mainmenu.png",
    "colourwordtest": "/Users/nguyen/Downloads/Participant_Test/Test images/colourwordtest.png",
    "inprogress": "/Users/nguyen/Downloads/Participant_Test/Test images/inprogress.png",
    "end": "/Users/nguyen/Downloads/Participant_Test/Test images/end.png",
    "results": "/Users/nguyen/Downloads/Participant_Test/Test images/results.png"
}

class ClientApp(App):
    def build(self):
        # Set the window to full screen
        Window.fullscreen = True

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("10.0.0.76", 65432))

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
        self.image.source = IMAGES["mainmenu"]
        self.layout.add_widget(self.image)

        start_button = Button(text="Start Colour Word Test", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        start_button.bind(on_press=self.start_test)
        self.layout.add_widget(start_button)

        back_button = Button(text="Back", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.2, "top": 0.15})
        back_button.bind(on_press=self.delete_csv)
        self.layout.add_widget(back_button)

    def start_test(self, instance):
        self.client_socket.sendall("START_COLOUR_WORD_TEST".encode())
        self.image.source = IMAGES["colourwordtest"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        testing_button = Button(text="Testing", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        testing_button.bind(on_press=self.start_testing)
        self.layout.add_widget(testing_button)

    def start_testing(self, instance):
        self.client_socket.sendall("START_TESTING".encode())
        self.image.source = IMAGES["inprogress"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        end_button = Button(text="End", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        end_button.bind(on_press=self.end_test)
        self.layout.add_widget(end_button)

    def end_test(self, instance):
        self.client_socket.sendall("END_TEST".encode())
        self.image.source = IMAGES["end"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        calculate_button = Button(text="Calculate Results", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
        calculate_button.bind(on_press=self.calculate_results)
        self.layout.add_widget(calculate_button)

    def calculate_results(self, instance):
        self.image.source = IMAGES["results"]
        self.layout.clear_widgets()
        self.layout.add_widget(self.image)
        save_button = Button(text="Save", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.8, "top": 0.15})
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




