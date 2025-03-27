import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Custom_Search.aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))
from parser import parse_graph_file

file_path = "Data/PathFinder-test.txt"


nodes, edges, origin, destinations = parse_graph_file(file_path)

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

# # Perform Breadth-First Search (BFS) from the origin node
# print("BFS Traversal from origin", origin, ":")
# bfs_tree = nx.bfs_tree(G, origin)
# bfs_nodes = list(bfs_tree.nodes())
# print(bfs_nodes)

# # Perform Depth-First Search (DFS) from the origin node
# print("\nDFS Traversal from origin", origin, ":")
# dfs_nodes = list(nx.dfs_preorder_nodes(G, origin))
# print(dfs_nodes)

# # Check reachability and show the reachable path(s)
# print("Reachability and path(s) from origin", origin, ":")
# for dest in destinations:
#     if nx.has_path(G, origin, dest):
#         # Get one shortest path from the origin to the destination
#         path = nx.shortest_path(G, source=origin, target=dest)
#         print("Destination", dest, "is reachable from", origin, "via the path:", path)
#     else:
#         print("Destination", dest, "is NOT reachable from", origin)
