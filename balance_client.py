import tkinter as tk

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer App")

        # Initialize timer variables
        self.seconds = 5
        self.timer_running = False

        # Create a label to display the timer
        self.timer_label = tk.Label(root, text="00:00", font=("Helvetica", 48))
        self.timer_label.pack(pady=20)

        # Create Start and Stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Update the timer display
        self.update_timer()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def update_timer(self):
        if self.timer_running:
            self.seconds += 1
            minutes = self.seconds // 60
            seconds = self.seconds % 60
            time_str = f"{minutes:02}:{seconds:02}"
            self.timer_label.config(text=time_str)
            self.root.after(1000, self.update_timer)  # Update every 1 second

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
