
import socket
import kivy
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import csv
import threading
import json
import os
from kivy.core.window import Window

IMAGES = {
    "hosting": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\hosting.png",
    "connected": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\connected.png",
    "cognitive1": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\cognitive1.png",
    "cognitive2": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\cognitive2.png",
    "cognitive3": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\cognitive3.png",
    "cognitive4": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\cognitive4.png",
    "waiting": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\waiting.png",
    "balance1": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\balance1.png",
    "balance2": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\balance2.png",
    "balance3": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\balance3.png",
    "balance4": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\balance4.png",
    "balance5": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\balance5.png",
    "eyetracking1": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\eyetracking1.png",
    "eyetracking2": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\eyetracking2.png",
    "eyetracking3": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\eyetracking3.png",
    "eyetracking4": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\eyetracking4.png",
    "eyetracking5": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\eyetracking5.png",
    "finish": r"C:\Users\richy\Documents\Proctor_Test\HITS_Participant_images\finish.png"
}

class ServerApp(App):
    def build(self):
        # Set the window to full screen
        Window.fullscreen = False

        self.layout = BoxLayout(orientation='vertical')
        self.image = Image(source=IMAGES["hosting"], size_hint=(1,1), allow_stretch=True)
        self.layout.add_widget(self.image)

        threading.Thread(target=self.start_server, daemon=True).start()

        return self.layout

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("10.0.0.76", 65432))
        self.server_socket.listen(1)
        print("Hosting...")
       
        self.conn, self.addr = self.server_socket.accept()
        print("Connection successful")

        self.update_image(IMAGES["connected"])

        self.handle_client()

    def handle_client(self):
        while True:
            data = self.conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("{"):
                user_data = json.loads(data)
                self.save_to_csv(user_data)
            if data == "cognitive1":
                self.display_cognitive1()
            elif data == "cognitive2":
                self.display_cognitive2()
            elif data == "cognitive3":
                self.display_cognitive3()
            elif data == "cognitive4":
                self.display_cognitive4()
            elif data == "mainmenu2":
                self.display_waiting()
            elif data == "balance1":
                self.display_balance1()
            elif data == "balance2":
                self.display_balance2()
            elif data == "balance3":
                self.display_balance3()
            elif data == "balance4":
                self.display_balance4()
            elif data == "balance5":
                self.display_balance5()
            elif data == "mainmenu3":
                self.display_waiting()
            elif data == "eyetracking1":
                self.display_eyetracking1()
            elif data == "eyetracking2":
                self.display_eyetracking2()
            elif data == "eyetracking3":
                self.display_eyetracking3()
            elif data == "eyetracking4":
                self.display_eyetracking4()
            elif data == "eyetracking5":
                self.display_eyetracking5()
            elif data == "mainmenu4":
                self.display_waiting()
            elif data == "SAVE_AND_EXIT":
                self.close_server()
            elif data == "DELETE_CSV":
                self.delete_csv()

    def save_to_csv(self, data):
        file_path = "user_data.csv"
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data["Name"], data["Age"], data["Height (cm)"], data["Sex"]])
        print("Data saved to CSV.")

    def display_cognitive1(self):
        self.update_image(IMAGES["cognitive1"])

    def display_cognitive2(self):
        self.update_image(IMAGES["cognitive2"])

    def display_cognitive3(self):
        self.update_image(IMAGES["cognitive3"])

    def display_cognitive4(self):
        self.update_image(IMAGES["cognitive4"])

    def display_balance1(self):
        self.update_image(IMAGES["balance1"])

    def display_balance2(self):
        self.update_image(IMAGES["balance2"])

    def display_balance3(self):
        self.update_image(IMAGES["balance3"])

    def display_balance4(self):
        self.update_image(IMAGES["balance4"])

    def display_balance5(self):
        self.update_image(IMAGES["balance5"])

    def display_eyetracking1(self):
        self.update_image(IMAGES["eyetracking1"])

    def display_eyetracking2(self):
        self.update_image(IMAGES["eyetracking2"])

    def display_eyetracking3(self):
        self.update_image(IMAGES["eyetracking3"])

    def display_eyetracking4(self):
        self.update_image(IMAGES["eyetracking4"])

    def display_eyetracking5(self):
        self.update_image(IMAGES["eyetracking5"])

    def display_waiting(self):
        self.update_image(IMAGES["waiting"])

    def update_image(self, image_path):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._update_image(image_path), 0)

    def _update_image(self, image_path):
        self.layout.remove_widget(self.image)
        self.image = Image(source=image_path, size_hint=(1,1), allow_stretch=True)
        self.layout.add_widget(self.image)

    def delete_csv(self):
        file_path = "user_data.csv"
        if os.path.exists(file_path):
            os.remove(file_path)
            print("CSV file deleted.")

    def close_server(self):
        self.update_image(IMAGES["finish"])
        print("Shutting down server")
        self.conn.close()
        self.server_socket.close()
        exit()

if __name__ == "__main__":
    app = ServerApp()
    app.run()


