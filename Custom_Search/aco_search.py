import os
import sys
import traceback
import argparse

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing.aco import ACO
from aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))

from parser import parse_graph_file

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ACO Search Algorithm')
    parser.add_argument('file_path', nargs='?', default="Data/PathFinder-Test.txt",
                        help='Path to the graph file (default: Data/PathFinder-Test.txt)')
    
    # Check if the script was called directly or through search.py
    if len(sys.argv) > 1:
        args = parser.parse_args()
        file_path = args.file_path
    else:
        # Default file path if no arguments provided
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

    # Calculate adaptive parameters
    node_count = G.number_of_nodes()
    
    ant_max_steps = node_count + 1
    iterations = 500 # 500-2000 
    num_ants = node_count
    alpha = 1
    beta = 2
    evaporation_rate = 0.5
    
    # cost_results = []
    # for i in range(1):
    #     # Initialize ACO with optimized parameters
    #     aco = ACO(G, 
    #             ant_max_steps=ant_max_steps,
    #             num_iterations=iterations, 
    #             evaporation_rate=evaporation_rate, 
    #             alpha=alpha, 
    #             beta=beta, 
    #             mode=2, # 0: any destination, 1: all destinations, 2: TSP mode (random origin and all destinations)
    #             log_step=None,
    #             visualize=False,  # Enable visualization
    #             visualization_step=10  # Update visualization every 10 iterations
    #     )

    #     aco_path, aco_cost = aco.find_shortest_path(
    #         source=origin,
    #         destination=destinations,
    #         num_ants=num_ants
    #     )
    #     print(f"Iteration {i+1}:")
    #     print(f"Cost: {aco_cost}")
        
    #     cost_results.append(aco_cost)
        
    # print("Minimum Cost:", min(cost_results))
    # print("Maximum Cost:", max(cost_results))
    # print("Average Cost:", sum(cost_results) / len(cost_results))
        
    # Output results Unit format
    aco = ACO(G, 
        ant_max_steps=ant_max_steps,
        num_iterations=iterations, 
        evaporation_rate=evaporation_rate, 
        alpha=alpha, 
        beta=beta, 
        mode=0, # 0: any destination, 1: all destinations, 2: TSP mode
        log_step=10, # Setting log, Int or None
        visualize=False,  # Enable visualization
        visualization_step=10  # Update visualization every 10 iterations
    )
    aco_path, aco_cost = aco.find_shortest_path(
        source=origin,
        destination=destinations,
        num_ants=num_ants,
    )

    if aco_cost == 0:
        print(f"{file_path} CUS2")
        print(f"[{', '.join(destinations)}] {G.number_of_nodes()}")
        print(f"Destination already reached: Origin {origin} to destination {destinations}")
        print("0.0")
    elif not aco_path:
        # No path found but no exception thrown
        print(f"{file_path} CUS2")
        print(f"[{', '.join(destinations)}] {G.number_of_nodes()}")
        print("No path found")
        print("0.0")
    else:
        # Normal output
        aco_path = [node for node in aco_path]
        goal_str = f"[{', '.join(destinations)}]"  # Format destinations consistently
        number_of_nodes = G.number_of_nodes()
        path_str = " ".join(aco_path)
        
        print(f"{file_path} CUS2")
        print(f"{goal_str} {number_of_nodes}")
        print(f"{path_str}")
        print(f"{aco_cost}")
        
        # Only visualize final result
        aco.graph_api.visualize_graph(aco_path, aco_cost)

if __name__ == "__main__":
    main()
    