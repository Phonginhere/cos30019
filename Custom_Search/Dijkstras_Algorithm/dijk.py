import os
import sys
import heapq
from collections import defaultdict

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

sys.path.append(os.path.join(parent_dir, "Custom_Search"))
from aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "..", "data_reader"))
from parser import parse_graph_file

file_path = "Data/PathFinder-test.txt"

print("Parsing graph file:", file_path)
nodes, edges, origin, destinations = parse_graph_file(file_path)

# Print goals
print("Goals:", destinations)
# Print number of nodes
print("Number of nodes:", len(nodes))

# Function for Dijkstra's Algorithm

def build_graph(nodes, edges):
    """
    Construct a graph dictionary from nodes and edges.
    
    Parameters:
      nodes - a list of node identifiers
      edges - a dictionary where keys are (src, tgt) tuples and values are weights
      
    Returns:
      A dictionary mapping each node to a list of (neighbor, weight) tuples.
    """
    # Initialize graph with every node (even if no outgoing edges)
    graph = {node: [] for node in nodes}
    
    # Process each edge and add to adjacency list with weight
    for (src, tgt), weight in edges.items():
        # print(f"Edge: {src} -> {tgt}, Cost: {weight}")
        graph[src].append((tgt, weight))
    
    return graph

def dijkstra(graph, start, goals):
    visited = set()
    heap = [(0, start, [start])]
    
    while heap:
        cost, node, path = heapq.heappop(heap)
        
        if node == goals:  # Check if we've reached the goal
            return node, len(path), path, cost
        
        if node in visited:
            continue
        
        visited.add(node)

        for neighbor, edge_cost in graph.get(node, []): # Access the list of tuples directly
            if neighbor not in visited:
                heapq.heappush(heap, (cost + edge_cost, neighbor, path + [neighbor]))
        
    return None, float('inf') 

# Build the graph dictionary from the nodes and edges
graph = build_graph(nodes, edges)

# Example usage of Dijkstra's algorithm
for dest in destinations:
    path = dijkstra(graph, origin, dest)
    if path:
        print(f"Path from {origin} to {dest}: {' -> '.join(map(str, path))}")
    else:
        print(f"No path found from {origin} to {dest}")
