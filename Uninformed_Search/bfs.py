import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

sys.path.append(os.path.join(parent_dir, "Custom_Search"))
from Custom_Search.aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))
from parser import parse_graph_file

file_path = "Data/PathFinder-test.txt"

print("Parsing graph file:", file_path)
nodes, edges, origin, destinations = parse_graph_file(file_path)

# Functions for BFS

def bfs_paths(network, start_node, target_node=None):
    """
    BFS with path tracking.
    
    Returns parent dictionary if no target specified,
    or path to target if specified.
    """
    queue = [start_node]
    parent = {start_node: None}
    
    while queue and (target_node is None or target_node not in parent):
        current = queue.pop(0)
        
        for neighbor in network.neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
    
    return parent

def bfs(network, start_node):
    """
    Perform breadth-first search on the network.
    
    Args:
        network: Your Network object
        start_node: Starting node for BFS
        
    Returns:
        visited: Set of visited nodes
    """
    queue = [start_node]
    visited = {start_node}
    
    while queue:
        current = queue.pop(0)
        
        for neighbor in network.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return visited

# Create a directed graph
G = Network()

# Pre-allocate graph memory
G.graph = {node: [] for node in nodes}
G.pos = nodes

# Add edges
for (start, end), weight in edges.items():
    G.add_edge(start, end, weight=float(weight))
    

print(G.graph)
print(G.pos)
print(G.edges)

# Replace this section:

# Perform Breadth-First Search (BFS) from the origin node
print("BFS Traversal from origin", origin, ":")
visited_nodes = bfs(G, origin)
print(list(visited_nodes))

# Perform Depth-First Search (DFS) from the origin node
print("\nDFS Traversal from origin", origin, ":")
# You would need to create a separate dfs function - for now this is a placeholder
# dfs_nodes = dfs(G, origin)
# print(dfs_nodes)

# Check reachability and show the reachable path(s)
print("Reachability and path(s) from origin", origin, ":")
for dest in destinations:
    # Use BFS to determine if there's a path and find it
    parent_dict = bfs_paths(G, origin, dest)
    if dest in parent_dict:
        # Reconstruct the path
        path = []
        current = dest
        while current is not None:
            path.append(current)
            current = parent_dict[current]
        path.reverse()
        print("Destination", dest, "is reachable from", origin, "via the path:", path)
    else:
        print("Destination", dest, "is NOT reachable from", origin)



