import os
import uuid
import time
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ── app factory ─────────────────────────────────────────────────────────────
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'college-chatbot-secret-key-2025')

# ── database config ───────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database', 'chatbot.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
# Render gives postgres:// but SQLAlchemy 1.4+ needs postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'http://localhost:5000',
    'http://127.0.0.1:5500',
    'http://127.0.0.1:5000',
    'https://harshbuwade.github.io',       # GitHub Pages
    'https://college-enquiry-chatbot-1-enxg.onrender.com',  # Render
    '*'
])

# ── models (in-app to keep single file) ──────────────────────────────────────
from models import db, User, Query, KnowledgeBase

db.init_app(app)

# ── chatbot ───────────────────────────────────────────────────────────────────
from chatbot import CollegeChatbot
chatbot = CollegeChatbot()

# ── DB init ────────────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        # Seed knowledge base if empty
        if KnowledgeBase.query.count() == 0:
            seeds = [
                KnowledgeBase(intent='greeting',          question_pattern='hello hi hey',
                              response='Welcome!',         keywords='hi,hello,hey'),
                KnowledgeBase(intent='admission_process', question_pattern='how to apply admission',
                              response='Fill online form', keywords='admission,apply'),
                KnowledgeBase(intent='courses_offered',   question_pattern='courses programs degrees',
                              response='BCA MCA MBA',      keywords='courses,programs'),
                KnowledgeBase(intent='fees_structure',    question_pattern='fee cost charges',
                              response='BCA 60k/yr',       keywords='fees,cost'),
                KnowledgeBase(intent='placement_records', question_pattern='placement job recruitment',
                              response='92% placed',       keywords='placement,job'),
                KnowledgeBase(intent='hostel_facilities', question_pattern='hostel accommodation room',
                              response='500 capacity',     keywords='hostel,room'),
                KnowledgeBase(intent='library_facilities',question_pattern='library books journals',
                              response='75000+ books',     keywords='library,books'),
                KnowledgeBase(intent='contact_info',      question_pattern='contact phone email address',
                              response='+91 98765 43210',  keywords='contact,phone'),
                KnowledgeBase(intent='scholarship',       question_pattern='scholarship financial aid',
                              response='Up to 50%',        keywords='scholarship,aid'),
            ]
            db.session.bulk_save_objects(seeds)
            db.session.commit()
            print('✅ Knowledge base seeded.')

# ── helpers ────────────────────────────────────────────────────────────────────
def get_or_create_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

# ── routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the frontend HTML."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })


@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        user_count  = User.query.count()
        query_count = Query.query.count()
        kb_count    = KnowledgeBase.query.count()
        return jsonify({
            'status': 'ok',
            'users': user_count,
            'queries': query_count,
            'knowledge_base': kb_count,
            'db_url': app.config['SQLALCHEMY_DATABASE_URI'][:50] + '...'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    t0 = time.time()
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    session_id = get_or_create_session()

    try:
        result = chatbot.get_response(message)

        # Persist query
        q = Query(
            session_id   = session_id,
            question     = message,
            answer       = result['response'],
            intent       = result.get('intent', 'unknown'),
            confidence   = result.get('confidence', 0.0),
            sentiment    = result.get('sentiment', 'neutral'),
            sentiment_score = result.get('sentiment_score', 0.0),
            response_time   = round(time.time() - t0, 3),
            ip_address   = request.remote_addr,
            user_agent   = request.headers.get('User-Agent', '')[:200],
        )
        db.session.add(q)

        # Update KB frequency
        kb = KnowledgeBase.query.filter_by(intent=result.get('intent')).first()
        if kb:
            kb.frequency   = (kb.frequency or 0) + 1
            kb.last_used   = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'response':      result['response'],
            'intent':        result.get('intent', 'unknown'),
            'confidence':    result.get('confidence', 0.0),
            'sentiment':     result.get('sentiment', 'neutral'),
            'entities':      result.get('entities', {}),
            'response_time': round(time.time() - t0, 3)
        })

    except Exception as e:
        db.session.rollback()
        print(f'Chat error: {e}')
        return jsonify({
            'response':      'Sorry, something went wrong. Please try again.',
            'intent':        'error',
            'confidence':    0.0,
            'sentiment':     'neutral',
            'entities':      {},
            'response_time': round(time.time() - t0, 3)
        })


@app.route('/api/history', methods=['GET'])
def history():
    session_id = get_or_create_session()
    try:
        rows = (Query.query
                .filter_by(session_id=session_id)
                .order_by(Query.timestamp.asc())
                .limit(50)
                .all())
        return jsonify([{
            'question':  r.question,
            'answer':    r.answer,
            'intent':    r.intent,
            'timestamp': r.timestamp.isoformat() if r.timestamp else None
        } for r in rows])
    except Exception as e:
        print(f'History error: {e}')
        return jsonify([])


@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json(silent=True) or {}
    query_id = data.get('query_id')
    rating   = data.get('rating')
    if not query_id or rating is None:
        return jsonify({'error': 'query_id and rating required'}), 400
    q = Query.query.get(query_id)
    if not q:
        return jsonify({'error': 'Query not found'}), 404
    q.feedback      = rating > 3
    q.feedback_text = data.get('comments', '')
    db.session.commit()
    return jsonify({'message': 'Feedback saved'})


# ── entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    print(f'🚀 College Enquiry Chatbot running on port {port}')
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Called by gunicorn
    init_db()
