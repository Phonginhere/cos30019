import networkx as nx
from dfs_routing import Dfs
import sys

sys.path.append("data_reader")
try:
    from parser import parse_graph_file
    
except ImportError:
    # Handle the case where the parser module isn't available
    def parse_graph_file(file_path):
        # Simplified example parser
        # You might want to implement a more robust fallback parser here
        print(f"Warning: Using fallback parser for {file_path}")
        # Return some default values for testing
        return ['1', '2', '3', '4', '5'], {('1', '2'): 1, ('2', '3'): 2}, '1', ['5']

def main():
    # Read the graph data from the file
    file_path = "Data/PathFinder-test.txt"  # Replace with your actual file name
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        return

    # Create the graph
    G = nx.DiGraph()
    for (start, end), weight in edges.items():
        G.add_edge(start, end, cost=weight)
        
    dfs = Dfs(G, origin, destinations[0] if isinstance(destinations, list) else destinations)

    
if __name__ == "__main__":
    main()