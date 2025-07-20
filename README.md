# ChatRoom - Complete Chat Application

A complete real-time chat application with a Flask backend API and a Tkinter frontend client, supporting direct messaging and group rooms.

## Features

- **Real-time Messaging**: Instant message delivery between users
- **Room Management**: Create and join chat rooms with multiple participants
- **Direct Messaging**: Private conversations between two users
- **User Management**: Register, login, and logout functionality
- **Server Announcements**: Broadcast messages to all users
- **RESTful API**: Clean HTTP endpoints for easy frontend integration
- **Tkinter Frontend**: Desktop application with modern GUI
- **Online User List**: Real-time display of connected users
- **Chat History**: Persistent message storage and retrieval

## Quick Start

### Prerequisites

- Python 3.8+
- Flask
- Tkinter (usually included with Python)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd chatroom
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python chatserve.py
   ```

4. **Run the client:**
   ```bash
   python frontend.py
   ```

The server will start on `http://localhost:5003` and the client will open as a desktop application.

## System Architecture

### Backend (chatserve.py)
- **Flask Server**: Lightweight web framework for building APIs
- **In-Memory Storage**: User sessions, rooms, and messages stored in memory
- **Thread-Safe Operations**: Lock-based synchronization for concurrent access
- **Polling-Based Updates**: Clients poll for new messages periodically

### Frontend (frontend.py)
- **Tkinter GUI**: Desktop application with modern interface
- **Real-time Updates**: Automatic message polling and display
- **User Interface**: Online users list, chat rooms, and message history
- **Multi-chat Support**: Switch between different conversations seamlessly

## API Endpoints

### User Management

#### Register User
```http
POST /register
Content-Type: application/json

{
  "username": "john_doe"
}
```

#### Logout User
```http
POST /logout
Content-Type: application/json

{
  "username": "john_doe"
}
```

#### Get Online Users
```http
GET /online
```

### Messaging

#### Send Message
```http
POST /send
Content-Type: application/json

{
  "sender": "john_doe",
  "recipient": "jane_smith",
  "message": "Hello, how are you?"
}
```

#### Get Messages
```http
GET /messages?username=john_doe&last_id=0
```

### Room Management

#### Create Room
```http
POST /create_room
Content-Type: application/json

{
  "admin": "john_doe",
  "participants": ["jane_smith", "bob_wilson"]
}
```

#### Leave Room
```http
POST /leave_room
Content-Type: application/json

{
  "username": "john_doe",
  "room_id": "room_1"
}
```

### System

#### Get Announcement
```http
GET /announcement
```

## Frontend Usage

### Getting Started
1. Run the frontend application
2. Enter your username when prompted
3. The application will connect to the server automatically

### Sending Messages
1. Select a user from the "Online Users" list for direct messages
2. Or select a chat room from the "Chats" list
3. Type your message in the input field
4. Press Enter or click Send

### Creating Group Chats
1. Click "Create Group Chat" button
2. Select participants from the online users list
3. Click "Create" to start the group chat
4. The new room will appear in your chats list

### Switching Between Chats
- Click on any user or room in the chats list to switch conversations
- The chat history will load automatically
- New messages will appear in real-time

## File Structure

```
chatroom/
├── chatserve.py        # Main Flask server
├── frontend.py         # Tkinter desktop client
├── announcement.txt    # Server announcement file
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Data Structures

```python
connected_users = set()  # Active users
rooms = {}              # {room_id: set(usernames)}
messages = []           # List of message objects
```

### Message Format

```python
{
  "id": 1,
  "sender": "username",
  "recipient": "username_or_room_id",
  "message": "message content"
}
```

## Configuration

### Server Settings

- **Host**: `0.0.0.0` (accessible from any IP)
- **Port**: `5003` (configurable in `chatserve.py`)
- **Debug Mode**: Enabled by default

### Frontend Settings

- **Server URL**: Configure in `frontend.py` line 12
- **Polling Interval**: 2 seconds (configurable)
- **GUI Theme**: Standard Tkinter theme

### Customization

- **Message Persistence**: Add database integration for message history
- **Authentication**: Implement user authentication and session management
- **WebSocket Support**: Replace polling with WebSocket for real-time updates
- **Rate Limiting**: Add request rate limiting to prevent spam

## Example Frontend Integration

### JavaScript Client

```javascript
// Register user
const registerUser = async (username) => {
  const response = await fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  });
  return response.json();
};

// Send message
const sendMessage = async (sender, recipient, message) => {
  const response = await fetch('/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sender, recipient, message })
  });
  return response.json();
};

// Poll for new messages
const pollMessages = async (username, lastId) => {
  const response = await fetch(`/messages?username=${username}&last_id=${lastId}`);
  return response.json();
};
```

### Python Client

```python
import requests

# Register
response = requests.post('http://localhost:5003/register', 
                        json={'username': 'test_user'})

# Send message
response = requests.post('http://localhost:5003/send',
                        json={
                            'sender': 'test_user',
                            'recipient': 'room_1',
                            'message': 'Hello room!'
                        })

# Get messages
response = requests.get('http://localhost:5003/messages?username=test_user&last_id=0')
messages = response.json()['messages']
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `chatserve.py` or kill existing process
2. **Frontend connection errors**: Check if server is running and SERVER_URL is correct
3. **Memory usage**: Consider database storage for large-scale deployments
4. **GUI not responding**: Check if server is accessible and firewall settings

### Performance Tips

- Use connection pooling for database integration
- Implement message pagination for large chat histories
- Add message compression for high-traffic scenarios
- Consider WebSocket for better real-time performance

## Deployment

### Development
```bash
# Terminal 1: Server
python chatserve.py

# Terminal 2: Client
python frontend.py
```

### Production
```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5003 chatserve:app

# Using uvicorn (if using ASGI)
pip install uvicorn
uvicorn chatserve:app --host 0.0.0.0 --port 5003
```

### Multi-Client Setup
- Run one server instance
- Multiple clients can connect to the same server
- Each client runs independently

## Security Considerations

### Production Deployment

- **CORS Configuration**: Restrict allowed origins for web clients
- **Rate Limiting**: Implement request rate limiting to prevent spam
- **Authentication**: Add user authentication and session management
- **HTTPS**: Use SSL/TLS encryption for secure communication

### Frontend Security

- **Local Access**: Frontend connects to localhost by default
- **No Sensitive Storage**: No passwords or sensitive data stored locally
- **Input Validation**: Server-side validation of all inputs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Database integration for message persistence
- [ ] User authentication and authorization
- [ ] File sharing capabilities
- [ ] Message encryption
- [ ] Push notifications
- [ ] Message reactions and emojis
- [ ] Voice and video chat
- [ ] Message search functionality
- [ ] User profiles and avatars 