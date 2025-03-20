# cos30019
Intro to AI with team

### Uninformed Search: 
1. BFS - Phong
2. DFS - Pink

### Informed Search
1. Greedy best-first - Tuan
2. A "Star" - Tuan

### Custom Search
1. ACO - Pink
2. Uniform Search - Phong

### How to use data_reader
import sys

sys.path.append("../data_reader")

from parser import parse_graph_file

# Example usage
file_path = "../Data/PathFinder-test.txt"  # Replace with your actual file name
nodes, edges, origin, destinations = parse_graph_file(file_path)

This will return nodes and edges as dictionary, origin as integer and destinations as list of integer
