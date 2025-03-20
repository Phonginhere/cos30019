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

aco = ACO(G, ant_max_steps=200, num_iterations=2000, ant_random_spawn=True)

aco_path, aco_cost = aco.find_shortest_path(
    source=origin,
    destination=destinations[0],
    num_ants=100
)

print("ACO Path:", aco_path)
print("ACO Cost:", aco_cost)