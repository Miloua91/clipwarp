import tkinter as tk
from tkinter import ttk
import pyperclip
import customtkinter
import asyncio
import websockets
from websockets.sync.client import connect
import threading
import json

class WebSocketThread (threading.Thread):
    '''WebSocketThread will make websocket run in an a new thread'''
    
    # overide self init
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name=name
        self.USERS = set()
        print("Start thread", self.name)

    # overide run method
    def run(self):
        # must set a new loop for asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
        # setup a server
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.listen, '192.168.1.9', 5678))
        # keep thread running
        asyncio.get_event_loop().run_forever()

    # listener    
    async def listen(self, websocket, path):
        '''listenner is called each time new client is connected
        websockets already ensures that a new thread is run for each client'''

        print("listen: ", websocket)
        
        # register new client #
        self.USERS.add(websocket)
        await self.notify_users()

        # this loop to get massage from client #
        while True:
            try:
                msg = await websocket.recv()
                if msg is None:
                    break
                await self.handle_message(websocket, msg)

            except websockets.exceptions.ConnectionClosed:
                print("close: ", websocket)
                break

        self.USERS.remove(websocket)
        await self.notify_users()
    
    # message handler        
    async def handle_message(self, client, data):
        print("handle_message: ", client, data)

    
    # example of an action
    # action: notify
    async def notify_users(self):
        '''notify the number of current connected clients'''
        if self.USERS: # asyncio.wait doesn't accept an empty list
            message = json.dumps({'type': 'users', 'count': len(self.USERS)})
            tasks = [asyncio.create_task(user.send(message)) for user in self.USERS]
            await asyncio.wait(tasks)

    # action: action
    async def action(self):
        '''this is an action which will be executed when user presses on button'''
        if self.USERS: # asyncio.wait doesn't accept an empty list
            message = json.dumps({'type': 'activation', 'count':'true'})
            await asyncio.wait([user.send(message) for user in self.USERS])

    # expose action
    def do_activate(self):
        '''this method is exposed to outside, not an async coroutine'''
        # use asyncio to run action
        # must call self.action(), not use self.action, because it must be a async coroutine
        asyncio.set_event_loop().run_until_complete(self.action())


# start WebSocketThread #
threadWebSocket=WebSocketThread("websocket_server")
threadWebSocket.start()

# helper function for window
def clicked():
    threadWebSocket.do_activate()
    lbl.configure(text="Button was clicked !!")
    

root = tk.Tk()
root.title("ClipWarp")
root.geometry("270x300")
root.resizable(False, False)

app = customtkinter.CTk()
app.geometry("270x300")
app.resizable(False, False)


# Create a frame to hold the text area
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=10, padx=10, fill="both", expand=False)

# Create a style to customize the border
style = ttk.Style()
style.configure("RoundedFrame.TFrame", borderwidth=2, relief="raised", border="2", borderradius=10)

# Create the text area
msgEntry = customtkinter.CTkEntry(master=frame, width=250, height=50, corner_radius=5, placeholder_text="put message to dissect here", justify="left")
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


# Create a frame to hold the scrollable section
scrollable_frame = ttk.Frame(root)
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
    canvas.configure(width=event.width, height=event.height)

# Function to scroll with mouse and keys
def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")


def on_key_scroll(event):
    if event.keysym == "Down" or event.char == "j":
        canvas.yview_scroll(1, "units")
    elif event.keysym == "Up" or event.char == "k":
        canvas.yview_scroll(-1, "units")

# Bind arrow keys and "j" and "k" keys globally for scrolling
root.bind_all("<Down>", on_key_scroll)
root.bind_all("<Up>", on_key_scroll)
root.bind_all("<KeyPress-j>", on_key_scroll)
root.bind_all("<KeyPress-k>", on_key_scroll)

# Bind the mouse wheel event to the canvas
canvas.bind("<MouseWheel>", on_mouse_wheel)

# Bind the resize_canvas function to the root window's resize event
root.bind("<Configure>", resize_canvas)

# Example content for the scrollable area
for i in range(20):
    label = tk.Label(scrollable_content, text=f"Label {i}")
    label.pack()

textbox = customtkinter.CTkTextbox(app)

textbox.insert("0.0", "new text to insert")  # insert at line 0 character 0
text = textbox.get("0.0", "end")  # get text from line 0 character 0 till the end
textbox.delete("0.0", "end")  # delete all text
textbox.configure(state="disabled")  # configure textbox to be read-only

root.mainloop()
app.mainloop()
