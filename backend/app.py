from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import hashlib
import os
from sqlalchemy import text

from models import db, User, Query, KnowledgeBase
from chatbot import CollegeChatbot

app = Flask(__name__)
CORS(app)

# Absolute path
basedir = os.path.abspath(os.path.dirname(__file__))

# Config
app.config['SECRET_KEY'] = 'college-chatbot-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'college_chatbot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure DB folder exists
database_dir = os.path.join(basedir, 'database')
os.makedirs(database_dir, exist_ok=True)
print(f"Database directory ready at: {database_dir}")

# Init DB
db.init_app(app)

# Init chatbot
chatbot = CollegeChatbot()

# -------------------- ROOT ROUTE (FIX) --------------------
@app.route('/')
def home():
    return "College Chatbot Backend is Running 🚀"


# -------------------- SESSION USER --------------------
def get_or_create_user():
    user_id = session.get('user_id')
    if not user_id:
        session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10]
        anonymous_user = User(
            username=f'guest_{session_id}',
            email=f'guest_{session_id}@temp.com'
        )
        db.session.add(anonymous_user)
        db.session.commit()
        session['user_id'] = anonymous_user.id
        return anonymous_user.id
    return user_id


# -------------------- CHAT API --------------------
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        user_id = get_or_create_user()
        result = chatbot.get_response(user_message, user_id)

        # Save to DB
        new_query = Query(
            user_id=user_id,
            question=user_message,
            answer=result['response'],
            intent=result['intent'],
            confidence=result['confidence']
        )
        db.session.add(new_query)
        db.session.commit()

        return jsonify({
            'response': result['response'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'sentiment': result.get('sentiment'),
            'entities': result.get('entities'),
            'query_id': new_query.id
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


# -------------------- HISTORY API --------------------
@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify([])

        queries = Query.query.filter_by(user_id=user_id)\
            .order_by(Query.timestamp.desc())\
            .limit(20).all()

        history = [{
            'id': q.id,
            'question': q.question,
            'answer': q.answer,
            'timestamp': q.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for q in queries]

        return jsonify(history)

    except Exception as e:
        print(f"Error in history endpoint: {e}")
        return jsonify({'error': str(e)}), 500


# -------------------- HEALTH CHECK --------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'database_path': app.config['SQLALCHEMY_DATABASE_URI']
    })


# -------------------- CREATE TABLES --------------------
with app.app_context():
    try:
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"ERROR during database initialization: {e}")


# -------------------- RUN --------------------
if __name__ == '__main__':
    print("=" * 50)
    print("Starting College Enquiry Chatbot Backend")
    print("=" * 50)
    print(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)