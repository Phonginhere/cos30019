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
    # Read the graph data from the file
    file_path = "Data/PathFinder-test.txt"  # Replace with your actual file name
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        return

    # Create the graph using our custom Network class
    G = Network()
    
    # Add all nodes first
    for node in nodes:
        if node not in G.graph:
            G.graph[node] = []
    
    # Then add all edges with weights
    for (start, end), weight in edges.items():
        G.add_edge(start, end, cost=weight)

    # Initialize ACO with parameters
    aco = ACO(G, ant_max_steps=500, num_iterations=200, evaporation_rate=0.1, alpha=1, beta=2, ant_random_spawn=False)

    try:
        # Handle single or multiple destinations
        if isinstance(destinations, list) and len(destinations) == 1:
            # For a single destination
            aco_path, aco_cost = aco.find_path_with_single_destination(
                source=origin,
                destination=destinations[0],
                num_ants=1000,
            )
        else:
            # For multiple destinations
            if hasattr(aco, 'find_path_with_multiple_destinations'):
                aco_path, aco_cost = aco.find_path_with_multiple_destinations(
                    source=origin,
                    destinations=destinations,
                    num_ants=1000
                )
            else:
                # Fallback to finding individual paths
                aco_path, aco_cost = aco.find_path_with_single_destination(
                    source=origin,
                    destination=destinations[0] if isinstance(destinations, list) else destinations,
                    num_ants=1000
                )
        
        # Convert all path nodes to strings (in case any are integers)
        aco_path = [str(node) for node in aco_path]
        
        # Output results in the required format
        goal = destinations[0] if isinstance(destinations, list) else destinations
        number_of_nodes = G.number_of_nodes()
        path_str = " ".join(aco_path)
        
        print(f"\"aco_search.py\" CUS2")
        print(f"{goal} {number_of_nodes}")
        print(f"{path_str}")
        
        # Visualization code - uncomment to use
        try:
            # Visualize the path if needed
            aco.graph_api.visualize_graph(shortest_path=aco_path, shortest_path_cost=aco_cost)
            
            # Visualize the original graph structure
            # aco.graph_api.visualize_original_graph()
        except Exception as e:
            # This way, visualization errors won't affect your required output
            print(f"Visualization error: {e}")
        
    except Exception as e:
        print(f"Error finding path: {e}")

if __name__ == "__main__":
    main()