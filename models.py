from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'admin'

    attempts = db.relationship('ExamAttempt', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(100), nullable=False)       # Subnetting, Routing, VLANs, etc.
    difficulty = db.Column(db.String(20), nullable=False)   # 'easy', 'medium', 'hard'

    options = db.relationship('Option', backref='question', cascade='all, delete-orphan', lazy=True)


class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)


class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    submit_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)                  # Percentage score (0 - 100)
    total_questions = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='in_progress')    # 'in_progress' or 'completed'

    answers = db.relationship('AttemptAnswer', backref='attempt', cascade='all, delete-orphan', lazy=True)


class AttemptAnswer(db.Model):
    """
    Persists the unique question order and scrambled choices
    assigned specifically to this student attempt.
    """
    __tablename__ = 'attempt_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    question_order = db.Column(db.Integer, nullable=False)
    shuffled_option_ids = db.Column(db.String(100), nullable=False)  # e.g., "4,1,3,2"
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)

    question = db.relationship('Question')
    selected_option = db.relationship('Option')