import heapq 
# ---------- INPUT ---------- 
n = int(input("Enter number of nodes: ")) 
heuristic = {} 
print("Enter heuristic value for each node:") 
for _ in range(n): 
    node = input("Node name: ") 
    h = int(input("Heuristic value: ")) 
    heuristic[node] = h 
graph = {} 
for node in heuristic: 
    graph[node] = [] 
e = int(input("Enter number of edges: ")) 
print("Enter edges (from to cost):") 
for _ in range(e): 
    u, v, c = input().split() 
    graph[u].append((v, int(c))) 
start = input("Enter start node: ") 
goal = input("Enter goal node: ") 
# ---------- A* ALGORITHM ---------- 
open_list = [] 
heapq.heappush(open_list, (heuristic[start], start)) 
g_cost = {start: 0} 
parent = {start: None} 

closed_list = set() 
 
while open_list: 
    _, current = heapq.heappop(open_list) 
    if current == goal: 
        break 
    closed_list.add(current) 
    for successor, cost in graph[current]: 
        new_g = g_cost[current] + cost 
        if successor in closed_list and successor in g_cost and g_cost[successor] <= new_g: 
            continue 
        if successor not in g_cost or new_g < g_cost[successor]: 
            g_cost[successor] = new_g 
            f = new_g + heuristic[successor] 
            heapq.heappush(open_list, (f, successor)) 
            parent[successor] = current 
# ---------- OUTPUT ---------- 
path = [] 
node = goal 
while node: 
    path.append(node) 
    node = parent[node] 
path.reverse() 
print("\nPath found:", " -> ".join(path)) 
print("Shortest path cost:", g_cost[goal]) 
