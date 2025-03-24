import os
import sys
import traceback

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

def calculate_adaptive_parameters(graph, destinations, edges):
    """
    Calculate adaptive parameters for ACO algorithm based on graph properties.
    
    Args:
        graph: Network object containing the graph
        destinations: List of destination nodes
        edges: Dictionary of edges and their weights
        
    Returns:
        tuple: (ant_max_steps, iterations, num_ants)
    """
    # Get graph properties
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    
    # Calculate graph density (between 0 and 1)
    max_possible_edges = node_count * (node_count - 1)
    graph_density = edge_count / max_possible_edges if max_possible_edges > 0 else 0
    
    # Calculate average node degree
    avg_degree = edge_count / node_count if node_count > 0 else 0
    
    # Calculate graph diameter estimate (approximate longest path)
    # For connected graphs, diameter is typically proportional to log(node_count)
    # For sparse graphs, it can be higher
    diameter_estimate = int(max(5, min(node_count, 2 * (1 + node_count / max(1, avg_degree)))))
    
    # Scale parameters based on graph properties
    # Adjust ant_max_steps based on diameter and density
    if graph_density < 0.2:  # Very sparse graph
        ant_max_steps = int(min(1000, 5 * diameter_estimate * node_count))
    elif graph_density > 0.7:  # Very dense graph
        ant_max_steps = int(min(500, 2 * diameter_estimate))
    else:  # Medium density
        ant_max_steps = int(min(800, 3 * diameter_estimate))
    
    # Scale iterations based on problem complexity
    if len(destinations) > 1:  # Multiple destinations is harder
        complexity_factor = 1.5
    else:
        complexity_factor = 1.0
        
    iterations = int(min(500, complexity_factor * 10 * (0.5 * node_count + 0.3 * edge_count)))
    
    # Scale num_ants based on node count and edge diversity
    unique_edge_weights = len(set(weight for (_, _), weight in edges.items()))
    num_ants = int(min(300, max(10, 0.8 * node_count + 0.2 * unique_edge_weights * len(destinations))))
    
    # Apply minimum values to ensure algorithm works on small graphs
    ant_max_steps = max(20, ant_max_steps)
    iterations = max(30, iterations)
    num_ants = max(10, num_ants)
    
    # Special case handling for known difficult graph patterns
    if graph_density < 0.1 and node_count > 15:
        # Potentially disconnected graph - increase parameters
        ant_max_steps = int(ant_max_steps * 2)
        iterations = int(iterations * 1.5)
        num_ants = int(num_ants * 1.2)
        
    # Check for too many destinations compared to nodes
    if len(destinations) > node_count / 3:
        # Many destinations - need more exploration
        ant_max_steps = int(ant_max_steps * 1.5)
        iterations = int(iterations * 1.3)
    
    return ant_max_steps, iterations, num_ants

def main():
    # Get file path from command line argument if provided
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Data/PathFinder-test.txt"
    
    # Fixed: Remove duplicate file loading - only load once
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        traceback.print_exc()
        return

    # Ensure origin is a string (not an int)
    if isinstance(origin, int):
        origin = str(origin)
    
    # Convert destinations to a consistent format
    try:
        if isinstance(destinations, int):
            destinations = [str(destinations)]  # Convert int to string
        elif isinstance(destinations, str):
            destinations = [destinations]  # Wrap single string in list
        elif isinstance(destinations, list):
            # Convert any integers in the list to strings
            destinations = [str(d) if isinstance(d, int) else d for d in destinations]
        else:
            # Handle any other unexpected types
            print(f"Warning: Unexpected destinations type: {type(destinations)}", file=sys.stderr)
            try:
                # Try to convert to list
                destinations = [str(d) for d in destinations] if hasattr(destinations, '__iter__') else [str(destinations)]
            except Exception as e:
                print(f"Error converting destinations: {e}", file=sys.stderr)
                destinations = [str(destinations)]  # Last resort
    except Exception as e:
        print(f"Error handling destinations: {e}", file=sys.stderr)
        traceback.print_exc()
        destinations = ['1']  # Default fallback
    

    # Create the graph - optimize memory usage
    G = Network()
    
    # Pre-allocate graph memory
    G.graph = {node: [] for node in nodes}
    
    # Add edges efficiently
    for (start, end), weight in edges.items():
        # Ensure nodes are strings
        start_str = str(start) if isinstance(start, int) else start
        end_str = str(end) if isinstance(end, int) else end
        G.add_edge(start_str, end_str, cost=float(weight))

    # Calculate adaptive parameters
    ant_max_steps, iterations, num_ants = calculate_adaptive_parameters(G, destinations, edges)
    
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
        if len(destinations) > 1:
            # Multiple destinations - order doesn't matter
            aco_path, aco_cost = aco.find_path_with_multiple_destinations(
                source=origin,
                destinations=destinations,
                num_ants=num_ants
            )
        else:
            # Single destination case
            dest = destinations[0]  # Fixed - already ensured to be a list
            aco_path, aco_cost = aco.find_path_with_single_destination(
                source=origin,
                destination=dest,
                num_ants=num_ants
            )
        
        # Output results
        if not aco_path:
            # No path found but no exception thrown
            print(f"\"aco_search.py\" CUS2")
            print(f"[{', '.join(destinations)}] {G.number_of_nodes()}")
            print("No path found")
            print("0.0")
        else:
            # Normal output
            aco_path = [str(node) for node in aco_path]
            goal_str = f"[{', '.join(destinations)}]"  # Format destinations consistently
            number_of_nodes = G.number_of_nodes()
            path_str = " ".join(aco_path)
            
            print(f"\"aco_search.py\" CUS2")
            print(f"{goal_str} {number_of_nodes}")
            print(f"{path_str}")
            print(f"{aco_cost}")
    except Exception as e:
        # Always produce valid output format even on error
        print(f"\"aco_search.py\" CUS2")
        print(f"[{', '.join(destinations)}] {G.number_of_nodes()}")
        print(f"No path found: {str(e).split('.')[0]}")  # First sentence of error only
        print("0.0")
        
        # Print detailed error info to stderr for debugging
        print(f"Error finding path: {e}", file=sys.stderr)
        traceback.print_exc()

if __name__ == "__main__":
    main()