"""
chatbot.py
College Enquiry Chatbot – core logic
Includes: Graph, RouteFinder (A* & Best-First), CollegeChatbot with NLP
"""
import heapq
import nltk
import re
import time
import random
from difflib import SequenceMatcher
from textblob import TextBlob

# ── NLTK bootstrap ─────────────────────────────────────────────────────────────
def _ensure_nltk():
    """Download NLTK packages only if missing; suppress all output."""
    _pkgs = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    for pkg in _pkgs:
        try:
            nltk.download(pkg, quiet=True, raise_on_error=False)
        except Exception:
            pass

_ensure_nltk()

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ──────────────────────────────────────────────────────────────────────────────
#  GRAPH & ROUTE FINDER
# ──────────────────────────────────────────────────────────────────────────────
class Graph:
    """Weighted undirected graph for route finding."""

    def __init__(self):
        self.nodes: dict = {}   # node_id → (x, y) coords
        self.edges: dict = {}   # node_id → {neighbour: cost}

    def add_node(self, node_id: str, x: float, y: float):
        self.nodes[node_id] = (x, y)
        self.edges.setdefault(node_id, {})

    def add_edge(self, u: str, v: str, cost: float):
        self.edges.setdefault(u, {})[v] = cost
        self.edges.setdefault(v, {})[u] = cost

    def get_neighbors(self, node: str) -> dict:
        return self.edges.get(node, {})

    def get_coordinates(self, node: str) -> tuple:
        return self.nodes.get(node, (0, 0))

    def heuristic(self, node: str, goal: str) -> float:
        """Euclidean distance heuristic."""
        if node not in self.nodes or goal not in self.nodes:
            return 0
        x1, y1 = self.nodes[node]
        x2, y2 = self.nodes[goal]
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


class RouteFinder:
    """Heuristic search algorithms: A* and Best-First Search."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.performance_stats: dict = {}

    # ── A* ─────────────────────────────────────────────────────────────────────
    def a_star_search(self, start: str, goal: str):
        t0 = time.time()
        nodes_expanded = 0
        open_set = [(0, start, [start], 0)]   # (f, node, path, g)
        visited: set = set()

        while open_set:
            f, current, path, g = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == goal:
                self.performance_stats = {
                    'nodes_expanded': nodes_expanded,
                    'execution_time': (time.time() - t0) * 1000,
                    'path_cost': g
                }
                return path, g

            if current in visited:
                continue
            visited.add(current)

            for neighbour, cost in self.graph.get_neighbors(current).items():
                if neighbour in visited:
                    continue
                new_g = g + cost
                h = self.graph.heuristic(neighbour, goal)
                heapq.heappush(open_set, (new_g + h, neighbour, path + [neighbour], new_g))

        self.performance_stats = {'nodes_expanded': nodes_expanded,
                                   'execution_time': (time.time() - t0) * 1000,
                                   'path_cost': float('inf')}
        return [], float('inf')

    # ── Best-First ─────────────────────────────────────────────────────────────
    def best_first_search(self, start: str, goal: str):
        t0 = time.time()
        nodes_expanded = 0
        open_set = [(self.graph.heuristic(start, goal), start, [start], 0)]
        visited: set = set()

        while open_set:
            _, current, path, cost = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == goal:
                self.performance_stats = {
                    'nodes_expanded': nodes_expanded,
                    'execution_time': (time.time() - t0) * 1000,
                    'path_cost': cost
                }
                return path, cost

            if current in visited:
                continue
            visited.add(current)

            for neighbour, edge_cost in self.graph.get_neighbors(current).items():
                if neighbour not in visited:
                    h = self.graph.heuristic(neighbour, goal)
                    heapq.heappush(open_set, (h, neighbour, path + [neighbour], cost + edge_cost))

        self.performance_stats = {'nodes_expanded': nodes_expanded,
                                   'execution_time': (time.time() - t0) * 1000,
                                   'path_cost': float('inf')}
        return [], float('inf')

    # ── Compare ────────────────────────────────────────────────────────────────
    def compare_algorithms(self, start: str, goal: str) -> dict:
        path_a, cost_a = self.a_star_search(start, goal)
        stats_a = self.performance_stats.copy()

        path_b, cost_b = self.best_first_search(start, goal)
        stats_b = self.performance_stats.copy()

        return {
            'a_star': {
                'path': path_a, 'cost': cost_a,
                'nodes_expanded': stats_a['nodes_expanded'],
                'time_ms': stats_a['execution_time']
            },
            'best_first': {
                'path': path_b, 'cost': cost_b,
                'nodes_expanded': stats_b['nodes_expanded'],
                'time_ms': stats_b['execution_time']
            }
        }


# ──────────────────────────────────────────────────────────────────────────────
#  SAMPLE GRAPH FACTORY
# ──────────────────────────────────────────────────────────────────────────────
LOCATION_NAMES = {
    'A': 'Home', 'B': 'Market', 'C': 'School', 'D': 'Hospital',
    'E': 'Park', 'F': 'Mall',   'G': 'Office', 'H': 'Library',
    'I': 'Gym',  'J': 'Stadium'
}
LOCATION_MAP = {
    'home': 'A', 'house': 'A', 'start': 'A',
    'market': 'B', 'bazaar': 'B',
    'school': 'C', 'college': 'C', 'university': 'C',
    'hospital': 'D', 'clinic': 'D', 'medical': 'D',
    'park': 'E', 'garden': 'E',
    'mall': 'F', 'shopping': 'F',
    'office': 'G', 'work': 'G', 'company': 'G',
    'library': 'H', 'books': 'H',
    'gym': 'I', 'fitness': 'I',
    'stadium': 'J', 'sports': 'J', 'ground': 'J'
}


def create_sample_graph() -> Graph:
    g = Graph()
    nodes = {
        'A': (0, 0), 'B': (2, 1), 'C': (4, 2), 'D': (1, 3),
        'E': (3, 4), 'F': (5, 3), 'G': (6, 5), 'H': (2, 5),
        'I': (4, 1), 'J': (7, 4)
    }
    for nid, (x, y) in nodes.items():
        g.add_node(nid, x, y)

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
    ql = query.lower()
    start = goal = None

    from_m = re.search(r'from\s+([a-z]+)', ql)
    to_m   = re.search(r'to\s+([a-z]+)',   ql)

    def resolve(word):
        if word in LOCATION_MAP:
            return LOCATION_MAP[word]
        if len(word) == 1 and word.upper() in LOCATION_NAMES:
            return word.upper()
        return None

    if from_m:
        start = resolve(from_m.group(1))
    if to_m:
        goal = resolve(to_m.group(1))

    return start or 'A', goal or 'G'


def get_route_response(start: str, goal: str) -> str:
    graph  = create_sample_graph()
    finder = RouteFinder(graph)
    res    = finder.compare_algorithms(start, goal)

    sn = LOCATION_NAMES.get(start, start)
    gn = LOCATION_NAMES.get(goal,  goal)

    lines = [
        f"🗺️ **Intelligent Route Finder**\n",
        f"**Route from {sn} to {gn}**\n",
    ]

    # A*
    if res['a_star']['path']:
        p = ' → '.join(LOCATION_NAMES.get(n, n) for n in res['a_star']['path'])
        lines += [
            "**A* Search (Optimal Path)**",
            f"• Path: {p}",
            f"• Distance: {res['a_star']['cost']:.2f} km",
            f"• Nodes Explored: {res['a_star']['nodes_expanded']}",
            f"• Time: {res['a_star']['time_ms']:.3f} ms\n",
        ]
    else:
        lines.append("**A* Search:** No path found\n")

    # Best-First
    if res['best_first']['path']:
        p = ' → '.join(LOCATION_NAMES.get(n, n) for n in res['best_first']['path'])
        lines += [
            "**Best First Search (Greedy Path)**",
            f"• Path: {p}",
            f"• Distance: {res['best_first']['cost']:.2f} km",
            f"• Nodes Explored: {res['best_first']['nodes_expanded']}",
            f"• Time: {res['best_first']['time_ms']:.3f} ms\n",
        ]
    else:
        lines.append("**Best First Search:** No path found\n")

    # Comparison
    if res['a_star']['path'] and res['best_first']['path']:
        lines.append("**Algorithm Comparison**")
        ca, cb = res['a_star']['cost'], res['best_first']['cost']
        if ca <= cb:
            lines.append(f"• A* found the shorter route ({abs(cb - ca):.2f} km saved)")
        else:
            lines.append(f"• Best First found the shorter route ({abs(ca - cb):.2f} km saved)")

        ta, tb = res['a_star']['time_ms'], res['best_first']['time_ms']
        if ta <= tb:
            lines.append(f"• A* was faster ({abs(tb - ta):.3f} ms difference)\n")
        else:
            lines.append(f"• Best First was faster ({abs(ta - tb):.3f} ms difference)\n")

    lines += [
        "**Available Locations**",
        "A=Home  | B=Market  | C=School | D=Hospital | E=Park",
        "F=Mall  | G=Office  | H=Library | I=Gym     | J=Stadium",
        "\nTry: *'Find route from Home to Stadium'*"
    ]
    return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  COLLEGE CHATBOT
# ──────────────────────────────────────────────────────────────────────────────
class CollegeChatbot:

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))

        self.knowledge_base = self._build_knowledge_base()

    # ── knowledge base ─────────────────────────────────────────────────────────
    @staticmethod
    def _build_knowledge_base() -> dict:
        return {
            'greeting': {
                'patterns': ['hi', 'hello', 'hey', 'good morning', 'good afternoon',
                             'good evening', 'namaste', 'greetings', 'howdy'],
                'responses': [
                    "👋 **Welcome to College Enquiry Chatbot**.\n\n"
                    "I can help you with:\n"
                    "• Admissions & process\n"
                    "• Courses & programs\n"
                    "• Fee structure\n"
                    "• Placement records\n"
                    "• Hostel facilities\n"
                    "• Library facilities\n"
                    "• Scholarships\n"
                    "• Smart route finding\n\n"
                    "Try asking: *'Admission process'* or *'Find route from Home to Office'*"
                ],
                'keywords': ['hi', 'hello', 'hey', 'greeting', 'namaste']
            },

            'admission_process': {
                'patterns': ['admission process', 'how to apply', 'apply for admission',
                             'admission procedure', 'get admission', 'enrollment'],
                'responses': [
                    "📋 **Admission Process**\n\n"
                    "1. **Online Application**\n"
                    "   • Visit our website and fill the form\n"
                    "   • Application fee: ₹500 (non-refundable)\n\n"
                    "2. **Required Documents**\n"
                    "   • 10th & 12th marksheets & certificates\n"
                    "   • Transfer certificate\n"
                    "   • ID proof (Aadhar / Passport)\n"
                    "   • Passport-size photographs (4 copies)\n\n"
                    "3. **Entrance Test & Interview**\n"
                    "   • Written test (aptitude + subject)\n"
                    "   • Personal interview round\n\n"
                    "4. **Result & Seat Confirmation**\n"
                    "   • Results declared within 7 working days\n"
                    "   • Pay fees within 3 days to confirm seat\n\n"
                    "**Key Dates (2025–26)**\n"
                    "   • Application Open: 1st May 2025\n"
                    "   • Entrance Test: 20th June 2025\n"
                    "   • Results: 30th June 2025"
                ],
                'keywords': ['admission', 'apply', 'procedure', 'process', 'enroll', 'join']
            },

            'courses_offered': {
                'patterns': ['courses', 'programs', 'subjects', 'what courses',
                             'degrees available', 'what do you offer'],
                'responses': [
                    "📚 **Courses Offered**\n\n"
                    "**Undergraduate (UG) Programs**\n"
                    "• BCA – Bachelor of Computer Applications (3 yrs)\n"
                    "• B.Sc Computer Science (3 yrs)\n"
                    "• B.Com – Bachelor of Commerce (3 yrs)\n"
                    "• BBA – Bachelor of Business Administration (3 yrs)\n\n"
                    "**Postgraduate (PG) Programs**\n"
                    "• MCA – Master of Computer Applications (2 yrs)\n"
                    "• MBA – Master of Business Administration (2 yrs)\n"
                    "• M.Sc Data Science (2 yrs)  *(New 2025!)*\n\n"
                    "**Eligibility**\n"
                    "• UG: Minimum 50% in 10+2 from recognised board\n"
                    "• PG: Bachelor's degree with minimum 50%\n\n"
                    "**Specialisations** – AI/ML, Cybersecurity, Finance, Marketing"
                ],
                'keywords': ['course', 'program', 'subject', 'degree', 'bca', 'mca', 'mba']
            },

            'fees_structure': {
                'patterns': ['fees', 'fee structure', 'course fees', 'how much does it cost',
                             'tuition fees', 'what is the fee'],
                'responses': [
                    "💰 **Fee Structure (Per Academic Year)**\n\n"
                    "**Undergraduate Programs**\n"
                    "• BCA          – Tuition: ₹45,000 | Total: ₹60,000\n"
                    "• B.Sc CS      – Tuition: ₹40,000 | Total: ₹55,000\n"
                    "• B.Com / BBA  – Tuition: ₹35,000 | Total: ₹48,000\n\n"
                    "**Postgraduate Programs**\n"
                    "• MCA          – Tuition: ₹60,000 | Total: ₹78,000\n"
                    "• MBA          – Tuition: ₹80,000 | Total: ₹95,000\n"
                    "• M.Sc DS      – Tuition: ₹65,000 | Total: ₹82,000\n\n"
                    "**Hostel (Optional)**\n"
                    "• Single room  – ₹80,000/year (incl. mess)\n"
                    "• Double room  – ₹70,000/year (incl. mess)\n"
                    "• Triple room  – ₹60,000/year (incl. mess)\n\n"
                    "**Payment Options**\n"
                    "• Semester-wise payment available\n"
                    "• Education loan assistance provided\n"
                    "• Scholarships for meritorious students (up to 50%)"
                ],
                'keywords': ['fee', 'fees', 'cost', 'payment', 'tuition', 'charges']
            },

            'placement_records': {
                'patterns': ['placement', 'placements', 'job', 'recruitment', 'hiring',
                             'companies recruiting', 'campus placement'],
                'responses': [
                    "📊 **Placement Statistics 2024–25**\n\n"
                    "**Overall Performance**\n"
                    "• Placement Rate   : 92%\n"
                    "• Students Placed  : 450+\n"
                    "• Average Package  : ₹7.2 LPA\n"
                    "• Highest Package  : ₹25 LPA\n"
                    "• Median Package   : ₹6.5 LPA\n\n"
                    "**Top Recruiters**\n"
                    "• IT Giants  : TCS, Infosys, Wipro, HCL\n"
                    "• Consultancy: Accenture, Deloitte, Cognizant\n"
                    "• Product    : Amazon, Microsoft, Flipkart\n"
                    "• Startups   : Razorpay, Zomato, Swiggy\n\n"
                    "**Branch-Wise Average Package**\n"
                    "• CSE / BCA / MCA : ₹8.5 LPA\n"
                    "• MBA             : ₹7.8 LPA\n"
                    "• M.Sc DS         : ₹9.2 LPA  *(new batch!)*\n"
                    "• B.Com / BBA     : ₹5.5 LPA\n\n"
                    "**Placement Cell Services**\n"
                    "• Resume & aptitude workshops\n"
                    "• Mock interviews & GD sessions\n"
                    "• Industry mentorship programme"
                ],
                'keywords': ['placement', 'job', 'recruitment', 'package', 'salary', 'lpa']
            },

            'hostel_facilities': {
                'patterns': ['hostel', 'accommodation', 'stay', 'room', 'mess',
                             'boarding', 'dorm'],
                'responses': [
                    "🏠 **Hostel Facilities**\n\n"
                    "**Capacity**\n"
                    "• Boys Hostel  : 500 students (4 blocks)\n"
                    "• Girls Hostel : 400 students (3 blocks)\n\n"
                    "**Room Types & Fees (Per Year)**\n"
                    "• Single Occupancy : ₹80,000\n"
                    "• Double Occupancy : ₹70,000\n"
                    "• Triple Occupancy : ₹60,000\n"
                    "  *(All fees include mess charges)*\n\n"
                    "**Amenities**\n"
                    "• 24×7 High-speed Wi-Fi (100 Mbps)\n"
                    "• Modern Gym & Sports Room\n"
                    "• Common Room with TV & Recreation\n"
                    "• Laundry & Housekeeping\n"
                    "• 24×7 CCTV & Security\n"
                    "• Backup Power (Generator)\n"
                    "• Medical Room & First Aid\n\n"
                    "**Mess Timings**\n"
                    "• Breakfast : 7:30 AM – 9:00 AM\n"
                    "• Lunch     : 12:00 PM – 2:00 PM\n"
                    "• Snacks    : 5:00 PM – 6:00 PM\n"
                    "• Dinner    : 7:00 PM – 9:00 PM"
                ],
                'keywords': ['hostel', 'accommodation', 'stay', 'room', 'mess', 'boarding']
            },

            'library_facilities': {
                'patterns': ['library', 'books', 'journals', 'reading room', 'study',
                             'e-books', 'digital library'],
                'responses': [
                    "📖 **Library Facilities**\n\n"
                    "**Timings**\n"
                    "• Monday – Friday : 8:00 AM – 9:00 PM\n"
                    "• Saturday        : 9:00 AM – 5:00 PM\n"
                    "• Sunday          : Closed\n\n"
                    "**Collection**\n"
                    "• Physical Books         : 75,000+\n"
                    "• National Journals      : 120+\n"
                    "• International Journals : 60+\n"
                    "• E-Books                : 25,000+\n"
                    "• Theses & Projects      : 5,000+\n\n"
                    "**Digital Resources**\n"
                    "• IEEE Xplore & ACM Digital Library\n"
                    "• Springer & Elsevier Journals\n"
                    "• NPTEL Video Lectures\n"
                    "• Coursera & Udemy institutional access\n"
                    "• Remote access 24×7 via VPN\n\n"
                    "**Infrastructure**\n"
                    "• 100-seat air-conditioned reading room\n"
                    "• 20 dedicated digital workstations\n"
                    "• Book borrowing: 4 books for 15 days"
                ],
                'keywords': ['library', 'books', 'journals', 'reading', 'study', 'ebook']
            },

            'contact_info': {
                'patterns': ['contact', 'phone number', 'email', 'address', 'how to reach',
                             'location', 'office hours'],
                'responses': [
                    "📞 **Contact Information**\n\n"
                    "**Phone Numbers**\n"
                    "• Admissions Desk   : +91 98765 43210\n"
                    "• General Enquiry   : +91 98765 43211\n"
                    "• Placement Cell    : +91 98765 43212\n"
                    "• Hostel Office     : +91 98765 43213\n\n"
                    "**Email**\n"
                    "• General     : info@college.edu.in\n"
                    "• Admissions  : admissions@college.edu.in\n"
                    "• Placements  : placements@college.edu.in\n\n"
                    "**Address**\n"
                    "   College Road, Education City\n"
                    "   Maharashtra – 400001, India\n\n"
                    "**Office Hours**\n"
                    "• Monday – Friday : 9:00 AM – 5:00 PM\n"
                    "• Saturday        : 9:00 AM – 1:00 PM\n"
                    "• Sunday          : Closed\n\n"
                    "**Website**: www.college.edu.in"
                ],
                'keywords': ['contact', 'phone', 'email', 'address', 'reach', 'location']
            },

            'scholarship': {
                'patterns': ['scholarship', 'financial aid', 'merit', 'fee waiver',
                             'discount', 'bursary'],
                'responses': [
                    "🏅 **Scholarships & Financial Aid**\n\n"
                    "**Merit-Based Scholarships**\n"
                    "• 90%+ in qualifying exam  → 50% tuition waiver\n"
                    "• 80–90%                   → 25% tuition waiver\n"
                    "• Rank 1 in Entrance Test  → Full fee waiver\n\n"
                    "**Government Schemes**\n"
                    "• SC/ST/OBC scholarships (state & central)\n"
                    "• EWS financial assistance\n"
                    "• National Scholarship Portal (NSP) support\n\n"
                    "**Education Loans**\n"
                    "• Tie-ups with SBI, Axis Bank, HDFC\n"
                    "• Loans up to ₹20 lakh at preferential rates\n\n"
                    "**How to Apply**\n"
                    "• Submit scholarship form at Student Affairs Office\n"
                    "• Deadline: 30 days after admission confirmation"
                ],
                'keywords': ['scholarship', 'financial', 'merit', 'waiver', 'discount']
            }
        }

    # ── NLP helpers ────────────────────────────────────────────────────────────
    def preprocess(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_course(self, text: str):
        courses = {
            'bca': ['bca', 'bachelor of computer applications'],
            'mca': ['mca', 'master of computer applications'],
            'mba': ['mba', 'master of business administration'],
            'bsc': ['bsc', 'b.sc', 'bachelor of science'],
            'msc': ['msc', 'm.sc', 'master of science', 'data science'],
            'bcom': ['bcom', 'b.com', 'bachelor of commerce'],
            'bba': ['bba', 'bachelor of business administration'],
        }
        tl = text.lower()
        for course, kws in courses.items():
            for kw in kws:
                if kw in tl:
                    return course
        return None

    def get_best_match(self, query: str):
        ql          = query.lower()
        processed   = self.preprocess(query)
        query_words = set(word_tokenize(processed))

        best_intent = None
        best_score  = 0

        for intent, data in self.knowledge_base.items():
            score = 0.0

            # Direct pattern match
            for pattern in data['patterns']:
                if pattern in ql:
                    score += 5
                else:
                    ratio = SequenceMatcher(None, pattern, ql).ratio()
                    if ratio > 0.65:
                        score += 3 * ratio

            # Keyword match
            for kw in data['keywords']:
                if kw in ql:
                    score += 2
                elif any(SequenceMatcher(None, kw, w).ratio() > 0.8 for w in query_words):
                    score += 1.5

            if score > best_score:
                best_score  = score
                best_intent = intent

        confidence = min(best_score / 6.0, 1.0)
        return best_intent, confidence

    # ── main entry point ───────────────────────────────────────────────────────
    def get_response(self, query: str, user_id=None) -> dict:
        t0 = time.time()

        route_triggers = [
            'route', 'path', 'navigate', 'navigation', 'direction',
            'shortest', 'way to', 'how to reach', 'distance from',
            'a* ', 'astar', 'best first', 'heuristic', 'pathfind',
            'travel from', 'go from'
        ]

        ql = query.lower()

        # Route finding branch
        if ('from ' in ql and ' to ' in ql) or any(kw in ql for kw in route_triggers):
            start, goal = parse_route_query(query)
            return {
                'response':      get_route_response(start, goal),
                'intent':        'route_finder',
                'confidence':    0.97,
                'sentiment':     'neutral',
                'sentiment_score': 0.0,
                'entities':      {'start': start, 'goal': goal},
                'response_time': round(time.time() - t0, 3)
            }

        # Greeting priority
        greeting_words = ['hi', 'hello', 'hey', 'namaste', 'good morning',
                          'good afternoon', 'good evening', 'howdy']
        if any(ql.startswith(gw) or ql == gw for gw in greeting_words):
            intent     = 'greeting'
            confidence = 1.0
        else:
            intent, confidence = self.get_best_match(query)

        course = self.extract_course(query)

        if not intent or confidence < 0.25:
            response = (
                "🤔 I'm not sure I understood that. Please rephrase your question.\n\n"
                "**You can ask me about:**\n"
                "• 📋 Admission process\n"
                "• 📚 Courses offered\n"
                "• 💰 Fee structure\n"
                "• 📊 Placement records\n"
                "• 🏠 Hostel facilities\n"
                "• 📖 Library facilities\n"
                "• 🏅 Scholarships\n"
                "• 📞 Contact info\n"
                "• 🗺️ Route finding (e.g., *'Find route from Home to Office'*)"
            )
        else:
            response = random.choice(self.knowledge_base[intent]['responses'])

        # Sentiment
        blob  = TextBlob(query)
        score = blob.sentiment.polarity
        sentiment = ('positive' if score > 0.3
                     else 'negative' if score < -0.3
                     else 'neutral')

        return {
            'response':       response,
            'intent':         intent or 'unknown',
            'confidence':     round(confidence, 3),
            'sentiment':      sentiment,
            'sentiment_score': round(score, 3),
            'entities':       {'course': course} if course else {},
            'response_time':  round(time.time() - t0, 3)
        }