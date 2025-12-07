# ChatApp Backend

Django REST API backend for the ChatApp application with WebSocket support for real-time chat.

## Tech Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **Django Channels** - WebSocket support
- **Daphne** - ASGI server
- **SQLite** - Database (default, can use PostgreSQL)
- **python-dotenv** - Environment variable management

## Project Structure

```
backend/
├── chatapp/              # Main Django project
│   ├── settings.py       # Project settings (uses .env)
│   ├── urls.py           # Main URL routing
│   ├── asgi.py           # ASGI config for WebSocket
│   └── wsgi.py           # WSGI config
├── users/                # User authentication app
│   ├── models.py         # User model
│   ├── views.py          # Auth API endpoints
│   ├── serializers.py    # DRF serializers
│   └── urls.py           # User routes
├── posts/                # Posts/Feed app
│   ├── models.py         # Post, PollOption, Like, Comment
│   ├── views.py          # Post API endpoints
│   ├── serializers.py    # Post serializers
│   └── urls.py           # Post routes
├── chat/                 # Real-time chat app
│   ├── models.py         # Conversation, Message models
│   ├── views.py          # Chat API endpoints
│   ├── consumers.py      # WebSocket consumer
│   ├── routing.py        # WebSocket URL routing
│   └── urls.py           # Chat routes
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (insecure default) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | Frontend URLs | `http://localhost:3000` |
| `RECAPTCHA_SITE_KEY` | Google reCAPTCHA v2 site key | (disabled) |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA v2 secret key | (disabled) |

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication (`/api/users/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/generate/` | Generate anonymous user | No |
| POST | `/login/` | Login with username/password | No |
| POST | `/signup/` | Signup with CAPTCHA verification | No |
| GET | `/recaptcha-key/` | Get reCAPTCHA site key | No |
| POST | `/logout/` | Logout user | Yes |
| GET | `/profile/` | Get current user profile | Yes |
| PUT | `/profile/update/` | Update profile | Yes |
| POST | `/change-password/` | Change password | Yes |
| GET | `/check-auth/` | Check authentication status | No |
| GET | `/search/?q=query` | Search users | Yes |

### Posts (`/api/posts/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all posts | No |
| POST | `/create/` | Create new post | Yes |
| GET | `/<id>/` | Get single post | No |
| DELETE | `/<id>/delete/` | Delete post | Yes (owner) |
| POST | `/<id>/like/` | Toggle like on post | Yes |
| GET/POST | `/<id>/comments/` | Get/Add comments | Yes |
| POST | `/<id>/vote/` | Vote on poll | Yes |
| GET | `/my-posts/` | Get current user's posts | Yes |

### Chat (`/api/chat/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/conversations/` | List conversations | Yes |
| POST | `/conversations/start/` | Start new conversation | Yes |
| GET | `/conversations/<id>/` | Get conversation details | Yes |
| GET | `/conversations/<id>/messages/` | Get messages | Yes |
| POST | `/conversations/<id>/messages/send/` | Send message | Yes |

### WebSocket

```
ws://localhost:8000/ws/chat/<conversation_id>/
```

**Message Format (Send):**
```json
{
  "message": "Hello!",
  "sender_id": 1
}
```

**Message Format (Receive):**
```json
{
  "message": {
    "id": 1,
    "content": "Hello!",
    "sender": { "id": 1, "username": "user1" },
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

## Models

### User
- `username` - Unique identifier
- `display_name` - Display name
- `user_type` - `anonymous` or `registered`
- `mobile_number` - Phone number (registered users)
- `avatar` - Profile image
- `bio` - User bio
- `is_online` - Online status

### Post
- `author` - User who created the post
- `post_type` - `text`, `image`, `video`, or `poll`
- `content` - Text content
- `image` - Image file
- `video` - Video file (max 10s)
- `created_at` - Timestamp

### Conversation
- `participants` - Users in conversation
- `created_at` - Timestamp
- `updated_at` - Last activity

### Message
- `conversation` - Parent conversation
- `sender` - User who sent message
- `content` - Message text
- `is_read` - Read status

## Production Deployment

### 1. Update Environment Variables

```bash
SECRET_KEY=your-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Use PostgreSQL

Update `DATABASE_URL` in `.env` to use PostgreSQL.

### 3. Use Redis for Channel Layer

```python
# In settings.py, update CHANNEL_LAYERS for production:
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.getenv('REDIS_URL', 'redis://localhost:6379/0')],
        },
    }
}
```

### 4. Collect Static Files

```bash
python manage.py collectstatic
```

### 5. Run with Daphne

```bash
daphne -b 0.0.0.0 -p 8000 chatapp.asgi:application
```

## Admin Panel

Access Django admin at `http://localhost:8000/admin/`

Default models registered:
- Users
- OTP Verifications
- Posts
- Poll Options
- Likes
- Comments
- Conversations
- Messages

## License

MIT
