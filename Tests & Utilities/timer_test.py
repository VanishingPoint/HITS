import tkinter as tk

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.attributes('-fullscreen', True)  # Make the window fullscreen
        self.time_left = 120  # 2 minutes in seconds
        self.label = tk.Label(root, text=self.format_time(self.time_left), font=("Helvetica", 48), fg='red')
        self.label.pack(expand=True)
        self.running = False
        self.start_timer()  # Start the timer as soon as the window is created

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def start_timer(self):
        if not self.running:
            self.running = True
            self.countdown()

    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label.config(text=self.format_time(self.time_left))
            self.root.after(1000, self.countdown)
        else:
            self.running = False
            self.root.destroy()  # Close the window when the countdown finishes

if __name__ == "__main__":
    root = tk.Tk()
    timer = CountdownTimer(root)
    root.mainloop()