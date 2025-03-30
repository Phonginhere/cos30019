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

def calculate_adaptive_parameters(graph, destinations, edges):
    """
    Calculate adaptive parameters for ACO algorithm based on graph properties.
    
    Args:
        graph: Network object containing the graph
        destinations: List of destination nodes
        edges: Dictionary of edges and their weights
        
    Returns:
        tuple: (ant_max_steps, iterations, num_ants, evaporation_rate, alpha, beta)
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
    diameter_estimate = int(max(5, min(node_count // 2, 2 * (1 + node_count / max(1, avg_degree)))))
    
    # Scale parameters based on graph properties - REDUCED VALUES
    # Adjust ant_max_steps based on diameter and density
    if graph_density < 0.2:  # Very sparse graph
        ant_max_steps = int(min(300, 20 * diameter_estimate))
    elif graph_density > 0.7:  # Very dense graph
        ant_max_steps = int(min(150, 15 * diameter_estimate))
    else:  # Medium density
        ant_max_steps = int(min(200, 18 * diameter_estimate))
    
    # Scale iterations based on problem complexity - REDUCED VALUES
    if len(destinations) > 1:  # Multiple destinations is harder
        complexity_factor = 1.2
    else:
        complexity_factor = 1.0
        
    iterations = int(min(100, complexity_factor * 5 * (0.3 * node_count + 0.1 * edge_count)))
    
    # Scale num_ants based on node count and edge diversity - REDUCED VALUES
    unique_edge_weights = len(set(weight for (_, _), weight in edges.items()))
    num_ants = int(min(80, max(10, node_count + 3 * unique_edge_weights * len(destinations))))
    
    # Apply minimum values to ensure algorithm works on small graphs
    ant_max_steps = max(20, ant_max_steps)
    iterations = max(15, iterations)
    num_ants = max(10, num_ants)
    
    # Special case handling for known difficult graph patterns - REDUCED MULTIPLIERS
    if graph_density < 0.1 and node_count > 15:
        # Potentially disconnected graph - increase parameters
        ant_max_steps = int(ant_max_steps * 1.3)
        iterations = int(iterations * 1.2)
        num_ants = int(num_ants * 1.1)
        
    # Check for too many destinations compared to nodes
    if len(destinations) > node_count / 3:
        # Many destinations - need more exploration
        ant_max_steps = int(ant_max_steps * 1.2)
        iterations = int(iterations * 1.1)
    
    # Calculate edge weight statistics for parameter tuning
    weights = [weight for (_, _), weight in edges.items()]
    weight_range = max(weights) - min(weights) if weights else 0
    weight_variance = sum((w - sum(weights)/len(weights))**2 for w in weights)/len(weights) if weights else 0
    weight_uniformity = weight_variance / (max(weights)**2) if weights and max(weights) > 0 else 0
    
    # EVAPORATION RATE optimization
    if graph_density > 0.6:  # Dense graph
        evaporation_rate = 0.15  # Faster convergence for dense graphs
    elif graph_density < 0.2:  # Sparse graph
        evaporation_rate = 0.05  # More exploration for sparse graphs
    else:  # Medium density
        evaporation_rate = 0.1  # Balanced approach
        
    # Adjust for weight distribution
    if weight_uniformity < 0.1:  # Very diverse weights
        evaporation_rate *= 0.8  # Reduce to explore more paths
    elif weight_uniformity > 0.5:  # Similar weights
        evaporation_rate *= 1.2  # Increase to converge faster
        
    # Clamp to reasonable range
    evaporation_rate = max(0.01, min(0.3, evaporation_rate))
    
    # ALPHA (pheromone importance) and BETA (heuristic importance) optimization
    # REBALANCED to give beta more influence
    if node_count > 25 or len(destinations) > 5:
        alpha = 0.3  # REDUCED from 0.6
        beta = 1.0   # Higher beta for better heuristic guidance
    elif node_count < 10 and len(destinations) <= 2:
        alpha = 0.1  # Less pheromone influence for simple problems
        beta = 0.8   # Still maintain good heuristic guidance
    else:
        alpha = 0.2  # REDUCED from 0.3
        beta = 0.9   # Higher beta for better path finding
    
    # Adjust alpha/beta based on graph density
    if graph_density > 0.7:
        alpha *= 0.9  # Dense graphs benefit from more greedy approaches
        beta *= 1.1   # Increase heuristic importance in dense graphs
    
    # Adjust beta based on weight distribution
    if weight_range > 10 * min(weights) if weights and min(weights) > 0 else False:
        beta = max(beta, 1.2)  # High weight variance - rely more on heuristic
    elif weight_uniformity > 0.7:  # Very uniform weights
        beta = min(beta, 0.7)  # Heuristic provides less useful information
    
    # Special cases - REBALANCED
    if len(destinations) == 1 and node_count > 30:
        # Single destination in large graph - balance exploration and exploitation
        evaporation_rate = max(0.05, evaporation_rate * 0.8)
        alpha = min(0.4, alpha * 1.1)  # Cap at reasonable value
        beta = max(0.8, beta * 1.1)     # Ensure sufficient heuristic influence
    
    # Ensure alpha is always lower than beta for better path finding
    if alpha >= beta:
        beta = alpha * 1.5
    
    # Hard caps to prevent extreme values
    ant_max_steps = min(300, ant_max_steps)
    iterations = min(100, iterations)
    num_ants = min(100, num_ants)
    alpha = min(0.5, alpha)
    beta = min(1.5, max(0.5, beta))
    
    return ant_max_steps, iterations, num_ants, evaporation_rate, alpha, beta

def main():
    # Get file path from command line argument if provided
    file_path = sys.argv[1] if len(sys.argv) > 1 else "Data/PathFinder-test.txt"
    
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
    # ant_max_steps, iterations, num_ants, evaporation_rate, alpha, beta = calculate_adaptive_parameters(G, destinations, edges)
    ant_max_steps = 200
    iterations = 500
    num_ants = 250
    evaporation_rate = 0.1
    alpha = 1
    beta = 2
    
    print(f"Adaptive parameters: ant_max_steps={ant_max_steps}, iterations={iterations}, num_ants={num_ants}")
    print(f"ACO tuning: evaporation_rate={evaporation_rate:.2f}, alpha={alpha:.2f}, beta={beta:.2f}")
    # Initialize ACO with optimized parameters
    aco = ACO(G, 
              ant_max_steps=ant_max_steps,
              num_iterations=iterations, 
              evaporation_rate=evaporation_rate, 
              alpha=alpha, 
              beta=beta, 
              mode=1, 
              ant_random_spawn=False) # Parallize optimization not really useful for starting from a single node and reach multiple destinations

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