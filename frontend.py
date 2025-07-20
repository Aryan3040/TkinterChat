# client.py

import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, ttk
import requests
import threading
import time

# --------------------------
# Configuration
# --------------------------

SERVER_URL = "http://localhost:5003"  # Replace with your server's IP and port

# --------------------------
# Global Variables
# --------------------------

username = None
current_chat = None  # Can be a username or room_id
chats = set()
messages = {}  # {chat_id: [{'sender': sender, 'message': message}, ...]}
last_message_id = 0
app_window = None
chat_display = None
online_users_tree = None
chats_tree = None
announcement_var = None

# --------------------------
# Helper Functions
# --------------------------

def register_user(root):
    global username
    while True:
        username = simpledialog.askstring("Username", "Please enter your username:", parent=root)
        if not username:
            messagebox.showerror("Error", "Username cannot be empty.")
            continue
        try:
            response = requests.post(f"{SERVER_URL}/register", json={'username': username})
            if response.status_code == 200:
                messagebox.showinfo("Success", response.json().get('message'))
                break
            else:
                messagebox.showerror("Error", response.json().get('message'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {e}")
            root.destroy()
            exit()

def send_message_api(recipient, message):
    payload = {
        'sender': username,
        'recipient': recipient,
        'message': message
    }
    try:
        response = requests.post(f"{SERVER_URL}/send", json=payload)
        if response.status_code != 200:
            messagebox.showerror("Error", response.json().get('message'))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send message: {e}")

def create_room_api(participants):
    payload = {
        'admin': username,
        'participants': participants
    }
    try:
        response = requests.post(f"{SERVER_URL}/create_room", json=payload)
        if response.status_code == 200:
            data = response.json()
            room_id = data.get('room_id')
            if room_id:
                chats.add(room_id)
                update_chats_tree()
                append_chat(f"--- Group Chat {room_id.split('_')[1]} created with: {', '.join(participants)} ---")
                # Set as current chat
                global current_chat
                current_chat = room_id
                append_chat(f"--- Switched to Group Chat {room_id.split('_')[1]} ---")
        else:
            messagebox.showerror("Error", response.json().get('message'))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create room: {e}")

def fetch_messages():
    global last_message_id
    params = {
        'username': username,
        'last_id': last_message_id
    }
    try:
        response = requests.get(f"{SERVER_URL}/messages", params=params)
        if response.status_code == 200:
            data = response.json()
            new_msgs = data.get('messages', [])
            for msg in new_msgs:
                last_message_id = max(last_message_id, msg['id'])
                recipient = msg['recipient']
                sender = msg['sender']
                if recipient.startswith('room_'):
                    chat_id = recipient
                else:
                    # Direct message
                    if recipient == username:
                        chat_id = sender
                    else:
                        chat_id = recipient
                if chat_id not in chats:
                    chats.add(chat_id)
                    update_chats_tree()
                    append_chat(f"--- New chat initiated with {chat_id_display(chat_id)} ---")
                if chat_id not in messages:
                    messages[chat_id] = []
                message_content = msg['message']
                if sender == 'server' and message_content.startswith('Room '):
                    # Parse room creation
                    try:
                        room_number = message_content.split('Room ')[1].split(' ')[0]
                        room_id = f'room_{room_number}'
                        if room_id not in chats:
                            chats.add(room_id)
                            update_chats_tree()
                            append_chat(f"--- Group Chat {room_number} has been created ---")
                        # Set as current_chat
                        global current_chat
                        current_chat = room_id
                        append_chat(f"--- Switched to Group Chat {room_number} ---")
                    except IndexError:
                        print("[Error] Failed to parse room creation message.")
                else:
                    # Store the message with sender info
                    messages[chat_id].append({'sender': sender, 'message': message_content})
                    if current_chat == chat_id:
                        if sender == username:
                            display_name = "You"
                        else:
                            display_name = sender
                        append_chat(f"{display_name}: {message_content}")
        else:
            print(f"Failed to fetch messages: {response.json().get('message')}")
    except Exception as e:
        print(f"Error fetching messages: {e}")

def fetch_announcement():
    try:
        response = requests.get(f"{SERVER_URL}/announcement")
        if response.status_code == 200:
            data = response.json()
            announcement = data.get('announcement', '')
            announcement_var.set(f"Announcement: {announcement}")
        else:
            print(f"Failed to fetch announcement: {response.json().get('message')}")
    except Exception as e:
        print(f"Error fetching announcement: {e}")

def poll_messages():
    while True:
        fetch_messages()
        update_online_users_tree()  # Periodically update online users
        fetch_announcement()
        time.sleep(2)  # Poll every 2 seconds

def start_polling():
    polling_thread = threading.Thread(target=poll_messages, daemon=True)
    polling_thread.start()

# --------------------------
# GUI Functions
# --------------------------

def start_gui(root):
    global chat_display, online_users_tree, chats_tree, app_window, announcement_var

    app_window = tk.Toplevel(root)
    app_window.title(f"Python Chatroom - {username}")
    app_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(app_window))

    # Announcements Section
    announcement_frame = tk.Frame(app_window)
    announcement_frame.pack(fill=tk.X, padx=10, pady=5)
    announcement_label = tk.Label(announcement_frame, text="Announcement:", font=('Arial', 12, 'bold'))
    announcement_label.pack(side=tk.LEFT)
    announcement_var = tk.StringVar()
    announcement_content = tk.Label(announcement_frame, textvariable=announcement_var, font=('Arial', 12), fg='blue')
    announcement_content.pack(side=tk.LEFT, padx=5)

    # Left frame for online users and chats
    left_frame = tk.Frame(app_window)
    left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

    # Right frame for chat display and message entry
    right_frame = tk.Frame(app_window)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Online users label and treeview
    users_label = tk.Label(left_frame, text="Online Users")
    users_label.pack()

    online_users_tree = ttk.Treeview(left_frame, columns=("Username",), show='headings', selectmode="extended")
    online_users_tree.heading("Username", text="Username")
    online_users_tree.pack(pady=5, fill=tk.BOTH, expand=True)

    # Chats label and treeview
    chats_label = tk.Label(left_frame, text="Chats")
    chats_label.pack()

    chats_tree = ttk.Treeview(left_frame, columns=("Chat ID",), show='headings', selectmode="browse")
    chats_tree.heading("Chat ID", text="Chat ID")
    chats_tree.pack(pady=5, fill=tk.BOTH, expand=True)

    # Buttons for DM and Group Chat
    dm_button = tk.Button(left_frame, text="Send DM", command=lambda: send_dm(online_users_tree))
    dm_button.pack(pady=5, fill=tk.X)

    group_chat_button = tk.Button(left_frame, text="Create Group Chat", command=lambda: create_group_chat_gui(online_users_tree))
    group_chat_button.pack(pady=5, fill=tk.X)

    # Chat display
    chat_display = scrolledtext.ScrolledText(right_frame, state='disabled', width=60, height=25)
    chat_display.pack(pady=5, fill=tk.BOTH, expand=True)

    # Message entry
    entry_frame = tk.Frame(right_frame)
    entry_frame.pack(pady=5, fill=tk.X)

    message_entry = tk.Entry(entry_frame, width=50)
    message_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    message_entry.bind("<Return>", lambda event: send_chat(message_entry, chat_display))

    send_button = tk.Button(entry_frame, text="Send", command=lambda: send_chat(message_entry, chat_display))
    send_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Switch chat button
    switch_chat_button = tk.Button(left_frame, text="Switch Chat", command=lambda: switch_chat_gui())
    switch_chat_button.pack(pady=5, fill=tk.X)

    # Assign to global variables for access
    globals()['chat_display'] = chat_display
    globals()['online_users_tree'] = online_users_tree
    globals()['chats_tree'] = chats_tree

    # Populate online users
    update_online_users_tree()

def append_chat(message):
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, message + "\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.see(tk.END)

def send_chat(message_entry, chat_display):
    global current_chat
    message = message_entry.get().strip()
    if not message:
        return
    message_entry.delete(0, tk.END)
    if current_chat:
        send_message_api(current_chat, message)
        append_chat(f"You: {message}")
    else:
        messagebox.showwarning("No Chat Selected", "Please select a chat to send messages.")

def send_dm(online_users_tree):
    selected = online_users_tree.selection()
    if len(selected) != 1:
        messagebox.showwarning("Select One User", "Please select exactly one user to send a DM.")
        return
    recipient = online_users_tree.item(selected[0], 'values')[0]
    global current_chat
    current_chat = recipient
    if recipient not in chats:
        chats.add(recipient)
        update_chats_tree()
    append_chat(f"--- Direct Message with {recipient} ---")

def create_group_chat_gui(online_users_tree):
    selected = online_users_tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one user to create a group chat.")
        return
    participants = [online_users_tree.item(user, 'values')[0] for user in selected]
    if username in participants:
        messagebox.showwarning("Invalid Selection", "You cannot add yourself to the group chat.")
        return
    create_room_api(participants)

def switch_chat_gui():
    selected = chats_tree.selection()
    if not selected:
        messagebox.showwarning("No Chat Selected", "Please select a chat to switch to.")
        return
    chat_id_display = chats_tree.item(selected[0], 'values')[0]
    # Find the actual chat_id based on display
    if chat_id_display.startswith('Group Chat'):
        room_number = chat_id_display.split(' ')[-1]
        chat_id = f'room_{room_number}'
    else:
        chat_id = chat_id_display
    global current_chat
    current_chat = chat_id
    append_chat(f"--- Chat with {chat_id_display} ---")
    if chat_id in messages:
        for msg in messages[chat_id]:
            if msg['sender'] == username:
                display_name = "You"
            else:
                display_name = msg['sender']
            append_chat(f"{display_name}: {msg['message']}")

def chat_id_display(chat_id):
    if chat_id.startswith('room_'):
        return f"Group Chat {chat_id.split('_')[1]}"
    else:
        return f"{chat_id}"

def update_chats_tree():
    try:
        chats_tree.delete(*chats_tree.get_children())
        for chat in chats:
            display_name = chat_id_display(chat)
            chats_tree.insert("", tk.END, values=(display_name,))
    except Exception as e:
        print(f"Error updating chats tree: {e}")

def get_announcement():
    try:
        response = requests.get(f"{SERVER_URL}/announcement")
        if response.status_code == 200:
            data = response.json()
            announcement = data.get('announcement', '')
            return announcement
        else:
            print(f"Failed to fetch announcement: {response.json().get('message')}")
            return ""
    except Exception as e:
        print(f"Error fetching announcement: {e}")
        return ""

def fetch_messages():
    global last_message_id
    params = {
        'username': username,
        'last_id': last_message_id
    }
    try:
        response = requests.get(f"{SERVER_URL}/messages", params=params)
        if response.status_code == 200:
            data = response.json()
            new_msgs = data.get('messages', [])
            for msg in new_msgs:
                last_message_id = max(last_message_id, msg['id'])
                recipient = msg['recipient']
                sender = msg['sender']
                if recipient.startswith('room_'):
                    chat_id = recipient
                else:
                    # Direct message
                    if recipient == username:
                        chat_id = sender
                    else:
                        chat_id = recipient
                if chat_id not in chats:
                    chats.add(chat_id)
                    update_chats_tree()
                    append_chat(f"--- New chat initiated with {chat_id_display(chat_id)} ---")
                if chat_id not in messages:
                    messages[chat_id] = []
                message_content = msg['message']
                if sender == 'server' and message_content.startswith('Room '):
                    # Parse room creation
                    try:
                        room_number = message_content.split('Room ')[1].split(' ')[0]
                        room_id = f'room_{room_number}'
                        if room_id not in chats:
                            chats.add(room_id)
                            update_chats_tree()
                            append_chat(f"--- Group Chat {room_number} has been created ---")
                        # Set as current_chat
                        global current_chat
                        current_chat = room_id
                        append_chat(f"--- Switched to Group Chat {room_number} ---")
                    except IndexError:
                        print("[Error] Failed to parse room creation message.")
                else:
                    # Store the message with sender info
                    messages[chat_id].append({'sender': sender, 'message': message_content})
                    if current_chat == chat_id:
                        if sender == username:
                            display_name = "You"
                        else:
                            display_name = sender
                        append_chat(f"{display_name}: {message_content}")
        else:
            print(f"Failed to fetch messages: {response.json().get('message')}")
    except Exception as e:
        print(f"Error fetching messages: {e}")

def fetch_announcement():
    try:
        response = requests.get(f"{SERVER_URL}/announcement")
        if response.status_code == 200:
            data = response.json()
            announcement = data.get('announcement', '')
            announcement_var.set(f"Announcement: {announcement}")
        else:
            print(f"Failed to fetch announcement: {response.json().get('message')}")
    except Exception as e:
        print(f"Error fetching announcement: {e}")

def poll_messages():
    while True:
        fetch_messages()
        update_online_users_tree()  # Periodically update online users
        fetch_announcement()
        time.sleep(2)  # Poll every 2 seconds

def start_polling():
    polling_thread = threading.Thread(target=poll_messages, daemon=True)
    polling_thread.start()

# --------------------------
# Online Users Handling
# --------------------------

def update_online_users_tree():
    try:
        # Step 1: Get the currently selected users
        selected_items = online_users_tree.selection()
        selected_users = [online_users_tree.item(item)['values'][0] for item in selected_items]

        # Step 2: Fetch the latest online users from the server
        response = requests.get(f"{SERVER_URL}/online")
        if response.status_code == 200:
            data = response.json()
            users = data.get('online_users', [])

            # Step 3: Repopulate the Treeview with the latest users
            populate_online_users(users)

            # Step 4: Re-select the previously selected users if they are still online
            for user in selected_users:
                if user in users:
                    # Find the Treeview item corresponding to the user
                    for item in online_users_tree.get_children():
                        if online_users_tree.item(item)['values'][0] == user:
                            online_users_tree.selection_add(item)
                            break
        else:
            print(f"Failed to fetch online users: {response.json().get('message')}")
    except Exception as e:
        print(f"Error fetching online users: {e}")

def populate_online_users(users):
    # Clear existing entries
    online_users_tree.delete(*online_users_tree.get_children())
    for user in users:
        if user != username:  # Exclude self
            online_users_tree.insert("", tk.END, values=(user,))

# --------------------------
# Main Function
# --------------------------

def main():
    global app_window, chat_display, online_users_tree, chats_tree, announcement_var

    # Initialize Tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the root window during registration

    # Register user
    register_user(root)

    # Start the main GUI
    start_gui(root)

    # Start polling messages
    start_polling()

    # Show the main GUI window
    root.deiconify()
    app_window.mainloop()

def on_closing(window):
    try:
        # Call the /logout endpoint to remove the user from online users
        response = requests.post(f"{SERVER_URL}/logout", json={'username': username})
        if response.status_code == 200:
            print(response.json().get('message'))
        else:
            print(f"Logout failed: {response.json().get('message')}")
    except Exception as e:
        print(f"Error during logout: {e}")
    window.destroy()

if __name__ == "__main__":
    main()
