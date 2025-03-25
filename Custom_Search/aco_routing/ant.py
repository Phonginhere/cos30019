from typing import Dict, List, Set, Union
import os
import sys

# Import paths setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing import utils
from aco_routing.graph_api import GraphApi

class Ant:
    def __init__(
        self,
        graph_api: GraphApi,
        source: str,
        destination=None,  # Union[str, List[str], Set[str]]
        alpha: float = 0.7,
        beta: float = 0.3,
        is_fit: bool = False,
        is_solution_ant: bool = False,
        mode: int = 0,
        node_order: Dict = None
    ):
        """Initialize the ant with required parameters
        
        Args:
            graph_api: The graph API for accessing the graph
            source: The source node
            destination: The destination(s) - can be string, list, or set
            alpha: Pheromone bias (default 0.7)
            beta: Edge cost bias (default 0.3)
            is_fit: Whether the ant has reached all destinations
            is_solution_ant: Whether this is a solution ant using highest pheromones
            mode: 0=find any destination, 1=find all destinations
            node_order: Dict mapping nodes to their original order for tiebreaking
        """
        self.graph_api = graph_api
        self.source = source
        self.destination = destination if destination is not None else []
        self.alpha = alpha
        self.beta = beta
        self.visited_nodes = set()
        self.path = []
        self.path_cost = 0.0
        self.is_fit = is_fit
        self.is_solution_ant = is_solution_ant
        self.visited_destinations = set()
        self.mode = mode
        self.node_order = node_order if node_order else {}
        
        # Initialize the ant's state
        self.current_node = self.source
        self.path.append(self.source)
        
        # Convert destination to set for efficient lookups
        if isinstance(self.destination, str):
            self.destination_set = {self.destination}
        elif isinstance(self.destination, list):
            self.destination_set = set(self.destination)
        else:
            self.destination_set = self.destination
            
        # Initialize visited destinations
        self.visited_destinations = set()
        if self.current_node in self.destination_set:
            self.visited_destinations.add(self.current_node)

    def reached_destination(self) -> bool:
        """Returns if the ant has reached all specified destinations
        
        For single destination: returns True when current node equals destination
        For multiple destinations: returns True when all destinations have been visited
        
        Returns:
            bool: True if all destinations have been reached
        """
        if not hasattr(self, 'destination_set'):
            # Handle legacy code where destination might be a string
            if isinstance(self.destination, str):
                return self.current_node == self.destination
            else:
                self.destination_set = set(self.destination) if isinstance(self.destination, list) else self.destination
                self.visited_destinations = set()
                
        # Update visited destinations
        if self.current_node in self.destination_set:
            self.visited_destinations.add(self.current_node)
            
        # Check if all destinations have been visited
        if self.mode == 0:
            return len(self.visited_destinations) > 0
        else:
            return self.visited_destinations == self.destination_set

    def _get_unvisited_neighbors(self) -> List[str]:
        """Get unvisited neighbors with optimized set lookup"""
        # Use a set for faster membership testing
        visited_set = self.visited_nodes
        
        # Use list comprehension with faster set lookup
        neighbors = [node for node in self.graph_api.get_neighbors(self.current_node)
                    if node not in visited_set]
                    
        # If node_order is available, use it to sort neighbors
        if self.node_order:
            # Sort by original file order when ties need to be broken
            neighbors.sort(key=lambda x: self.node_order.get(x, float('inf')))
            
        return neighbors

    def _compute_all_edges_desirability(
        self,
        unvisited_neighbors: List[str],
    ) -> float:
        """Computes the denominator of the transition probability equation for the ant

        Args:
            unvisited_neighbors (List[str]): All unvisited neighbors of the current node

        Returns:
            float: The summation of all the outgoing edges (to unvisited nodes) from the current node
        """
        total = 0.0
        for neighbor in unvisited_neighbors:
            edge_pheromones = self.graph_api.get_edge_pheromones(
                self.current_node, neighbor
            )
            edge_cost = self.graph_api.get_edge_cost(self.current_node, neighbor)
            # Avoid division by zero
            if edge_cost == 0:
                edge_cost = 0.001  # Small value instead of zero
                
            total += utils.compute_edge_desirability(
                edge_pheromones, edge_cost, self.alpha, self.beta
            )

        return total

    def _calculate_edge_probabilities(
        self, unvisited_neighbors: List[str]
    ) -> Dict[str, float]:
        """Computes the transition probabilities of all the edges from the current node

        Args:
            unvisited_neighbors (List[str]): A list of unvisited neighbors of the current node

        Returns:
            Dict[str, float]: A dictionary mapping nodes to their transition probabilities
        """
        probabilities: Dict[str, float] = {}

        all_edges_desirability = self._compute_all_edges_desirability(
            unvisited_neighbors
        )
        
        # Guard against division by zero
        if all_edges_desirability == 0:
            # Equal probability for all neighbors
            equal_prob = 1.0 / len(unvisited_neighbors) if unvisited_neighbors else 0
            return {neighbor: equal_prob for neighbor in unvisited_neighbors}

        for neighbor in unvisited_neighbors:
            edge_pheromones = self.graph_api.get_edge_pheromones(
                self.current_node, neighbor
            )
            edge_cost = self.graph_api.get_edge_cost(self.current_node, neighbor)

            # Avoid division by zero
            if edge_cost == 0:
                edge_cost = 0.001  # Small value instead of zero

            current_edge_desirability = utils.compute_edge_desirability(
                edge_pheromones, edge_cost, self.alpha, self.beta
            )
            probabilities[neighbor] = current_edge_desirability / all_edges_desirability

        return probabilities

    def _break_ties_by_node_order(self, nodes):
        """Break ties based on node ordering when probabilities are equal"""
        if self.node_order:
            # Use original file order if available
            return min(nodes, key=lambda x: self.node_order.get(x, float('inf')))
        
        # Fallback to numeric ordering if node_order not available
        try:
            return min(nodes, key=lambda x: int(x))
        except ValueError:
            return min(nodes)  # Lexicographic order for non-numeric

    def _choose_next_node(self) -> Union[str, None]:
        """Choose the next node to be visited by the ant

        Returns:
            [str, None]: The computed next node to be visited by the ant or None if no possible moves
        """
        unvisited_neighbors = self._get_unvisited_neighbors()

        # Check if ant has no possible nodes to move to
        if len(unvisited_neighbors) == 0:
            # If we reached the destination, it's OK to have no more moves
            if self.reached_destination():
                self.is_fit = True
            return None

        if self.is_solution_ant:
            # The final/solution ant greedily chooses the next node with the highest pheromone value
            if not unvisited_neighbors:
                return None
                
            # Group neighbors by pheromone value
            neighbors_by_pheromone = {}
            for neighbor in unvisited_neighbors:
                pheromone = self.graph_api.get_edge_pheromones(self.current_node, neighbor)
                if pheromone not in neighbors_by_pheromone:
                    neighbors_by_pheromone[pheromone] = []
                neighbors_by_pheromone[pheromone].append(neighbor)
            
            # Find highest pheromone value
            best_pheromone = max(neighbors_by_pheromone.keys())
            
            # If multiple nodes have same pheromone, break tie by node order
            tied_nodes = neighbors_by_pheromone[best_pheromone]
            if len(tied_nodes) > 1:
                return self._break_ties_by_node_order(tied_nodes)
            else:
                return tied_nodes[0]

        # For regular ants, use probabilistic selection
        probabilities = self._calculate_edge_probabilities(unvisited_neighbors)
        
        # Check for equal probabilities
        values = list(probabilities.values())
        if len(values) > 0 and all(abs(v - values[0]) < 1e-10 for v in values):
            # All probabilities are equal (within floating point tolerance)
            return self._break_ties_by_node_order(list(probabilities.keys()))
        else:
            # Pick the next node based on the roulette wheel selection technique
            return utils.roulette_wheel_selection(probabilities)

    def take_step(self) -> None:
        """Compute and update the ant position"""
        # Mark the current node as visited
        self.visited_nodes.add(self.current_node)
        
        # Update visited destinations
        if self.current_node in self.destination_set:
            self.visited_destinations.add(self.current_node)

        # Pick the next node of the ant
        next_node = self._choose_next_node()

        # Check if ant is stuck at current node or has reached all destinations
        if not next_node:
            if self.reached_destination():
                self.is_fit = True
            return

        # Standard case: add the new node to the path
        self.path.append(next_node)
        self.path_cost += self.graph_api.get_edge_cost(self.current_node, next_node)
        self.current_node = next_node
        
        # Update visited_destinations if we've reached a destination
        if self.current_node in self.destination_set:
            self.visited_destinations.add(self.current_node)
            # If mode is 0 (any destination), mark as fit immediately when reaching a destination
            if self.mode == 0:
                self.is_fit = True

    def deposit_pheromones_on_path(self) -> None:
        """Updates the pheromones along all the edges in the path"""
        # Avoid division by zero
        deposit_amount = 1.0 / max(self.path_cost, 0.1)
        
        for i in range(len(self.path) - 1):
            u, v = self.path[i], self.path[i + 1]
            self.graph_api.deposit_pheromones(u, v, deposit_amount)