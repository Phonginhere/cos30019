import networkx as nx
from aco_routing import ACO
import re
import sys

sys.path.append("../data_reader")

from parser import parse_graph_file

# Example usage
file_path = "../Data/PathFinder-test.txt"  # Replace with your actual file name
nodes, edges, origin, destinations = parse_graph_file(file_path)


G = nx.DiGraph()

# Add all edges from the edges dictionary to the graph
for (start, end), weight in edges.items():
    G.add_edge(start, end, cost=weight)

print("Nodes:", G.nodes())
print("EdGes:", G.edges())