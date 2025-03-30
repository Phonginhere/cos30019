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
    graph_density = edge_count / max_possible_edges
    
    # Calculate average node degree
    avg_degree = edge_count / node_count
    
    # ==== LARGE SCALE OPTIMIZED PARAMETERS ====
    
    # Iterations: Between 300-1000 based on complexity
    problem_complexity = (node_count * 0.7) + (edge_count * 0.3) + (avg_degree * 5)
    
    # Scale iterations in the 300-1000 range based on complexity
    iterations = int(300 + (problem_complexity / 100) * 700)
    iterations = max(300, min(1000, iterations))
    
    # Number of ants: Between node_count and 500
    num_ants = int(node_count + (graph_density * 200) + (node_count * 0.5))
    num_ants = max(node_count, min(500, num_ants))
    
    # Ant max steps: Between node_count and node_count*1.5
    ant_max_steps = int(node_count * (1 + (0.5 * (1 - graph_density))))
    ant_max_steps = max(node_count, min(int(node_count * 1.5), ant_max_steps))
    
    # ==== PHEROMONE PARAMETER TUNING ====
    
    # Calculate edge weight statistics for parameter tuning
    weights = [weight for (_, _), weight in edges.items()]
    weight_variance = sum((w - sum(weights)/len(weights))**2 for w in weights)/len(weights) if weights else 0
    weight_uniformity = weight_variance / (max(weights)**2) if weights and max(weights) > 0 else 0
    
    # EVAPORATION RATE optimization - higher for dense graphs to converge faster
    if graph_density > 0.6:  # Dense graph
        evaporation_rate = 0.2  # Faster convergence for dense graphs
    elif graph_density < 0.2:  # Sparse graph
        evaporation_rate = 0.08  # More exploration for sparse graphs
    else:  # Medium density
        evaporation_rate = 0.15  # Balanced approach
        
    # Adjust for weight distribution
    if weight_uniformity < 0.1:  # Very diverse weights
        evaporation_rate *= 0.8  # Reduce to explore more paths
    elif weight_uniformity > 0.5:  # Similar weights
        evaporation_rate *= 1.2  # Increase to converge faster
        
    # Clamp to reasonable range
    evaporation_rate = max(0.05, min(0.3, evaporation_rate))
    
    # ALPHA (pheromone importance) and BETA (heuristic importance) optimization
    alpha = 1.0  # Medium pheromone influence
    beta = 1.0   # Strong heuristic guidance
    
    # Adjust alpha/beta based on graph size
    if node_count > 30:
        alpha = 0.3  # Less pheromone influence for larger graphs
        beta = 1.2   # More heuristic guidance
    elif node_count < 15:
        alpha = 0.5  # More pheromone for smaller graphs
        beta = 0.8   # Less need for heuristic guidance
    
    # Adjust based on graph density
    if graph_density > 0.7:  # Dense graph
        alpha *= 0.9  # Rely less on pheromones
        beta *= 1.1   # More on distance heuristic
    elif graph_density < 0.2:  # Sparse graph
        alpha *= 1.1  # Need more pheromone guidance
        beta *= 0.9   # Heuristic less reliable in sparse graphs
    
    # Final clamping to ensure values stay in reasonable ranges
    alpha = max(0.5, min(2, alpha))
    beta = max(0.5, min(2, beta))
    
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
    ant_max_steps, iterations, num_ants, evaporation_rate, alpha, beta = calculate_adaptive_parameters(G, destinations, edges)
    print(f"Adaptive Parameters: ant_max_steps={ant_max_steps}, iterations={iterations}, num_ants={num_ants}, evaporation_rate={evaporation_rate}, alpha={alpha}, beta={beta}")
    
    # Initialize ACO with optimized parameters
    aco = ACO(G, 
              ant_max_steps=ant_max_steps,
              num_iterations=iterations, 
              evaporation_rate=evaporation_rate, 
              alpha=alpha, 
              beta=beta, 
              mode=2) # 0: any destination, 1: all destinations, 2: TSP mode (random origin and all destinations)

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