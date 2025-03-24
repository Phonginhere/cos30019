import os
import sys

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import directly without Custom_Search prefix since we're already in that directory
from aco_routing.aco import ACO
from aco_routing.network import Network

# For data parser
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))
try:
    from parser import parse_graph_file
except ImportError:
    # Handle the case where the parser module isn't available
    def parse_graph_file(file_path):
        # Simplified example parser
        nodes = ['1', '2', '3', '4', '5']
        edges = {
            ('1', '2'): 1, 
            ('2', '3'): 2, 
            ('3', '4'): 1,
            ('4', '5'): 3,
            ('1', '5'): 10,  # Direct but longer path
            ('2', '5'): 8    # Add direct path from 2 to 5
        }
        return nodes, edges, '1', ['5']

def main():
    # Get file path from command line argument if provided
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Data/PathFinder-test.txt"
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        return
    
    # Read the graph data from the file
    file_path = "Data/PathFinder-test.txt"
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        return

    # Create the graph - optimize memory usage
    G = Network()
    
    # Pre-allocate graph memory
    G.graph = {node: [] for node in nodes}
    
    # Add edges efficiently
    for (start, end), weight in edges.items():
        G.add_edge(start, end, cost=weight)

    # Optimize parameters based on graph size
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    
    # Scale parameters to problem size
    ant_max_steps = min(250, 75 * node_count)  # Limit steps based on graph size
    iterations = min(200, 150 * node_count)   # Limit iterations based on graph size
    num_ants = min(100, 40 * node_count)      # Scale ant count to graph size
    
    # Initialize ACO with optimized parameters
    aco = ACO(G, 
              ant_max_steps=ant_max_steps,
              num_iterations=iterations, 
              evaporation_rate=0.1, 
              alpha=1, 
              beta=2, 
              ant_random_spawn=False)

    try:
        # Check if multiple destinations need to be visited
        if isinstance(destinations, list) and len(destinations) > 1:
            # Multiple destinations - order doesn't matter
            aco_path, aco_cost = aco.find_path_with_multiple_destinations(
                source=origin,
                destinations=destinations,
                num_ants=num_ants
            )
        else:
            # Single destination case
            dest = destinations[0] if isinstance(destinations, list) else destinations
            aco_path, aco_cost = aco.find_path_with_single_destination(
                source=origin,
                destination=dest,
                num_ants=num_ants
            )
        
        # Output results
        aco_path = [str(node) for node in aco_path]
        goal = destinations
        number_of_nodes = G.number_of_nodes()
        path_str = " ".join(aco_path)
        
        print(f"\"aco_search.py\" CUS2")
        print(f"{goal} {number_of_nodes}")
        print(f"{path_str}")
        # print(f"{aco_cost}")
    except Exception as e:
        print(f"Error finding path: {e}")

if __name__ == "__main__":
    main()