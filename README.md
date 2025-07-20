# ChatRoom - Real-time Chat Backend

A lightweight Flask-based backend for real-time chat applications with support for direct messaging and group rooms.

## Features

- **Real-time Messaging**: Instant message delivery between users
- **Room Management**: Create and join chat rooms with multiple participants
- **Direct Messaging**: Private conversations between two users
- **User Management**: Register, login, and logout functionality
- **Server Announcements**: Broadcast messages to all users
- **RESTful API**: Clean HTTP endpoints for easy frontend integration

## Quick Start

### Prerequisites

- Python 3.8+
- Flask

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

The server will start on `http://localhost:5003`

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

## How It Works

### Architecture

- **Flask Server**: Lightweight web framework for building APIs
- **In-Memory Storage**: User sessions, rooms, and messages stored in memory
- **Thread-Safe Operations**: Lock-based synchronization for concurrent access
- **Polling-Based Updates**: Clients poll for new messages periodically

### Data Structures

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

## File Structure

```
chatroom/
├── chatserve.py        # Main Flask server
├── announcement.txt    # Server announcement file
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Example Frontend Integration

### JavaScript Example

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

### Python Client Example

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

## Configuration

### Server Settings

- **Host**: `0.0.0.0` (accessible from any IP)
- **Port**: `5003` (configurable in `chatserve.py`)
- **Debug Mode**: Enabled by default

### Customization

- **Message Persistence**: Add database integration for message history
- **Authentication**: Implement user authentication and session management
- **WebSocket Support**: Replace polling with WebSocket for real-time updates
- **Rate Limiting**: Add request rate limiting to prevent spam

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `chatserve.py` or kill existing process
2. **CORS errors**: Add CORS middleware for web frontend integration
3. **Memory usage**: Consider database storage for large-scale deployments

### Performance Tips

- Use connection pooling for database integration
- Implement message pagination for large chat histories
- Add message compression for high-traffic scenarios

## Deployment

### Development
```bash
python chatserve.py
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Database integration for message persistence
- [ ] User authentication and authorization
- [ ] File sharing capabilities
- [ ] Message encryption
- [ ] Push notifications
- [ ] Message reactions and emojis 