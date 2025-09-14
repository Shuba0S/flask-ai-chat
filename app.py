import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, User, Conversation, Message
from forms import SignupForm, LoginForm, MessageForm
from datetime import datetime
import openai
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///chatbot.db'
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Flask setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')

# DB setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Minimal User class for Flask-Login that fetches from DB
class FlaskUser(UserMixin):
    def __init__(self, user):
        self.id = str(user.id)
        self.email = user.email

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    user = db.query(User).filter_by(id=int(user_id)).first()
    db.close()
    if user:
        return FlaskUser(user)
    return None

# Helper: get SQLAlchemy user record
def get_user_record(user_id):
    db = SessionLocal()
    user = db.query(User).filter_by(id=int(user_id)).first()
    db.close()
    return user

# Home
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        db = SessionLocal()
        existing = db.query(User).filter_by(email=form.email.data.lower()).first()
        if existing:
            flash('Email already registered', 'danger')
            db.close()
            return render_template('signup.html', form=form)
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        flash('Account created. Please sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = SessionLocal()
        user = db.query(User).filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            flask_user = FlaskUser(user)
            login_user(flask_user)
            flash('Logged in successfully', 'success')
            db.close()
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        db.close()
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

# Dashboard - list conversations
@app.route('/dashboard')
@login_required
def dashboard():
    db = SessionLocal()
    user = db.query(User).filter_by(id=int(current_user.id)).first()
    conversations = db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.created_at.desc()).all()
    db.close()
    return render_template('dashboard.html', conversations=conversations)

# Start new conversation page
@app.route('/conversations/new', methods=['GET', 'POST'])
@login_required
def new_conversation():
    db = SessionLocal()
    user = db.query(User).filter_by(id=int(current_user.id)).first()
    # Enforce max 3 conversations
    existing_convs = db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.created_at.asc()).all()
    if len(existing_convs) >= 3:
        oldest = existing_convs[0]
    # ✅ Delete messages related to the oldest conversation first
        db.query(Message).filter_by(conversation_id=oldest.id).delete()
        db.delete(oldest)
        db.commit()

    conv = Conversation(user_id=user.id, title=f'Conversation {datetime.utcnow().isoformat()}')
    db.add(conv)
    db.commit()
    db.refresh(conv)
    conv_id = conv.id
    db.close()
    return redirect(url_for('chat', conv_id=conv_id))

# Chat view + send message
@app.route('/chat/<int:conv_id>', methods=['GET', 'POST'])
@login_required
def chat(conv_id):
    form = MessageForm()
    db = SessionLocal()
    conv = db.query(Conversation).filter_by(id=conv_id, user_id=int(current_user.id)).first()
    if not conv:
        db.close()
        flash('Conversation not found', 'danger')
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        # Save user message
        user_msg = Message(conversation_id=conv.id, role='user', content=form.content.data)
        db.add(user_msg)
        db.commit()

        # Prepare messages for AI
        msgs = db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
        prompt_messages = []
        for m in msgs:
            prompt_messages.append({
                'role': m.role,
                'content': m.content
            })

        # Select API key: per-user if provided else global
        user_record = db.query(User).filter_by(id=int(current_user.id)).first()
        api_key = user_record.api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            # No API key set - show error
            assistant_msg = Message(
                conversation_id=conv.id,
                role='assistant',
                content='AI API key not configured. Please ask admin to set OPENAI_API_KEY or add your API key to your profile.'
            )
            db.add(assistant_msg)
            db.commit()
            db.close()
            flash('AI service not available.', 'danger')
            return redirect(url_for('chat', conv_id=conv_id))

        # Call OpenAI
        try:
            openai.api_key = api_key
            completion = openai.ChatCompletion.create(
                model='gpt-4o-mini',  # keep as you set
                messages=prompt_messages,
                max_tokens=500,
            )
            ai_text = completion.choices[0].message.content.strip()
        except Exception as e:
            ai_text = f"AI call failed: {str(e)}"

        assistant_msg = Message(conversation_id=conv.id, role='assistant', content=ai_text)
        db.add(assistant_msg)
        db.commit()
        db.close()
        return redirect(url_for('chat', conv_id=conv_id))

    # ✅ GET: show messages
    messages = db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.created_at.asc()).all()
    db.close()
    return render_template("chat.html", form=form, conversation=conv, messages=messages)


if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host="127.0.0.1", port=8000, debug=True)