from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    total_queries = db.Column(db.Integer, default=0)
    preferences = db.Column(db.JSON, nullable=True)  # Store user preferences
    queries = db.relationship('Query', backref='user', lazy=True, cascade='all, delete-orphan')

class Query(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    sentiment = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)
    response_time = db.Column(db.Float)  # Time taken to respond in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Boolean, nullable=True)
    feedback_text = db.Column(db.Text, nullable=True)  # User comments on feedback
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    id = db.Column(db.Integer, primary_key=True)
    intent = db.Column(db.String(50), nullable=False)
    question_pattern = db.Column(db.String(200), nullable=False)
    response = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(200))
    frequency = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)  # How often this answer helps
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CollegeInfo(db.Model):
    __tablename__ = 'college_info'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    additional_info = db.Column(db.JSON, nullable=True)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('queries.id'))
    rating = db.Column(db.Integer)  # 1-5 rating
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)