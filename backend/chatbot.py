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
        self.edges[to_node][from_node] = distance  # undirected graph
    
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
        """
        A* Search Algorithm
        Combines actual cost (g) + heuristic estimate (h)
        """
        import heapq
        import time
        
        start_time = time.time()
        nodes_expanded = 0
        
        # Priority queue: (f_score, current_node, path, g_score)
        open_set = [(0, start, [start], 0)]
        visited = set()
        
        while open_set:
            # Get node with lowest f_score
            f_score, current, path, g_score = heapq.heappop(open_set)
            nodes_expanded += 1
            
            if current == goal:
                end_time = time.time()
                self.performance_stats = {
                    'nodes_expanded': nodes_expanded,
                    'execution_time': (end_time - start_time) * 1000,  # ms
                    'path_cost': g_score
                }
                return path, g_score
            
            if current in visited:
                continue
            visited.add(current)
            
            # Explore neighbors
            for neighbor, cost in self.graph.get_neighbors(current).items():
                if neighbor in visited:
                    continue
                
                tentative_g_score = g_score + cost
                h_score = self.graph.heuristic(neighbor, goal)
                f_score = tentative_g_score + h_score
                
                heapq.heappush(open_set, (f_score, neighbor, path + [neighbor], tentative_g_score))
        
        return [], float('inf')
    
    def best_first_search(self, start: str, goal: str):
        """
        Best First Search Algorithm
        Prioritizes speed over optimality (uses only heuristic)
        """
        import heapq
        import time
        
        start_time = time.time()
        nodes_expanded = 0
        
        # Priority queue: (heuristic, current_node, path, cost)
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
        """Compare A* and Best First Search performance"""
        results = {}
        
        # A* Search
        path_a, cost_a = self.a_star_search(start, goal)
        stats_a = self.performance_stats.copy()
        results['a_star'] = {
            'path': path_a,
            'cost': cost_a,
            'nodes_expanded': stats_a['nodes_expanded'],
            'time_ms': stats_a['execution_time']
        }
        
        # Best First Search
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
    """Create a sample city map graph for demonstration"""
    g = Graph()
    
    # Add nodes (locations with coordinates)
    nodes = {
        'A': (0, 0),      # Start/Home
        'B': (2, 1),      # Market
        'C': (4, 2),      # School
        'D': (1, 3),      # Hospital
        'E': (3, 4),      # Park
        'F': (5, 3),      # Mall
        'G': (6, 5),      # Office/Goal
        'H': (2, 5),      # Library
        'I': (4, 1),      # Gym
        'J': (7, 4),      # Stadium
    }
    
    for node, coords in nodes.items():
        g.add_node(node, coords[0], coords[1])
    
    # Add edges (roads with distances in km)
    edges = [
        ('A', 'B', 3.5),
        ('A', 'D', 4.2),
        ('B', 'C', 2.8),
        ('B', 'E', 3.0),
        ('B', 'I', 2.5),
        ('C', 'F', 2.5),
        ('C', 'G', 5.0),
        ('D', 'E', 2.0),
        ('E', 'F', 3.2),
        ('E', 'G', 4.5),
        ('E', 'H', 2.8),
        ('F', 'G', 2.0),
        ('F', 'J', 3.5),
        ('G', 'J', 2.8),
        ('H', 'G', 3.0),
        ('I', 'C', 2.0),
    ]
    
    for u, v, w in edges:
        g.add_edge(u, v, w)
    
    return g


def parse_route_query(query: str):
    """Parse route query to extract start and goal locations"""
    query_lower = query.lower()
    
    # Default values
    start = None
    goal = None
    
    # Location mapping
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
    
    # Try to extract from "from X to Y" pattern
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
    
    # Set defaults if still not found
    start = start or 'A'
    goal = goal or 'G'
    
    return start, goal


def get_route_response(start: str, goal: str):
    """Generate route response for given start and goal"""
    graph = create_sample_graph()
    finder = RouteFinder(graph)
    
    # Location mapping for display names
    location_names = {
        'A': 'Home', 'B': 'Market', 'C': 'School', 'D': 'Hospital',
        'E': 'Park', 'F': 'Mall', 'G': 'Office', 'H': 'Library',
        'I': 'Gym', 'J': 'Stadium'
    }
    
    start_name = location_names.get(start, start)
    goal_name = location_names.get(goal, goal)
    
    results = finder.compare_algorithms(start, goal)
    
    # Build formatted response
    response = "🗺️ **Intelligent Route Finder**\n"
    response += "=" * 50 + "\n\n"
    
    response += f"📍 **Route from {start_name} to {goal_name}**\n\n"
    
    # A* Search Results
    if results['a_star']['path']:
        path_str = ' → '.join([location_names.get(n, n) for n in results['a_star']['path']])
        response += "**🎯 A* Search (Optimal Path)**\n"
        response += "─────────────────────────────────\n"
        response += f"• Path: {path_str}\n"
        response += f"• Total Distance: {results['a_star']['cost']:.2f} km\n"
        response += f"• Nodes Explored: {results['a_star']['nodes_expanded']}\n"
        response += f"• Computation Time: {results['a_star']['time_ms']:.2f} ms\n\n"
    else:
        response += "**🎯 A* Search:** No path found\n\n"
    
    # Best First Search Results
    if results['best_first']['path']:
        path_str = ' → '.join([location_names.get(n, n) for n in results['best_first']['path']])
        response += "**⚡ Best First Search (Fast Path)**\n"
        response += "─────────────────────────────────\n"
        response += f"• Path: {path_str}\n"
        response += f"• Total Distance: {results['best_first']['cost']:.2f} km\n"
        response += f"• Nodes Explored: {results['best_first']['nodes_expanded']}\n"
        response += f"• Computation Time: {results['best_first']['time_ms']:.2f} ms\n\n"
    else:
        response += "**⚡ Best First Search:** No path found\n\n"
    
    # Comparison Analysis
    response += "**📊 Algorithm Comparison**\n"
    response += "─────────────────────────────────\n"
    
    if results['a_star']['path'] and results['best_first']['path']:
        if results['a_star']['cost'] < results['best_first']['cost']:
            diff = results['best_first']['cost'] - results['a_star']['cost']
            response += f"• ✅ A* Search found the SHORTER route ({diff:.2f} km shorter)\n"
        else:
            diff = results['a_star']['cost'] - results['best_first']['cost']
            response += f"• ✅ Best First Search found the SHORTER route ({diff:.2f} km shorter)\n"
        
        if results['a_star']['time_ms'] < results['best_first']['time_ms']:
            time_diff = results['best_first']['time_ms'] - results['a_star']['time_ms']
            response += f"• ✅ A* Search was FASTER ({time_diff:.2f} ms)\n"
        else:
            time_diff = results['a_star']['time_ms'] - results['best_first']['time_ms']
            response += f"• ✅ Best First Search was FASTER ({time_diff:.2f} ms)\n"
    
    # Heuristic Information
    response += "\n**🧠 Heuristic Used**\n"
    response += "─────────────────────────────────\n"
    response += "• Euclidean distance (straight-line)\n"
    response += "• Estimates remaining distance to goal\n"
    response += "• Guides search toward target efficiently\n\n"
    
    # Industry Context
    response += "**💡 Industry Applications**\n"
    response += "─────────────────────────────────\n"
    response += "• **Navigation Apps:** Google Maps, Apple Maps, Waze\n"
    response += "• **Logistics:** Delivery route optimization\n"
    response += "• **Cloud Computing:** Network traffic routing\n"
    response += "• **Transportation:** Ride-sharing route planning\n\n"
    
    response += "**📍 Available Locations**\n"
    response += "─────────────────────────────────\n"
    response += "A = Home | B = Market | C = School | D = Hospital\n"
    response += "E = Park | F = Mall | G = Office | H = Library\n"
    response += "I = Gym | J = Stadium\n\n"
    
    response += "**💡 Try these queries:**\n"
    response += "• 'Find route from A to G'\n"
    response += "• 'Shortest path from home to office'\n"
    response += "• 'Navigation from market to stadium'"
    
    return response


class CollegeChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not found. Some features may be limited.")
            self.nlp = None
        
        # Comprehensive knowledge base with proper formatting including route finder
        self.knowledge_base = {
            'greeting': {
                'patterns': [
                    'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                    'namaste', 'hola', 'howdy', 'whats up', 'sup'
                ],
                'responses': [
                    "Hello! 👋 Welcome to College Enquiry Chatbot.\n\nI can help you with:\n• College admissions, courses, and fees\n• Placement records and companies\n• Library, hostel, and other facilities\n• **Route finding** with A* and Best First Search algorithms\n\nTry asking: 'Find route from home to office' or 'Shortest path from A to G'",
                    "Hi there! 😊 I'm here to answer your college questions and help you find optimal routes using heuristic search algorithms like A* and Best First Search!",
                    "Greetings! 🎓 How can I assist you today? You can ask about college admissions or try route finding queries like 'Find route from A to G'."
                ],
                'keywords': ['hi', 'hello', 'hey', 'greeting', 'namaste', 'howdy']
            },
            'route_finder': {
                'patterns': [
                    'route', 'path', 'find route', 'shortest path', 'navigation',
                    'how to reach', 'distance between', 'from to', 'way to',
                    'directions', 'reach', 'travel to', 'go to', 'find path',
                    'optimal route', 'best route', 'fastest route', 'a*', 'astar',
                    'best first', 'heuristic', 'pathfinding', 'location', 'map'
                ],
                'responses': [],  # Dynamic - handled in get_response
                'keywords': ['route', 'path', 'from', 'to', 'distance', 'navigation', 
                             'way', 'reach', 'travel', 'direction', 'location', 'map']
            },
            'admission_process': {
                'patterns': [
                    'admission process', 'how to apply', 'apply for admission', 'admission procedure',
                    'how can i get admission', 'admission steps', 'process of admission',
                    'what is the admission process', 'tell me about admission'
                ],
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
                'keywords': ['admission', 'apply', 'procedure', 'process', 'steps']
            },
            'hostel_general': {
                'patterns': [
                    'hostel', 'accommodation', 'hostel facility', 'dormitory',
                    'hostel details', 'tell me about hostel', 'hostel information'
                ],
                'responses': [
                    "🏠 **Hostel Facilities**\n\n"
                    "• Separate hostels for Boys (500) and Girls (400)\n"
                    "• Room Types: Single, Double, Triple sharing\n"
                    "• Annual Fee: ₹70,000 (includes mess)\n\n"
                    "**Amenities:** Wi-Fi, Gym, Common Room, Laundry, 24/7 Security"
                ],
                'keywords': ['hostel', 'accommodation', 'dorm', 'stay']
            },
            'placement_stats': {
                'patterns': [
                    'placement statistics', 'placement record', 'placement data',
                    'tell me about placements', 'how is placement'
                ],
                'responses': [
                    "📊 **Placement Statistics 2025**\n\n"
                    "• Placement Rate: **92%**\n"
                    "• Average Package: **₹7.2 LPA**\n"
                    "• Highest Package: **₹25 LPA**\n"
                    "• Students Placed: **450+**\n\n"
                    "**Top Recruiters:** TCS, Infosys, Wipro, Accenture, Amazon, Microsoft"
                ],
                'keywords': ['placement', 'statistics', 'record']
            },
            'contact': {
                'patterns': [
                    'contact', 'phone', 'email', 'address', 'reach', 'call',
                    'phone number', 'college address'
                ],
                'responses': [
                    "📞 **Contact Information**\n\n"
                    "• Admission: +91 98765 43210\n"
                    "• General: +91 98765 43211\n"
                    "• Email: info@college.edu\n\n"
                    "**Address:** College Road, Education City, State - 400001"
                ],
                'keywords': ['contact', 'phone', 'email', 'address', 'call']
            }
        }
    
    def preprocess_text(self, text):
        """Advanced text preprocessing with NLTK"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_course(self, text):
        """Extract specific course mentioned in query"""
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
        """Find the best matching intent using NLP and Fuzzy Matching"""
        query_lower = query.lower()
        processed_query = self.preprocess_text(query)
        query_words = set(word_tokenize(processed_query))
        
        best_intent = None
        best_score = 0
        
        for intent, data in self.knowledge_base.items():
            score = 0
            
            # Pattern matching
            for pattern in data['patterns']:
                if pattern in query_lower:
                    score += 5
                else:
                    match_ratio = SequenceMatcher(None, pattern, query_lower).ratio()
                    if match_ratio > 0.7:
                        score += 3 * match_ratio
            
            # Keyword matching
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
        """Main method to get chatbot response"""
        start_time = time.time()
        
        # Check if it's a route finding query FIRST
        route_keywords = ['route', 'path', 'navigation', 'from', 'to', 'distance', 
                          'shortest', 'way', 'reach', 'directions', 'travel',
                          'a*', 'astar', 'heuristic', 'pathfinding', 'location', 'map']
        
        if any(keyword in query.lower() for keyword in route_keywords):
            # Parse start and goal from query
            start, goal = parse_route_query(query)
            
            # Generate route response
            route_response = get_route_response(start, goal)
            
            return {
                'response': route_response,
                'intent': 'route_finder',
                'confidence': 0.95,
                'sentiment': 'neutral',
                'sentiment_score': 0,
                'entities': {'start': start, 'goal': goal, 'query_type': 'route_finding'},
                'response_time': round(time.time() - start_time, 3)
            }
        
        # Extract course if mentioned
        course = self.extract_course(query)
        
        # Get best matching intent
        intent, confidence = self.get_best_match(query)
        
        # Check for greetings
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'good morning', 'good afternoon']
        if any(word in query.lower() for word in greeting_words):
            intent = 'greeting'
            confidence = 1.0
        
        # If no match found
        if not intent or confidence < 0.3:
            response = (
                "I'm not sure I understand. Could you please rephrase your question?\n\n"
                "**You can ask me about:**\n"
                "• Admission process, dates, and eligibility\n"
                "• Course details (BCA, MCA, MBA)\n"
                "• Fee structure\n"
                "• Placement records\n"
                "• Hostel facilities\n"
                "• **Route finding** (e.g., 'Find route from A to G' or 'How to reach home from office')"
            )
        else:
            response = self.knowledge_base[intent]['responses'][0]
        
        # Analyze sentiment
        blob = TextBlob(query)
        sentiment_score = blob.sentiment.polarity
        if sentiment_score > 0.3:
            sentiment = 'positive'
        elif sentiment_score < -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        response_time = time.time() - start_time
        
        return {
            'response': response,
            'intent': intent if intent else 'unknown',
            'confidence': confidence,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'entities': {'course': course} if course else {},
            'response_time': round(response_time, 3)
        }