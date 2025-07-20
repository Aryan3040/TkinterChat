# server.py

from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)

# --------------------------
# Global Data Structures
# --------------------------

connected_users = set()  # Set of usernames
rooms = {}  # {room_id: set(usernames)}
room_id_counter = 1
messages = []  # List of messages: {'id': int, 'sender': str, 'recipient': str, 'message': str}
message_id = 1
data_lock = Lock()

# --------------------------
# Helper Functions
# --------------------------

def get_new_messages(username, last_id):
    user_rooms = {room_id for room_id, participants in rooms.items() if username in participants}
    new_msgs = [msg for msg in messages if msg['id'] > last_id and 
                (msg['recipient'] == username or msg['recipient'] in user_rooms)]
    return new_msgs

# --------------------------
# Routes
# --------------------------

@app.route('/register', methods=['POST'])
def register():
    global connected_users
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'status': 'fail', 'message': 'Username is required.'}), 400

    with data_lock:
        if username in connected_users:
            return jsonify({'status': 'fail', 'message': 'Username already taken.'}), 400
        connected_users.add(username)
    
    return jsonify({'status': 'success', 'message': f'User {username} registered successfully.'}), 200

@app.route('/send', methods=['POST'])
def send():
    global messages, message_id
    data = request.get_json()
    sender = data.get('sender')
    recipient = data.get('recipient')  # Can be a username or room_id (as string)
    message = data.get('message')

    if not sender or not recipient or not message:
        return jsonify({'status': 'fail', 'message': 'Sender, recipient, and message are required.'}), 400

    with data_lock:
        if sender not in connected_users:
            return jsonify({'status': 'fail', 'message': 'Sender not registered.'}), 400

        # If recipient is a room
        if recipient.startswith('room_'):
            if recipient not in rooms:
                return jsonify({'status': 'fail', 'message': 'Room does not exist.'}), 400
            if sender not in rooms[recipient]:
                return jsonify({'status': 'fail', 'message': 'You are not a participant of this room.'}), 400
        else:
            # Direct message: check if recipient is online
            if recipient not in connected_users:
                return jsonify({'status': 'fail', 'message': 'Recipient not online.'}), 400

        # Add message to the list
        msg = {
            'id': message_id,
            'sender': sender,
            'recipient': recipient,
            'message': message
        }
        messages.append(msg)
        message_id += 1

    return jsonify({'status': 'success', 'message': 'Message sent successfully.'}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    username = request.args.get('username')
    last_id = request.args.get('last_id', default=0, type=int)

    if not username:
        return jsonify({'status': 'fail', 'message': 'Username is required.'}), 400

    with data_lock:
        if username not in connected_users:
            return jsonify({'status': 'fail', 'message': 'User not registered.'}), 400
        new_msgs = get_new_messages(username, last_id)

    return jsonify({'status': 'success', 'messages': new_msgs}), 200

@app.route('/create_room', methods=['POST'])
def create_room():
    global room_id_counter, message_id
    data = request.get_json()
    admin = data.get('admin')
    participants = data.get('participants')  # List of usernames

    if not admin or not participants:
        return jsonify({'status': 'fail', 'message': 'Admin and participants are required.'}), 400

    with data_lock:
        if admin not in connected_users:
            return jsonify({'status': 'fail', 'message': 'Admin is not registered.'}), 400
        for user in participants:
            if user not in connected_users:
                return jsonify({'status': 'fail', 'message': f'User {user} is not online.'}), 400

        # Include admin in the participants to ensure they're part of the room
        full_participants = set(participants)
        full_participants.add(admin)

        room_id = f'room_{room_id_counter}'
        room_id_counter += 1
        rooms[room_id] = full_participants

        # Notify participants about room creation
        for user in rooms[room_id]:
            msg = {
                'id': message_id,
                'sender': 'server',
                'recipient': user,
                'message': f'Room {room_id.split("_")[1]} has been created and you have been added as a participant.'
            }
            messages.append(msg)
            message_id += 1

    return jsonify({'status': 'success', 'message': f'Room {room_id} created successfully.', 'room_id': room_id}), 200

@app.route('/online', methods=['GET'])
def online_users_route():
    with data_lock:
        users = list(connected_users)
    return jsonify({'status': 'success', 'online_users': users}), 200

@app.route('/leave_room', methods=['POST'])
def leave_room():
    data = request.get_json()
    username = data.get('username')
    room_id = data.get('room_id')

    if not username or not room_id:
        return jsonify({'status': 'fail', 'message': 'Username and room_id are required.'}), 400

    with data_lock:
        if room_id not in rooms:
            return jsonify({'status': 'fail', 'message': 'Room does not exist.'}), 400
        if username not in rooms[room_id]:
            return jsonify({'status': 'fail', 'message': 'You are not a participant of this room.'}), 400

        rooms[room_id].remove(username)
        if len(rooms[room_id]) == 0:
            del rooms[room_id]
        else:
            # Notify remaining participants
            for user in rooms[room_id]:
                msg = {
                    'id': message_id,
                    'sender': 'server',
                    'recipient': user,
                    'message': f'{username} has left room {room_id.split("_")[1]}.'
                }
                messages.append(msg)
                message_id += 1

    return jsonify({'status': 'success', 'message': f'You have left room {room_id}.'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'status': 'fail', 'message': 'Username is required.'}), 400
    with data_lock:
        if username in connected_users:
            connected_users.remove(username)
            # Remove user from all rooms
            for room_id, participants in list(rooms.items()):
                if username in participants:
                    participants.remove(username)
                    if len(participants) == 0:
                        del rooms[room_id]
                    else:
                        # Notify remaining participants
                        msg = {
                            'id': message_id,
                            'sender': 'server',
                            'recipient': user,
                            'message': f'{username} has left room {room_id.split("_")[1]}.'
                        }
                        for user in participants:
                            messages.append(msg.copy())  # Create a separate message for each user
                            message_id += 1
            return jsonify({'status': 'success', 'message': f'User {username} logged out successfully.'}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'Username not found.'}), 400

@app.route('/announcement', methods=['GET'])
def get_announcement():
    try:
        with open('announcement.txt', 'r') as f:
            announcement = f.read().strip()
        return jsonify({'status': 'success', 'announcement': announcement}), 200
    except Exception as e:
        return jsonify({'status': 'fail', 'message': 'Failed to read announcement.'}), 500

# --------------------------
# Run Server
# --------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
