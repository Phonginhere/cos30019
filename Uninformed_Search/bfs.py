import os
import sys

# Set up path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))
from parser import parse_graph_file

# Import the UninformNetwork class
sys.path.append(os.path.join(current_dir, "entity"))
from Uninformed_Search.entity.UninformNetwork import UninformNetwork

# Parse the graph file
file_path = "Data/PathFinder-test.txt"
print("Parsing graph file:", file_path)
nodes, edges, origin, destinations = parse_graph_file(file_path)

# Print goals and number of nodes
print("Goals:", destinations)
print("Number of nodes:", len(nodes))

# Create the UninformNetwork instance
network = UninformNetwork()
network.build_from_data(nodes, edges)

# Find and display the shortest path to any destination
shortest_path, shortest_dest, shortest_weight = network.find_shortest_path_to_destinations(origin, destinations)

# Show the result
if shortest_path:
    print(f"Path: {' -> '.join(map(str, shortest_path))} with total weight {shortest_weight}")
else:
    print("\nNo paths found to any destination.")