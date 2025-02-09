import sys
import tkinter
from PIL import Image, ImageTk
import time

# Global variable to store the root window reference
root = None

def showPIL(pilImage):
    global root
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root, width=w, height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.LANCZOS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2, h/2, image=image)
    root.after(5000, close_image_window)  # Schedule the window to close after 5000ms (5 seconds)
    root.mainloop()

def close_image_window():
    global root
    if root:
        root.destroy()
        root = None

pilImage = Image.open("bingbong.png")
showPIL(pilImage)