import nltk
import re
import spacy
import time
import random
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from difflib import SequenceMatcher
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class Graph:
    """Represents a graph for route finding"""
    
    def __init__(self):
        self.nodes: dict = {}  # node: (lat, lon)
        self.edges: dict = {}  # node: {neighbor: cost}
    
    def add_node(self, node_id: str, lat: float, lon: float):
        """Add a node with coordinates"""
        self.nodes[node_id] = (lat, lon)
        if node_id not in self.edges:
            self.edges[node_id] = {}
    
    def add_edge(self, from_node: str, to_node: str, distance: float):
        """Add a weighted edge between nodes"""
        self.edges[from_node][to_node] = distance
        self.edges[to_node][from_node] = distance
    
    def get_neighbors(self, node: str) -> dict:
        """Get all neighbors of a node"""
        return self.edges.get(node, {})
    
    def get_coordinates(self, node: str) -> tuple:
        """Get coordinates for a node"""
        return self.nodes.get(node, (0, 0))
    
    def heuristic(self, node: str, goal: str) -> float:
        """Euclidean distance heuristic for A* search"""
        if node not in self.nodes or goal not in self.nodes:
            return 0
        lat1, lon1 = self.nodes[node]
        lat2, lon2 = self.nodes[goal]
        return ((lat1 - lat2)**2 + (lon1 - lon2)**2) ** 0.5


class RouteFinder:
    """Intelligent Route Finder using Heuristic Search"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.performance_stats = {
            'nodes_expanded': 0,
            'execution_time': 0,
            'path_cost': 0
        }
    
    def a_star_search(self, start: str, goal: str):
        import heapq
        import time
        
        start_time = time.time()
        nodes_expanded = 0
        open_set = [(0, start, [start], 0)]
        visited = set()
        
        while open_set:
            f_score, current, path, g_score = heapq.heappop(open_set)
            nodes_expanded += 1
            
            if current == goal:
                end_time = time.time()
                self.performance_stats = {
                    'nodes_expanded': nodes_expanded,
                    'execution_time': (end_time - start_time) * 1000,
                    'path_cost': g_score
                }
                return path, g_score
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor, cost in self.graph.get_neighbors(current).items():
                if neighbor in visited:
                    continue
                
                tentative_g_score = g_score + cost
                h_score = self.graph.heuristic(neighbor, goal)
                f_score = tentative_g_score + h_score
                heapq.heappush(open_set, (f_score, neighbor, path + [neighbor], tentative_g_score))
        
        return [], float('inf')
    
    def best_first_search(self, start: str, goal: str):
        import heapq
        import time
        
        start_time = time.time()
        nodes_expanded = 0
        open_set = [(self.graph.heuristic(start, goal), start, [start], 0)]
        visited = set()
        
        while open_set:
            _, current, path, cost = heapq.heappop(open_set)
            nodes_expanded += 1
            
            if current == goal:
                end_time = time.time()
                self.performance_stats = {
                    'nodes_expanded': nodes_expanded,
                    'execution_time': (end_time - start_time) * 1000,
                    'path_cost': cost
                }
                return path, cost
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor, edge_cost in self.graph.get_neighbors(current).items():
                if neighbor not in visited:
                    h_score = self.graph.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (h_score, neighbor, path + [neighbor], cost + edge_cost))
        
        return [], float('inf')
    
    def compare_algorithms(self, start: str, goal: str):
        results = {}
        path_a, cost_a = self.a_star_search(start, goal)
        stats_a = self.performance_stats.copy()
        results['a_star'] = {
            'path': path_a,
            'cost': cost_a,
            'nodes_expanded': stats_a['nodes_expanded'],
            'time_ms': stats_a['execution_time']
        }
        
        path_bf, cost_bf = self.best_first_search(start, goal)
        stats_bf = self.performance_stats.copy()
        results['best_first'] = {
            'path': path_bf,
            'cost': cost_bf,
            'nodes_expanded': stats_bf['nodes_expanded'],
            'time_ms': stats_bf['execution_time']
        }
        
        return results


def create_sample_graph():
    g = Graph()
    nodes = {
        'A': (0, 0), 'B': (2, 1), 'C': (4, 2), 'D': (1, 3),
        'E': (3, 4), 'F': (5, 3), 'G': (6, 5), 'H': (2, 5),
        'I': (4, 1), 'J': (7, 4)
    }
    
    for node, coords in nodes.items():
        g.add_node(node, coords[0], coords[1])
    
    edges = [
        ('A', 'B', 3.5), ('A', 'D', 4.2), ('B', 'C', 2.8),
        ('B', 'E', 3.0), ('B', 'I', 2.5), ('C', 'F', 2.5),
        ('C', 'G', 5.0), ('D', 'E', 2.0), ('E', 'F', 3.2),
        ('E', 'G', 4.5), ('E', 'H', 2.8), ('F', 'G', 2.0),
        ('F', 'J', 3.5), ('G', 'J', 2.8), ('H', 'G', 3.0),
        ('I', 'C', 2.0)
    ]
    
    for u, v, w in edges:
        g.add_edge(u, v, w)
    
    return g


def parse_route_query(query: str):
    query_lower = query.lower()
    start, goal = None, None
    
    location_map = {
        'home': 'A', 'house': 'A', 'start': 'A',
        'market': 'B', 'mall': 'F',
        'school': 'C', 'college': 'C', 'university': 'C',
        'hospital': 'D', 'clinic': 'D',
        'park': 'E', 'garden': 'E',
        'office': 'G', 'work': 'G', 'company': 'G',
        'library': 'H', 'books': 'H',
        'gym': 'I', 'fitness': 'I',
        'stadium': 'J', 'sports': 'J'
    }
    
    from_match = re.search(r'from\s+([A-Za-z]+)', query_lower)
    to_match = re.search(r'to\s+([A-Za-z]+)', query_lower)
    
    if from_match:
        from_word = from_match.group(1)
        if from_word in location_map:
            start = location_map[from_word]
        elif len(from_word) == 1 and from_word.upper() in 'ABCDEFGHIJ':
            start = from_word.upper()
    
    if to_match:
        to_word = to_match.group(1)
        if to_word in location_map:
            goal = location_map[to_word]
        elif len(to_word) == 1 and to_word.upper() in 'ABCDEFGHIJ':
            goal = to_word.upper()
    
    start = start or 'A'
    goal = goal or 'G'
    return start, goal


def get_route_response(start: str, goal: str):
    graph = create_sample_graph()
    finder = RouteFinder(graph)
    
    location_names = {
        'A': 'Home', 'B': 'Market', 'C': 'School', 'D': 'Hospital',
        'E': 'Park', 'F': 'Mall', 'G': 'Office', 'H': 'Library',
        'I': 'Gym', 'J': 'Stadium'
    }
    
    start_name = location_names.get(start, start)
    goal_name = location_names.get(goal, goal)
    results = finder.compare_algorithms(start, goal)
    
    response = "🗺️ **Intelligent Route Finder**\n\n"
    response += f"📍 **Route from {start_name} to {goal_name}**\n\n"
    
    if results['a_star']['path']:
        path_str = ' → '.join([location_names.get(n, n) for n in results['a_star']['path']])
        response += "**🎯 A* Search (Optimal Path)**\n"
        response += f"• Path: {path_str}\n"
        response += f"• Distance: {results['a_star']['cost']:.2f} km\n"
        response += f"• Nodes Explored: {results['a_star']['nodes_expanded']}\n"
        response += f"• Time: {results['a_star']['time_ms']:.2f} ms\n\n"
    else:
        response += "**🎯 A* Search:** No path found\n\n"
    
    if results['best_first']['path']:
        path_str = ' → '.join([location_names.get(n, n) for n in results['best_first']['path']])
        response += "**⚡ Best First Search (Fast Path)**\n"
        response += f"• Path: {path_str}\n"
        response += f"• Distance: {results['best_first']['cost']:.2f} km\n"
        response += f"• Nodes Explored: {results['best_first']['nodes_expanded']}\n"
        response += f"• Time: {results['best_first']['time_ms']:.2f} ms\n\n"
    else:
        response += "**⚡ Best First Search:** No path found\n\n"
    
    if results['a_star']['path'] and results['best_first']['path']:
        response += "**📊 Comparison**\n"
        if results['a_star']['cost'] < results['best_first']['cost']:
            diff = results['best_first']['cost'] - results['a_star']['cost']
            response += f"• A* found the shorter route ({diff:.2f} km shorter)\n"
        else:
            diff = results['a_star']['cost'] - results['best_first']['cost']
            response += f"• Best First found the shorter route ({diff:.2f} km shorter)\n"
        
        if results['a_star']['time_ms'] < results['best_first']['time_ms']:
            time_diff = results['best_first']['time_ms'] - results['a_star']['time_ms']
            response += f"• A* was faster ({time_diff:.2f} ms)\n\n"
        else:
            time_diff = results['a_star']['time_ms'] - results['best_first']['time_ms']
            response += f"• Best First was faster ({time_diff:.2f} ms)\n\n"
    
    response += "**📍 Available Locations**\n"
    response += "A=Home | B=Market | C=School | D=Hospital\n"
    response += "E=Park | F=Mall | G=Office | H=Library\n"
    response += "I=Gym | J=Stadium\n"
    
    return response


class CollegeChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found.")
            self.nlp = None
        
        self.knowledge_base = {
            'greeting': {
                'patterns': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste'],
                'responses': [
                    "Hello! 👋 Welcome to College Enquiry Chatbot.\n\nI can help you with:\n• College admissions, courses, and fees\n• Placement records\n• Library and hostel facilities\n• Route finding with A* and Best First Search\n\nTry asking: 'Admission process' or 'Find route from A to G'"
                ],
                'keywords': ['hi', 'hello', 'hey', 'greeting']
            },
            
            'admission_process': {
                'patterns': ['admission process', 'how to apply', 'apply for admission', 'admission procedure'],
                'responses': [
                    "📋 **Admission Process**\n\n"
                    "1️⃣ Fill the online application form on our website\n\n"
                    "2️⃣ Upload required documents\n"
                    "   • 10th and 12th marksheets\n"
                    "   • Transfer certificate\n"
                    "   • ID proof (Aadhar/Passport)\n"
                    "   • Recent photographs\n\n"
                    "3️⃣ Pay the application fee of ₹500\n\n"
                    "4️⃣ Appear for entrance test and personal interview\n\n"
                    "5️⃣ Check results online on the declared date\n\n"
                    "6️⃣ Complete fee payment to confirm your seat"
                ],
                'keywords': ['admission', 'apply', 'procedure', 'process']
            },
            
            'courses_offered': {
                'patterns': ['courses', 'programs', 'subjects', 'what courses', 'degrees'],
                'responses': [
                    "📚 **Courses Offered**\n\n"
                    "**Undergraduate (UG):**\n"
                    "• BCA - 3 years\n"
                    "• B.Sc Computer Science - 3 years\n"
                    "• B.Com - 3 years\n\n"
                    "**Postgraduate (PG):**\n"
                    "• MCA - 2 years\n"
                    "• MBA - 2 years\n\n"
                    "**Eligibility:**\n"
                    "• UG: 50% in 10+2\n"
                    "• PG: Bachelor's degree with 50%"
                ],
                'keywords': ['course', 'program', 'subject', 'degree']
            },
            
            'fees_structure': {
                'patterns': ['fees', 'fee structure', 'course fees', 'how much', 'cost'],
                'responses': [
                    "💰 **Fee Structure (per year)**\n\n"
                    "**BCA:**\n• Tuition: ₹45,000\n• Total: ₹60,000\n\n"
                    "**B.Sc CS:**\n• Tuition: ₹40,000\n• Total: ₹55,000\n\n"
                    "**MCA:**\n• Tuition: ₹60,000\n• Total: ₹78,000\n\n"
                    "**MBA:**\n• Tuition: ₹80,000\n• Total: ₹95,000\n\n"
                    "**Hostel:** ₹70,000 (includes mess)"
                ],
                'keywords': ['fee', 'fees', 'cost', 'payment']
            },
            
            'placement_records': {
                'patterns': ['placement', 'placements', 'job', 'recruitment', 'company'],
                'responses': [
                    "📊 **Placement Statistics 2025**\n\n"
                    "**Overall:**\n• Placement Rate: 92%\n• Students Placed: 450+\n• Average Package: ₹7.2 LPA\n• Highest Package: ₹25 LPA\n\n"
                    "**Top Recruiters:**\n• TCS, Infosys, Wipro\n• Accenture, Deloitte\n• Amazon, Microsoft\n\n"
                    "**Branch-wise Average:**\n• CSE/IT: ₹8.5 LPA\n• MBA: ₹7.8 LPA\n• MCA: ₹6.5 LPA"
                ],
                'keywords': ['placement', 'job', 'recruitment']
            },
            
            'hostel_facilities': {
                'patterns': ['hostel', 'accommodation', 'stay', 'room', 'mess'],
                'responses': [
                    "🏠 **Hostel Facilities**\n\n"
                    "**Capacity:**\n• Boys: 500 students\n• Girls: 400 students\n\n"
                    "**Room Fees (per year):**\n• Single: ₹80,000\n• Double: ₹70,000\n• Triple: ₹60,000\n\n"
                    "**Amenities:**\n• 24/7 Wi-Fi\n• Modern Gym\n• Common Room\n• Laundry\n• 24/7 Security\n\n"
                    "**Mess Timings:**\n• Breakfast: 7:30-9:00 AM\n• Lunch: 12:00-2:00 PM\n• Dinner: 7:00-9:00 PM"
                ],
                'keywords': ['hostel', 'accommodation', 'stay', 'room', 'mess']
            },
            
            'library_facilities': {
                'patterns': ['library', 'books', 'journals', 'reading', 'study'],
                'responses': [
                    "📚 **Library Facilities**\n\n"
                    "**Timings:**\n• Mon-Fri: 8:00 AM - 8:00 PM\n• Saturday: 9:00 AM - 5:00 PM\n• Sunday: Closed\n\n"
                    "**Collection:**\n• Total Books: 75,000+\n• National Journals: 100+\n• International Journals: 50+\n• E-Books: 25,000+\n\n"
                    "**Digital Resources:**\n• IEEE, ACM, Springer\n• Coursera, Udemy\n• Remote 24/7 access"
                ],
                'keywords': ['library', 'books', 'journals', 'reading']
            },
            
            'contact_info': {
                'patterns': ['contact', 'phone', 'email', 'address', 'reach'],
                'responses': [
                    "📞 **Contact Information**\n\n"
                    "**Phone:**\n• Admission: +91 98765 43210\n• General: +91 98765 43211\n\n"
                    "**Email:** info@college.edu\n\n"
                    "**Address:**\nCollege Road, Education City\nState - 400001\n\n"
                    "**Office Hours:**\n• Mon-Fri: 9:00 AM - 5:00 PM\n• Saturday: 9:00 AM - 1:00 PM\n• Sunday: Closed"
                ],
                'keywords': ['contact', 'phone', 'email', 'address']
            }
        }
    
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_course(self, text):
        courses = {
            'bca': ['bca', 'bachelor of computer applications'],
            'mca': ['mca', 'master of computer applications'],
            'mba': ['mba', 'master of business administration']
        }
        
        text_lower = text.lower()
        for course, keywords in courses.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return course
        return None
    
    def get_best_match(self, query):
        query_lower = query.lower()
        processed_query = self.preprocess_text(query)
        query_words = set(word_tokenize(processed_query))
        
        best_intent = None
        best_score = 0
        
        for intent, data in self.knowledge_base.items():
            score = 0
            
            for pattern in data['patterns']:
                if pattern in query_lower:
                    score += 5
                else:
                    match_ratio = SequenceMatcher(None, pattern, query_lower).ratio()
                    if match_ratio > 0.7:
                        score += 3 * match_ratio
            
            for keyword in data['keywords']:
                if keyword in query_lower:
                    score += 2
                elif any(SequenceMatcher(None, keyword, word).ratio() > 0.8 for word in query_words):
                    score += 1.5
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        confidence = min(best_score / 6, 1.0)
        return best_intent, confidence
    
    def get_response(self, query, user_id=None):
        start_time = time.time()
        
        # Route finding check
        route_keywords = ['route', 'path', 'navigation', 'from', 'to', 'distance', 
                          'shortest', 'way', 'reach', 'directions', 'travel',
                          'a*', 'astar', 'heuristic', 'pathfinding']
        
        if any(keyword in query.lower() for keyword in route_keywords):
            start, goal = parse_route_query(query)
            route_response = get_route_response(start, goal)
            return {
                'response': route_response,
                'intent': 'route_finder',
                'confidence': 0.95,
                'sentiment': 'neutral',
                'sentiment_score': 0,
                'entities': {'start': start, 'goal': goal},
                'response_time': round(time.time() - start_time, 3)
            }
        
        course = self.extract_course(query)
        intent, confidence = self.get_best_match(query)
        
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'good morning']
        if any(word in query.lower() for word in greeting_words):
            intent = 'greeting'
            confidence = 1.0
        
        if not intent or confidence < 0.3:
            response = (
                "I'm not sure I understand. Please rephrase your question.\n\n"
                "**You can ask about:**\n"
                "• Admission process\n"
                "• Courses offered\n"
                "• Fee structure\n"
                "• Placement records\n"
                "• Hostel facilities\n"
                "• Library facilities\n"
                "• Route finding (e.g., 'Find route from A to G')"
            )
        else:
            response = self.knowledge_base[intent]['responses'][0]
        
        blob = TextBlob(query)
        sentiment_score = blob.sentiment.polarity
        sentiment = 'positive' if sentiment_score > 0.3 else 'negative' if sentiment_score < -0.3 else 'neutral'
        
        return {
            'response': response,
            'intent': intent if intent else 'unknown',
            'confidence': confidence,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'entities': {'course': course} if course else {},
            'response_time': round(time.time() - start_time, 3)
        }