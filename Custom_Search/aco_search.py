import networkx as nx
from aco_routing import ACO
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

    # Initialize ACO with parameters
    aco = ACO(G, ant_max_steps=1000, num_iterations=1000, evaporation_rate=0.1, alpha=1, beta=2, ant_random_spawn=False)

    try:
        # Handle single or multiple destinations
        if isinstance(destinations, list) and len(destinations) == 1:
            # For a single destination
            aco_path, aco_cost = aco.find_shortest_path(
                source=origin,
                destination=destinations[0],
                num_ants=1000,
            )
        else:
            # For multiple destinations
            # Check if the method exists
            if hasattr(aco, 'find_path_with_multiple_destinations'):
                aco_path, aco_cost = aco.find_path_with_multiple_destinations(
                    source=origin,
                    destinations=destinations,
                    num_ants=1000
                )
            else:
                # Fallback to finding individual paths
                print("Warning: Multiple destination method not available, finding path to first destination only.")
                aco_path, aco_cost = aco.find_shortest_path(
                    source=origin,
                    destination=destinations[0] if isinstance(destinations, list) else destinations,
                    num_ants=1000
                )
        
        # Output results
        print("Origin:", origin)
        print("Destination(s):", destinations)
        print("ACO Path:", aco_path)
        print("ACO Cost:", aco_cost)
        
        # Visualize the graph with the shortest path
        # Only call visualization methods if they exist
        if hasattr(aco.graph_api, 'visualize_graph'):
            aco.graph_api.visualize_graph(shortest_path=aco_path)
        else:
            print("Path visualization not available")
        
    except Exception as e:
        print(f"Error finding path: {e}")
        # Try to visualize the original graph
        if hasattr(aco.graph_api, 'visualize_original_graph'):
            aco.graph_api.visualize_original_graph()
        else:
            print("Graph visualization not available")
            # Print the graph structure instead
            print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            print(f"Nodes: {list(G.nodes())}")
            print(f"Edges: {list(G.edges())}")

if __name__ == "__main__":
    main()