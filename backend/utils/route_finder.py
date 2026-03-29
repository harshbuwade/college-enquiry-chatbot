import heapq
import math
import time
from typing import Dict, List, Tuple, Optional

class Graph:
    """Represents a graph for route finding"""
    
    def __init__(self):
        self.nodes: Dict[str, Tuple[float, float]] = {}  # node: (lat, lon)
        self.edges: Dict[str, Dict[str, float]] = {}    # node: {neighbor: cost}
    
    def add_node(self, node_id: str, lat: float, lon: float):
        """Add a node with coordinates"""
        self.nodes[node_id] = (lat, lon)
        if node_id not in self.edges:
            self.edges[node_id] = {}
    
    def add_edge(self, from_node: str, to_node: str, distance: float):
        """Add a weighted edge between nodes"""
        self.edges[from_node][to_node] = distance
        self.edges[to_node][from_node] = distance  # undirected graph
    
    def get_neighbors(self, node: str) -> Dict[str, float]:
        """Get all neighbors of a node"""
        return self.edges.get(node, {})
    
    def get_coordinates(self, node: str) -> Tuple[float, float]:
        """Get coordinates for a node"""
        return self.nodes.get(node, (0, 0))
    
    def heuristic(self, node: str, goal: str) -> float:
        """Euclidean distance heuristic for A* search"""
        if node not in self.nodes or goal not in self.nodes:
            return 0
        lat1, lon1 = self.nodes[node]
        lat2, lon2 = self.nodes[goal]
        # Simple Euclidean distance (for demo)
        return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


class RouteFinder:
    """Intelligent Route Finder using Heuristic Search"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.performance_stats = {
            'nodes_expanded': 0,
            'execution_time': 0,
            'path_cost': 0
        }
    
    def a_star_search(self, start: str, goal: str) -> Tuple[List[str], float]:
        """
        A* Search Algorithm
        Combines actual cost (g) + heuristic estimate (h)
        """
        start_time = time.time()
        nodes_expanded = 0
        
        # Priority queue: (f_score, current_node, path, g_score)
        open_set = [(0, start, [start], 0)]
        visited = set()
        g_scores = {start: 0}
        
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
    
    def best_first_search(self, start: str, goal: str) -> Tuple[List[str], float]:
        """
        Best First Search Algorithm
        Prioritizes speed over optimality (uses only heuristic)
        """
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
    
    def compare_algorithms(self, start: str, goal: str) -> Dict:
        """Compare A* and Best First Search performance"""
        results = {}
        
        # A* Search
        print(f"\n🔍 Running A* Search from {start} to {goal}...")
        path_a, cost_a = self.a_star_search(start, goal)
        stats_a = self.performance_stats.copy()
        results['a_star'] = {
            'path': path_a,
            'cost': cost_a,
            'nodes_expanded': stats_a['nodes_expanded'],
            'time_ms': stats_a['execution_time']
        }
        print(f"   Path: {' → '.join(path_a)}")
        print(f"   Cost: {cost_a:.2f}")
        print(f"   Nodes Expanded: {stats_a['nodes_expanded']}")
        print(f"   Time: {stats_a['execution_time']:.2f} ms")
        
        # Best First Search
        print(f"\n⚡ Running Best First Search from {start} to {goal}...")
        path_bf, cost_bf = self.best_first_search(start, goal)
        stats_bf = self.performance_stats.copy()
        results['best_first'] = {
            'path': path_bf,
            'cost': cost_bf,
            'nodes_expanded': stats_bf['nodes_expanded'],
            'time_ms': stats_bf['execution_time']
        }
        print(f"   Path: {' → '.join(path_bf)}")
        print(f"   Cost: {cost_bf:.2f}")
        print(f"   Nodes Expanded: {stats_bf['nodes_expanded']}")
        print(f"   Time: {stats_bf['execution_time']:.2f} ms")
        
        return results


def create_sample_graph() -> Graph:
    """Create a sample city map graph for demonstration"""
    g = Graph()
    
    # Add nodes (locations with coordinates)
    nodes = {
        'A': (0, 0),     # Start
        'B': (2, 1),     # Location 1
        'C': (4, 2),     # Location 2
        'D': (1, 3),     # Location 3
        'E': (3, 4),     # Location 4
        'F': (5, 3),     # Location 5
        'G': (6, 5),     # Goal
    }
    
    for node, coords in nodes.items():
        g.add_node(node, coords[0], coords[1])
    
    # Add edges (roads with distances)
    edges = [
        ('A', 'B', 3.5),
        ('A', 'D', 4.2),
        ('B', 'C', 2.8),
        ('B', 'E', 3.0),
        ('C', 'F', 2.5),
        ('C', 'G', 5.0),
        ('D', 'E', 2.0),
        ('E', 'F', 3.2),
        ('E', 'G', 4.5),
        ('F', 'G', 2.0),
    ]
    
    for u, v, w in edges:
        g.add_edge(u, v, w)
    
    return g


# Create API endpoint for the chatbot to expose route finding
def get_route_finder_response(query: str) -> str:
    """Integrate route finder with chatbot"""
    
    if "route" not in query.lower() and "path" not in query.lower():
        return None
    
    graph = create_sample_graph()
    finder = RouteFinder(graph)
    
    # Extract start and goal from query (simplified)
    start = 'A'
    goal = 'G'
    
    # Try to parse from query
    if "from" in query.lower() and "to" in query.lower():
        # Basic parsing - can be enhanced
        parts = query.lower().split()
        for i, part in enumerate(parts):
            if part == "from" and i + 1 < len(parts):
                start = parts[i + 1].upper()
            if part == "to" and i + 1 < len(parts):
                goal = parts[i + 1].upper()
    
    results = finder.compare_algorithms(start, goal)
    
    # Format response
    response = "🗺️ **Intelligent Route Finder Results**\n\n"
    
    response += "📍 **Route from " + start + " to " + goal + "**\n\n"
    
    response += "**A* Search (Optimal Path):**\n"
    response += f"• Path: {' → '.join(results['a_star']['path'])}\n"
    response += f"• Distance: {results['a_star']['cost']:.2f} km\n"
    response += f"• Nodes explored: {results['a_star']['nodes_expanded']}\n"
    response += f"• Computation time: {results['a_star']['time_ms']:.2f} ms\n\n"
    
    response += "**Best First Search (Fast Path):**\n"
    response += f"• Path: {' → '.join(results['best_first']['path'])}\n"
    response += f"• Distance: {results['best_first']['cost']:.2f} km\n"
    response += f"• Nodes explored: {results['best_first']['nodes_expanded']}\n"
    response += f"• Computation time: {results['best_first']['time_ms']:.2f} ms\n\n"
    
    response += "📊 **Analysis:**\n"
    if results['a_star']['cost'] < results['best_first']['cost']:
        response += "• A* Search found the shorter route\n"
    else:
        response += "• Best First Search found the shorter route\n"
    
    if results['a_star']['time_ms'] < results['best_first']['time_ms']:
        response += "• A* Search was faster to compute\n"
    else:
        response += "• Best First Search was faster to compute\n"
    
    response += "\n💡 **Industry Application:** These algorithms are used in navigation apps, logistics optimization, and network routing to find the most efficient paths."
    
    return response