
import pystray
import tkinter as tk
from pystray import MenuItem as item
from PIL import Image

# Function to create and show the GUI window
def show_gui():
    gui_window = tk.Tk()
    gui_window.title("ClipWarp")
    label = tk.Label(gui_window, text="Hello, this is my app's GUI!")
    label.pack()
    gui_window.mainloop()

# Function to be called when the tray icon is clicked
def on_clicked(icon, item):
    show_gui()

# Create a tray icon
image = Image.open("icon.ico")

clip_warp = pystray.Icon(name="ClipWarp",icon=image,title="ClipWarp",menu=pystray.Menu(
    pystray.MenuItem(text="Open Tab",action=show_gui,default=True),
))


# Run the app
clip_warp.run()

