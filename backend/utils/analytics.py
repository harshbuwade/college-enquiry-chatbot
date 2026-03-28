# utils/analytics.py
from models import db, Query, User, KnowledgeBase
from datetime import datetime, timedelta
from sqlalchemy import func

class Analytics:
    """Analytics class for tracking chatbot usage and performance"""
    
    @staticmethod
    def get_total_queries():
        """Get total number of queries"""
        return Query.query.count()
    
    @staticmethod
    def get_unique_users():
        """Get number of unique users"""
        return db.session.query(Query.user_id).distinct().count()
    
    @staticmethod
    def get_queries_today():
        """Get number of queries today"""
        today = datetime.utcnow().date()
        return Query.query.filter(func.date(Query.timestamp) == today).count()
    
    @staticmethod
    def get_popular_intents(limit=5):
        """Get most popular intents"""
        return db.session.query(
            Query.intent, 
            func.count(Query.intent).label('count')
        ).group_by(Query.intent).order_by(func.count(Query.intent).desc()).limit(limit).all()
    
    @staticmethod
    def get_average_confidence():
        """Get average confidence score"""
        result = db.session.query(func.avg(Query.confidence)).scalar()
        return float(result) if result else 0
    
    @staticmethod
    def get_average_response_time():
        """Get average response time"""
        result = db.session.query(func.avg(Query.response_time)).scalar()
        return float(result) if result else 0
    
    @staticmethod
    def get_sentiment_distribution():
        """Get distribution of sentiments"""
        return db.session.query(
            Query.sentiment, 
            func.count(Query.sentiment).label('count')
        ).group_by(Query.sentiment).all()
    
    @staticmethod
    def get_queries_over_time(days=7):
        """Get number of queries per day for last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.session.query(
            func.date(Query.timestamp).label('date'),
            func.count(Query.id).label('count')
        ).filter(Query.timestamp >= cutoff_date).group_by(func.date(Query.timestamp)).all()
    
    @staticmethod
    def get_user_retention():
        """Get user retention stats"""
        # Users with more than 5 queries
        active_users = db.session.query(
            Query.user_id, 
            func.count(Query.id).label('query_count')
        ).group_by(Query.user_id).having(func.count(Query.id) > 5).count()
        
        total_users = db.session.query(User).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'retention_rate': (active_users / total_users * 100) if total_users > 0 else 0
        }
    
    @staticmethod
    def get_knowledge_base_stats():
        """Get knowledge base usage statistics"""
        return db.session.query(
            KnowledgeBase.intent,
            KnowledgeBase.question_pattern,
            KnowledgeBase.frequency,
            KnowledgeBase.success_rate
        ).order_by(KnowledgeBase.frequency.desc()).all()
    
    @staticmethod
    def get_hourly_activity():
        """Get activity by hour of day"""
        return db.session.query(
            func.strftime('%H', Query.timestamp).label('hour'),
            func.count(Query.id).label('count')
        ).group_by('hour').order_by('hour').all()
    
    @staticmethod
    def get_dashboard_stats():
        """Get all stats for dashboard"""
        return {
            'total_queries': Analytics.get_total_queries(),
            'unique_users': Analytics.get_unique_users(),
            'queries_today': Analytics.get_queries_today(),
            'avg_confidence': Analytics.get_average_confidence(),
            'avg_response_time': Analytics.get_average_response_time(),
            'popular_intents': [{'intent': i[0], 'count': i[1]} for i in Analytics.get_popular_intents()],
            'sentiment_distribution': [{'sentiment': s[0], 'count': s[1]} for s in Analytics.get_sentiment_distribution()],
            'user_retention': Analytics.get_user_retention()
        }