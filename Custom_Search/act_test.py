import networkx as nx
from aco_routing import ACO
import re
import sys

sys.path.append("data_reader")

from parser import parse_graph_file
 
# Example usage
file_path = "Data/PathFinder-test.txt"  # Replace with your actual file name
nodes, edges, origin, destinations = parse_graph_file(file_path)


G = nx.DiGraph()

# Add all edges from the edges dictionary to the graph
for (start, end), weight in edges.items():
    G.add_edge(start, end, cost=weight)

aco = ACO(G, ant_max_steps=100, num_iterations=100, evaporation_rate=0.1, alpha=0.7, beta=0.3)

aco_path, aco_cost = aco.find_shortest_path(
    source=origin,
    destination=destinations[0],
    num_ants=300,
)
print("Origin:", origin)
print("Destination:", destinations[0])
print("ACO Path:", aco_path)
print("ACO Cost:", aco_cost)

# Visualize the graph with the shortest path
# aco.graph_api.visualize_graph(
#     shortest_path=aco_path
# )