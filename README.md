# 🧠 Quizly - Backend API

**Quizly** is a Django REST API that lets authenticated users generate and manage quizzes from **YouTube videos**.  
It downloads a video’s audio (via **yt-dlp + FFmpeg**), transcribes it locally with **OpenAI Whisper**, and then uses **Google Gemini (Flash)** to generate a quiz with **10 multiple-choice questions**.

This backend is designed to be consumed by a separate frontend (not included in this repository).

---

## 🚀 Features

- 🔐 **Authentication (JWT + HTTP-only Cookies)**
  - Registration
  - Login (sets `access_token` + `refresh_token` cookies)
  - Token refresh (cookie-based)
  - Logout (clears cookies + blacklists refresh token)
- 📹 **YouTube Quiz Generation**
  - Input: YouTube URL
  - Pipeline: yt-dlp → FFmpeg → Whisper → Gemini → DB
- 📝 **Quiz Management**
  - List your quizzes
  - Retrieve quiz detail
  - Update title/description
  - Delete quiz (cascade deletes questions)
- 👥 **User isolation**
  - Users can only access their own quizzes
- 🛠️ **Admin Interface**
  - Manage quizzes + inline questions
- 🧪 **Testing + Coverage**
  - pytest + coverage
  - target: **≥ 95% coverage**

---

## 🧠 Tech Stack

| Layer | Technology |
|------|-----------|
| Backend | Django |
| API | Django REST Framework |
| Auth | SimpleJWT (JWT in HTTP-only cookies) |
| AI | Google Gemini Flash (`gemini-2.5-flash`) |
| Transcription | OpenAI Whisper (local) |
| YouTube download | yt-dlp + FFmpeg |
| Database | SQLite (dev) |
| Testing | pytest, pytest-django, coverage |

---

## 📦 Requirements

- **Python 3.11+** (recommended)
- **pip**
- **Git**
- (Optional) virtual environment (`venv`)
- ✅ **FFmpeg installed globally** (required for yt-dlp postprocessing + Whisper workflows)

---

## ⚠️ FFmpeg (Global Required)

This project extracts audio from YouTube videos and converts it to `.mp3`.  
That conversion uses FFmpeg under the hood. If FFmpeg is missing, quiz creation will fail.

Verify it’s installed:

```bash
ffmpeg -version
```

### Install FFmpeg (examples)

#### macOS (Homebrew)
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows (Install via Chocolatey)
```bash
choco install ffmpeg
```
-> Or download a build and ensure ffmpeg is on your PATH.

---

## 🛠️ Setup (Development)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/SimonHeistermann/Quizly.git
cd Quizly
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
python3 -m venv venv
```

#### macOS / Linux
```bash
source venv/bin/activate
```

or

#### Windows (Command Prompt)
```bash
venv\Scripts\activate 
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Setup

#### macOS / Linux
```bash
cp env-template .env
```

or

#### Windows (Command Prompt)
```bash
copy env-template .env
```

🔐 Tip: Never commit your .env file to Git.
You can safely use the default values for local development.
Optionally, replace SECRET_KEY or toggle DEBUG.

### 5️⃣ 🔑 Generate your own SECRET_KEY
Django requires a secret key for cryptographic signing.
You must generate one manually and add it to your .env file.

Option 1 (recommended):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the generated key into your .env file:
```bash
SECRET_KEY='your-secret-key-here'
```

Option 2:
If Django isn’t installed yet, use an online generator such as
👉 https://djecrety.ir/

and paste the result into your .env.

### 6️⃣ 🤖 Get a Gemini API Key

You need a Google Gemini API key to generate quiz questions.

High-level steps:

1. Go to Google AI Studio

2. Create / select a project

3. Generate an API key

4. Put the key into your .env

In .env:
```bash
GEMINI_API_KEY=your-api-key-here
```

✅ Do you need quotes around the Gemini key?
Usually no. It’s typically URL-safe and contains no spaces.
If your key ever contains special characters (rare), quotes are still safe:
```bash
GEMINI_API_KEY="your_key_here"
```

### 7️⃣ 🧠 Whisper Model “turbo” explained
Whisper has multiple model sizes/speeds.
turbo is commonly used as a fast transcription model choice.

In this project you can configure it via:
```bash
WHISPER_MODEL=turbo
```

If you want better quality (usually slower), you could use e.g.:

- base
- small
- medium
- large

(Only do this if your system can handle it.)

### 8️⃣ Run Migrations
```bash
python manage.py migrate
```

### 9️⃣ Create a Superuser
```bash
python manage.py createsuperuser
```

### 🔟 Run the Development Server
```bash
python manage.py runserver
```

--> Open in browser:
➡️ http://127.0.0.1:8000/

---

## 📌 API Endpoints

Base prefix:

- /api/

### 🔐 Authentication

#### Register:
- POST /api/register/

#### Login (sets HTTP-only cookies):
- POST /api/login/

Response example:
```bash
{
  "detail": "Login successfully!",
  "user": { "id": 1, "username": "olivia", "email": "olivia@example.com" }
}
```

#### Cookies set:

- access_token
- refresh_token

#### Refresh Access Token (cookie-based):
- POST /api/token/refresh/

#### Logout (clears cookies + blacklists refresh token):
- POST /api/logout/

---

## Quiz Management

### Create Quiz from YouTube URL:
- Create Quiz from YouTube URL

#### Body:
```bash
{ "url": "https://www.youtube.com/watch?v=example" }
```

### List My Quizzes:
- GET /api/quizzes/

### Quiz Detail:
- GET /api/quizzes/<id>/

### Update Quiz (only title/description):
- PATCH /api/quizzes/<id>/

#### Body example:
```bash
{ "title": "Updated title" }
```

### Delete Quiz:
- DELETE /api/quizzes/<id>/

#### Retuns: 
- 204 No Content

---

## 🌐 Hosting / Production Setup

If you plan to host your project (e.g. on Render, Railway, or your own VPS/server):

### 🔧 Update your .env file

DEBUG=False
SECRET_KEY=<your-production-secret>
SECURE_COOKIES=True
ALLOWED_HOSTS=quizly.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
CORS_ALLOWED_ORIGINS=https://quizly.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://quizly.yourdomain.com

### 📦 Collect static files
```bash
python manage.py collectstatic
```

### ⚙️ Configure Gunicorn + Reverse Proxy (e.g. Nginx)

Set up Gunicorn as your WSGI server and use Nginx to serve static files and handle HTTPS requests.

Example (conceptually):

Gunicorn listens on 127.0.0.1:8000

Nginx listens on port 80/443 and proxies requests to Gunicorn

### 🔒 SSL Certificates

Use Let’s Encrypt (via Certbot) to enable HTTPS.

### 🧰 Debugging Tips

Remember:
👉 Django only loads .env values when the server starts, so after editing your .env, restart it:
```bash
python manage.py runserver
```

### 📁 Project Structure (simplified)
```bash
Quizly/
│
├── apps/                                # Domain-driven Django apps (feature-based structure)
│   │
│   ├── user_auth_app/                  # User authentication & authorization domain
│   │   │                                 # (e.g. registration, login, JWT, cookies, permissions)
│   │   │
│   │   ├── api/                        # REST API layer (Django REST Framework)
│   │   │   ├── serializers.py          # DRF serializers (validation, transformation, I/O schemas)
│   │   │   ├── views.py                # API views / viewsets (endpoint logic)
│   │   │   ├── urls.py                 # App-specific API routes
│   │   │   ├── permissions.py          # Custom permission classes (if applicable)
│   │   │   └── ...                     # Optional: filters.py, pagination.py, schemas.py, etc.
│   │   │
│   │   ├── tests/                      # Automated tests for this app
│   │   │   ├── test_api.py             # API tests (auth flows, status codes, responses)
│   │   │   ├── test_services.py        # Business-logic tests (if using a service layer)
│   │   │   └── ...                     # Optional: factories/, fixtures/, mocks/
│   │   │
│   │   ├── utils.py                    # Reusable helper functions
│   │   │                                 # (e.g. JWT cookie helpers, token utilities)
│   │   ├── models.py                  # Database models (User, Profile, etc. if applicable)
│   │   ├── apps.py                    # Django AppConfig
│   │   └── __init__.py
│   │
│   └── quiz_management_app/            # Quiz / domain-specific business logic
│       │                                 # (quizzes, questions, answers, scoring, etc.)
│       │
│       ├── api/                        # REST API layer for quiz management
│       │   ├── serializers.py          # Quiz-related serializers
│       │   ├── views.py                # Quiz endpoints (CRUD, participation, results)
│       │   ├── urls.py                 # Quiz API routes
│       │   └── ...                     # Optional API helpers
│       │
│       ├── tests/                      # Tests for quiz functionality
│       │   ├── test_models.py          # Model tests (relations, constraints)
│       │   ├── test_api.py             # API tests (quiz flows, permissions)
│       │   └── ...
│       │
│       ├── models.py                  # Quiz-related database models
│       ├── admin.py                   # Django admin configuration
│       ├── utils.py                   # Quiz-specific helper functions
│       ├── apps.py                    # Django AppConfig
│       └── __init__.py
│
├── core/                               # Django project configuration (global layer)
│   │
│   ├── settings.py                    # Global settings (apps, middleware, DB, auth, DRF config)
│   ├── urls.py                        # Root URL configuration (includes app-level URLs)
│   ├── wsgi.py                        # WSGI entry point (used for deployment)
│   └── asgi.py                        # ASGI entry point (if async / websockets are used)
│
├── env-template                       # Environment variable template (.env example)
│                                     # Used to document required environment variables
│
├── requirements.txt                  # Python dependencies (pinned versions recommended)
│
└── manage.py                         # Django management entry point
```

---

## 🧪 Testing

Run all tests:
```bash
pytest
``` 

Run with coverage (recommended):
```bash
coverage run -m pytest
coverage report -m --include="apps/*" --omit="*/migrations/*,*/tests/*"
```

(Optional) HTML coverage report:
```bash
coverage html
open htmlcov/index.html
```
✅ Coverage target: ≥ 95%

---

### 🧩 License

MIT License © 2025 Simon Heistermann