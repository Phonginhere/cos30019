from dataclasses import dataclass, field
from typing import Dict, List, Set, Union
import os
import sys

# Import paths setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing import utils
from aco_routing.graph_api import GraphApi

@dataclass
class Ant:
    graph_api: GraphApi
    source: str
    # Change from single string to support multiple destinations
    destination: Union[str, List[str], Set[str]] = field(default_factory=list)
    # Pheromone bias
    alpha: float = 0.7
    # Edge cost bias
    beta: float = 0.3
    # Set of nodes that have been visited by the ant
    visited_nodes: Set = field(default_factory=set)
    # Path taken by the ant so far
    path: List[str] = field(default_factory=list)
    # Cost of the path taken by the ant so far
    path_cost: float = 0.0
    # Indicates if the ant has reached the destination (fit) or not (unfit)
    is_fit: bool = False
    # Indicates if the ant is the pheromone-greedy solution ant
    is_solution_ant: bool = False
    # Track destinations that have been visited
    visited_destinations: Set = field(default_factory=set)
    # Mode to control objection function
    mode: int = 0

    def __post_init__(self) -> None:
        # Set the spawn node as the current and first node
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
        return [node for node in self.graph_api.get_neighbors(self.current_node)
                if node not in visited_set]

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

    def _choose_next_node(self) -> Union[str, None]:
        """Choose the next node to be visited by the ant

        Returns:
            [str, None]: The computed next node to be visited by the ant or None if no possible moves
        """
        unvisited_neighbors = self._get_unvisited_neighbors()

        # Check if ant has no possible nodes to move to
        if len(unvisited_neighbors) == 0:
            # If we reached the destination, it's OK to have no more moves
            if self.current_node == self.destination:
                self.is_fit = True
                return None
            
            return None

        if self.is_solution_ant:
            # The final/solution ant greedily chooses the next node with the highest pheromone value
            best_node = None
            best_pheromone = -1
            
            for neighbor in unvisited_neighbors:
                pheromone = self.graph_api.get_edge_pheromones(self.current_node, neighbor)
                if pheromone > best_pheromone:
                    best_pheromone = pheromone
                    best_node = neighbor
                    
            return best_node

        # For regular ants, use probabilistic selection
        probabilities = self._calculate_edge_probabilities(unvisited_neighbors)
        
        # Check for equal probabilities
        if all(prob == 1.0 / len(unvisited_neighbors) for prob in probabilities.values()):
            return min(prob for prob in probabilities.keys())
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

    def deposit_pheromones_on_path(self) -> None:
        """Updates the pheromones along all the edges in the path"""
        # Avoid division by zero
        deposit_amount = 1.0 / max(self.path_cost, 0.1)
        
        for i in range(len(self.path) - 1):
            u, v = self.path[i], self.path[i + 1]
            self.graph_api.deposit_pheromones(u, v, deposit_amount)