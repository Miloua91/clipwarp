import asyncio
import json
import os
import socket
import tkinter as tk
from datetime import datetime
from threading import Thread
from tkinter import ttk

import customtkinter
import pyperclip
import pystray
import websockets
from PIL import Image
from pystray import MenuItem as item
from websockets.sync.client import connect


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


CONNECTIONS = {}


async def register(websocket):
    name = f"Client_{len(CONNECTIONS) + 1}"
    CONNECTIONS[name] = websocket
    print(f"{name} connected")
    try:
        async for message in websocket:
            for conn_name, conn in CONNECTIONS.items():
                if conn != websocket:
                    await conn.send(message)
                else:
                    print(f"Message received from {conn_name}: {message}")
        await websocket.wait_closed()

    finally:
        if (
            name in CONNECTIONS
        ):  # Check if the name exists in CONNECTIONS before deleting
            del CONNECTIONS[name]
            print(f"{name} disconnected")


async def start_server():
    async with websockets.serve(register, get_ip_address(), 5678):
        print(f"server listening on {get_ip_address()}")
        await asyncio.Future()


def run_server():
    asyncio.run(start_server())


# Create a new thread for the asyncio event loop
thread = Thread(target=run_server)
thread.start()

uri = "ws://192.168.1.13:5678"  # Change this to the WebSocket server URI


async def send_message(message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print(f"Sent: {message}")


# Function to create and show the GUI window
root = tk.Tk()
root.title("ClipWarp")
root.geometry(
    "+{}+{}".format(root.winfo_screenwidth() - 360, root.winfo_screenheight() - 400)
)
root.resizable(False, False)
root.attributes("-topmost", True)

app = customtkinter.CTk()
app.geometry(
    "+{}+{}".format(app.winfo_screenwidth() - 330, app.winfo_screenheight() - 400)
)
app.resizable(False, False)
app.overrideredirect(True)  # Remove window decorations

# Create a frame to hold the text area
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=10, padx=10, fill="both", expand=False)

# Create a style to customize the border
style = ttk.Style()
style.configure(
    "RoundedFrame.TFrame", borderwidth=2, relief="raised", border="2", borderradius=10
)

# Create the text area
msgEntry = customtkinter.CTkEntry(
    master=frame,
    width=240,
    height=50,
    corner_radius=5,
    placeholder_text="ClipWarp",
    justify="left",
)
msgEntry.pack(pady=2, padx=2)

# Create a frame to hold the buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10, padx=10, fill="both", expand=False)


def on_paste_press(event):
    label_paste.config(image=paste_flat)
    # Get the content of the clipboard
    clipboard_content = pyperclip.paste()
    msgEntry.insert("insert", clipboard_content)


def on_paste_release(event):
    label_paste.config(image=paste)


def on_send_press(event):
    label_send.config(image=send_flat)
    message = msgEntry.get()
    asyncio.run(send_message(message))


def on_send_release(event):
    label_send.config(image=send)


# Load images
paste = tk.PhotoImage(file="./Button/paste.png")
paste_flat = tk.PhotoImage(file="./Button/paste_flat.png")
send = tk.PhotoImage(file="./Button/send.png")
send_flat = tk.PhotoImage(file="./Button/send_flat.png")

# Create label with initial image for paste button
label_paste = tk.Label(button_frame, image=paste)
label_paste.pack(side=tk.LEFT, padx=10, pady=10)

# Create label with initial image for send button
label_send = tk.Label(button_frame, image=send)
label_send.pack(side=tk.LEFT, padx=10, pady=10)

# Bind events to paste button label
label_paste.bind("<ButtonPress-1>", on_paste_press)
label_paste.bind("<ButtonRelease-1>", on_paste_release)

# Bind events to send button label
label_send.bind("<ButtonPress-1>", on_send_press)
label_send.bind("<ButtonRelease-1>", on_send_release)

# Create a frame to hold the scrollable section with a specific width
frame_width = 200
outer_frame = ttk.Frame(root, width=frame_width)
outer_frame.pack(fill="both", expand=True)

# Create the scrollable frame inside the outer frame
scrollable_frame = ttk.Frame(outer_frame)
scrollable_frame.pack(fill="both", expand=True)

# Create a canvas widget inside the scrollable frame
canvas = tk.Canvas(scrollable_frame)
canvas.pack(side=tk.LEFT, fill="both", expand=True)

# Create a frame inside the canvas to contain the scrollable content
scrollable_content = ttk.Frame(canvas)

# Add the scrollable content frame to the canvas
canvas.create_window((0, 0), window=scrollable_content, anchor="nw")


# Function to update the scroll region when the contents of the canvas change
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


# Bind the scrollbar to the canvas
canvas.bind("<Configure>", on_configure)

# Create a scrollbar widget and attach it to the canvas
scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
canvas.configure(yscrollcommand=scrollbar.set)


# Function to resize the canvas when the window is resized
def resize_canvas(event):
    canvas.configure(width=220, height=200)


# Function to scroll with mouse and keys
def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")


def on_key_scroll(event):
    if event.keysym == "Down":
        canvas.yview_scroll(1, "units")
    elif event.keysym == "Up":
        canvas.yview_scroll(-1, "units")


# Bind arrow keys and "j" and "k" keys globally for scrolling
root.bind_all("<Down>", on_key_scroll)
root.bind_all("<Up>", on_key_scroll)

# Bind the mouse wheel event to the canvas
canvas.bind("<MouseWheel>", on_mouse_wheel)

# Bind the resize_canvas function to the root window's resize event
root.bind("<Configure>", resize_canvas)


class Toast(tk.Toplevel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.overrideredirect(True)  # Remove window decorations
        self.geometry(
            "+{}+{}".format(
                parent.winfo_screenwidth() - 250, parent.winfo_screenheight() - 80
            )
        )
        self.attributes("-topmost", True)
        self.configure(bg="black")
        self.label = tk.Label(self, text=text, fg="white", bg="black", padx=10, pady=5)
        self.label.pack()
        self.after(3000, self.destroy)  # Auto-close after 3 seconds


def show_toast(parent, text):
    toast = Toast(parent, text)


# Set to store IDs of clips already added
added_clip_ids = set()


def add_message_to_scrollable_content(message):
    try:
        # Parse the JSON message
        data = json.loads(message)

        # Check if the database is empty
        if not data:
            # Database is empty, so clear the added_clip_ids set
            added_clip_ids.clear()
            for widget in scrollable_content.winfo_children():
                widget.destroy()
            canvas.update_idletasks()  # Ensure all pending idle tasks are completed
            canvas.config(scrollregion=canvas.bbox("all"))

        # Extract names and IDs and add them to the scrollable content
        for clip in data:  # Iterate in reverse order            clip_id = clip['id']
            clip_id = clip["id"]
            name = clip["clip"]

            # Check if the ID already exists in the set of added IDs
            if clip_id not in added_clip_ids:
                label_text = f"{name}"

                # Create label
                label = tk.Label(
                    scrollable_content, text=label_text, wraplength=240, justify="left"
                )
                label.pack(anchor="w")  # Align the label to the left side

                separator = ttk.Separator(scrollable_content, orient="horizontal")
                separator.pack(fill="x", padx=5, pady=5)

                # Bind a copy function to the label
                def copy_label_text(event):
                    root.clipboard_clear()
                    root.clipboard_append(name)
                    show_toast(root, "Text copied to clipboard.")

                label.bind(
                    "<Button-1>", copy_label_text
                )  # Bind left-click event to copy_label_text function

                # Add ID to the set of added IDs
                added_clip_ids.add(clip_id)

        canvas.update_idletasks()  # Ensure all pending idle tasks are completed
        canvas.config(scrollregion=canvas.bbox("all"))

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


async def receive_messages():
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            add_message_to_scrollable_content(message)


def start_msg():
    asyncio.run(receive_messages())


# Create a new thread for the asyncio event loop
thread = Thread(target=start_msg)
thread.start()


# Function to be called when the tray icon is clicked
def on_quit(icon, item):
    icon.stop()
    os._exit(0)


# Define a variable to track the visibility state of the GUI
gui_visible = False


def on_clicked(icon, item):
    global gui_visible
    if gui_visible:
        root.withdraw()
        gui_visible = False
    else:
        gui_visible = True
        root.deiconify()


def run_gui():
    global gui_visible
    # Create a tray icon
    image = Image.open("./assets/cw.ico")

    clip_warp = pystray.Icon(
        name="ClipWarp",
        icon=image,
        title="ClipWarp",
        menu=pystray.Menu(
            pystray.MenuItem(text="CW", action=on_clicked, default=True),
            pystray.MenuItem(text="Exit", action=on_quit),
        ),
    )

    # Run the app
    clip_warp.run()


# Start the GUI in a separate thread
gui_thread = Thread(target=run_gui)
gui_thread.start()

root.mainloop()
app.mainloop()
