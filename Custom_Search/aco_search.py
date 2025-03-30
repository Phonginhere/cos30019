import os
import sys
import traceback

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing.aco import ACO
from aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))

from parser import parse_graph_file

def main():
    # Get file path from command line argument if provided
    file_path = "Data/PathFinder-test.txt"
    
    try:
        nodes, edges, origin, destinations = parse_graph_file(file_path)
    except Exception as e:
        print(f"Error parsing graph file: {e}")
        traceback.print_exc()
        return

    # Create the graph - optimize memory usage
    G = Network()
    
    # Pre-allocate graph memory
    G.graph = {node: [] for node in nodes}
    G.pos = nodes
    
    # Add edges 
    for (start, end), weight in edges.items():
        G.add_edge(start, end, cost=float(weight))
    
    # Calculate adaptive parametersg
    node_count = G.number_of_nodes()
    
    ant_max_steps = node_count * 2
    iterations = 100
    num_ants = node_count 
    alpha = 3.5
    beta = 2.5
    evaporation_rate = 0.5 # Learning rate
    
    # Initialize ACO with optimized parameters
    aco = ACO(G, 
              ant_max_steps=ant_max_steps,
              num_iterations=iterations, 
              evaporation_rate=evaporation_rate, 
              alpha=alpha, 
              beta=beta, 
              mode=1, # 0: any destination, 1: all destinations, 2: TSP mode (random origin and all destinations)
              log_step=10 # Log every 10 iterations
    )

    aco_path, aco_cost = aco.find_shortest_path(
        source=origin,
        destination=destinations,
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
        aco_path = [node for node in aco_path]
        goal_str = f"[{', '.join(destinations)}]"  # Format destinations consistently
        number_of_nodes = G.number_of_nodes()
        path_str = " ".join(aco_path)
        
        print(f"\"aco_search.py\" CUS2")
        print(f"{goal_str} {number_of_nodes}")
        print(f"{path_str}")
        print(f"{aco_cost}")
        
        aco.graph_api.visualize_graph(aco_path, aco_cost)

if __name__ == "__main__":
    main()