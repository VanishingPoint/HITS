
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
    "hosting": r"C:\Users\richy\Documents\Proctor_Test\Test images\hosting.png",
    "connected": r"C:\Users\richy\Documents\Proctor_Test\Test images\connected.png",
    "colourwordtest": r"C:\Users\richy\Documents\Proctor_Test\Test images\colourwordtest.png",
    "inprogress": r"C:\Users\richy\Documents\Proctor_Test\Test images\inprogress.png",
    "end": r"C:\Users\richy\Documents\Proctor_Test\Test images\end.png",
    "results": r"C:\Users\richy\Documents\Proctor_Test\Test images\results.png"
}

class ServerApp(App):
    def build(self):
        # Set the window to full screen
        Window.fullscreen = True

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
            if data == "START_COLOUR_WORD_TEST":
                self.display_color_word_test()
            elif data == "START_TESTING":
                self.display_in_progress()
            elif data == "END_TEST":
                self.display_end()
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

    def display_color_word_test(self):
        self.update_image(IMAGES["colourwordtest"])

    def display_in_progress(self):
        self.update_image(IMAGES["inprogress"])

    def display_end(self):
        self.update_image(IMAGES["end"])

    def display_results(self):
        self.update_image(IMAGES["results"])

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
        print("Shutting down server")
        self.conn.close()
        self.server_socket.close()
        exit()

if __name__ == "__main__":
    app = ServerApp()
    app.run()


