import asyncio
import atexit
import json
import os
import socket
import sqlite3
import tkinter as tk
from datetime import datetime
from sqlite3 import Error
from threading import Thread
from tkinter import ttk

import customtkinter
import pyperclip
import pystray
import uvicorn
import websockets
from blacksheep import Application
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


async def register(websocket, path):
    if "/" in path:
        name = path  # Assign a specific name for this path
    else:
        name = f"Client_{len(CONNECTIONS) + 1}"

    CONNECTIONS[name] = websocket
    print(f"{name} connected")
    print("Full URL:", path)
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


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def create_db():
    connection = create_connection("./assets/clipwarp.db")

    create_users_table = """
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL
    );
    """

    create_clips_table = """
    CREATE TABLE IF NOT EXISTS clips(
      id INTEGER PRIMARY KEY AUTOINCREMENT, 
      clips_text TEXT NOT NULL, 
      user_id INTEGER NOT NULL, 
      FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """

    execute_query(connection, create_users_table)
    execute_query(connection, create_clips_table)

    return connection


# Call create_db function to create the database and tables
connection = create_db()


async def start_server():
    async with websockets.serve(register, get_ip_address(), 5678):
        print(f"server listening on {get_ip_address()}")
        await asyncio.Future()


def run_server():
    asyncio.run(start_server())


def serve():
    app = Application()

    # serve files contained in a "static" folder relative to the server cwd
    app.serve_files("assets/dist", index_document="index.html")
    uvicorn.run(app, host="localhost", port=6969)


# Create a new thread for the asyncio event loop
thread = Thread(target=run_server)
thread.start()

thread = Thread(target=serve)
thread.start()

uri = f"ws://{get_ip_address()}:5678/Server"  # Change this to the WebSocket server URI


async def send_message(message):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print(f"Sent: {message}")
        insert_clips = f"""
        INSERT INTO clips (clips_text, user_id)
        VALUES ('{message}', 1)
        """


# Function to create and show the GUI window
root = tk.Tk()
root.title("ClipWarp")
root.geometry(
    "+{}+{}".format(root.winfo_screenwidth() - 360, root.winfo_screenheight() - 400)
)
root.resizable(False, False)
root.attributes("-topmost", True)


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


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


added_clip_ids = set()


def add_message_to_scrollable_content(message):

    connection = create_connection("./assets/clipwarp.db")

    select_clips = "SELECT * from clips"
    clips = execute_read_query(connection, select_clips)

    for clip in clips:
        clip_id = clip[0]  # Assuming the first column is the ID
        clip_text = clip[1]  # Assuming the second column is the clips_text
        user_id = clip[2]  # Assuming the third column is the user_id

    # Check if the database is empty
    if not clips:
        # Database is empty, so clear the added_clip_ids set
        added_clip_ids.clear()
        for widget in scrollable_content.winfo_children():
            widget.destroy()
        canvas.update_idletasks()  # Ensure all pending idle tasks are completed
        canvas.config(scrollregion=canvas.bbox("all"))

    # Extract names and IDs and add them to the scrollable content
    for clip in clips:  # Iterate in reverse order            clip_id = clip['id']
        clip_id = clip[0]
        name = clip[1]

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


async def receive_messages():
    uri = f"ws://{get_ip_address()}:5678"  # Change this to the WebSocket server URI
    connection = create_connection("./assets/clipwarp.db")
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            insert_clips = f"""
            INSERT INTO clips (clips_text, user_id)
            VALUES ('{message}', 1)
            """
            execute_query(connection, insert_clips)
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


def exit_prom():
    print("by")
    os._exit(0)


atexit.register(exit_prom)

root.mainloop()
