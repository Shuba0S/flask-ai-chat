# 🧠 AI Chatbot System

## 📖 Introduction
This project is an **AI Chatbot System** built with **Flask** and **OpenAI's API**. It allows users to sign up, log in, and interact with an AI assistant through a conversation interface. Each user is allowed a maximum of **3 conversations** — older ones are deleted automatically to maintain this limit.

The frontend is rendered using **Jinja templating**, and the backend logic is handled in Python.

> ⚠️ **Note**: This project is currently for **local development/testing only**. It is **not yet deployment-ready**.

---

## 🎯 Features

- ✅ User registration and login with secure password handling.
- ✅ Authenticated users can create and manage conversations.
- ✅ Each user can have a maximum of **3 conversations** — the **oldest** is deleted automatically when a new one is created.
- ✅ Conversations stored in a local **SQLite** database.
- ✅ Each conversation supports interactive chat with **OpenAI** via the GPT model.
- ✅ Messages stored with roles: `user` and `assistant`.

---

## 🧩 File Structure

```
📁 your-project/
├── app.py               # Main Flask application
├── models.py            # SQLAlchemy ORM models
├── forms.py             # Flask-WTF forms
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base layout
│   ├── chat.html        # Chat interface
│   ├── dashboard.html   # User's conversation list
│   ├── login.html       # Login form
│   ├── signup.html      # Signup form
├── .env                 # Environment variables (OPENAI key, DB URL, etc.)
├── requirements.txt     # Python package requirements
```

---

## 🛠️ Tech Stack

- **Flask** – Lightweight Python web framework
- **Flask-Login** – User session and authentication
- **Flask-WTF** – Secure form handling with validation
- **SQLAlchemy** – ORM for database interactions
- **OpenAI API** – AI assistant using GPT-4o-mini
- **Jinja2** – Templating engine for frontend rendering
- **SQLite** – Local database (via SQLAlchemy)
- **python-dotenv** – Environment variable management

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Shuba0S/flask-ai-chat.git
cd flask-ai-chat
```

### 2. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```
### 5. Initialize the database

```bash
python
>>> from models import Base
>>> from app import engine
>>> Base.metadata.create_all(engine)
>>> exit()
```
### 6. Run the Flask app

```bash
python app.py
```

### 7. Open in your browser

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## ⚙️ Known Limitations

- 🧪 This project is for **local development/testing only**.
- 🚫 Not deployment-ready (no Docker, CI/CD, or cloud configuration).
- 🧼 Basic input validation only; more robust sanitization should be added for production.
- 💾 Uses **SQLite**, which is not suitable for production-scale applications.
- 🧠 No support for handling simultaneous user sessions with high concurrency.
- 🔐 No password reset or email verification features included.

---

## 🔮 Future Improvements

- 🌐 Add deployment scripts for platforms like **Docker**, **Heroku**, or **Render**.
- 🔐 Implement password reset, email verification, and 2FA.
- 📧 Add email or SMS notifications on AI message delivery or activity.
- 📈 Add analytics for conversation usage and user behavior.
- 🧹 Improve the UI/UX of the dashboard and chat interface.
- 💾 Add support for PostgreSQL or MySQL for production use.
- 👥 Add support for admin dashboard to view user activity.
- 🧠 Integrate memory and context tracking across sessions.

---

## 👤 Author

**Shuba S**  
📧 Email: shuba9902@gmail.com  
💼 [LinkedIn](https://www.linkedin.com/in/shuba-s01/)  
🐙 [GitHub](https://github.com/Shuba0S/)

---

## 📄 License

Released under the **MIT License**. See [LICENSE](LICENSE) for details.
