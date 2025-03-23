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
    destination: str
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

    @classmethod
    def from_path(cls, graph_api, path, path_cost, is_solution_ant=False):
        """Create an ant with a predefined path
        
        Args:
            graph_api: The graph API instance
            path: The path for the ant
            path_cost: The cost of the path
            is_solution_ant: Whether this is a solution ant
            
        Returns:
            Ant: A new ant with the given path
        """
        ant = cls(
            graph_api=graph_api,
            source=path[0],
            destination=path[-1],
            is_solution_ant=is_solution_ant,
        )
        
        # Set the path and other properties
        ant.path = path.copy()
        ant.current_node = path[-1]
        ant.path_cost = path_cost
        ant.is_fit = True
        
        # Mark all nodes in the path as visited
        ant.visited_nodes = set(path)
        
        return ant

    def __post_init__(self) -> None:
        # Set the spawn node as the current and first node
        self.current_node = self.source
        self.path.append(self.source)

    def reached_destination(self) -> bool:
        """Returns if the ant has reached the destination node in the graph

        Returns:
            bool: returns True if the ant has reached the destination
        """
        return self.current_node == self.destination

    def _get_unvisited_neighbors(self) -> List[str]:
        """Returns a subset of the neighbors of the node which are unvisited

        Returns:
            List[str]: A list of all the unvisited neighbors
        """
        return [
            node
            for node in self.graph_api.get_neighbors(self.current_node)
            if node not in self.visited_nodes
        ]

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
                
            # If the solution ant has no moves and isn't at the destination, we need to backtrack
            if self.is_solution_ant:
                # If we've visited all nodes and can't reach destination, that's a problem
                if len(self.visited_nodes) >= self.graph_api.graph.number_of_nodes():
                    raise Exception(f"No path found from {self.source} to {self.destination}")
                    
                # For the solution ant, try to minimize visited node constraints
                # This allows backtracking to find a path
                if len(self.path) > 1:
                    # Try to go back one step
                    previous = self.path[-2]
                    return previous
            
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
        
        # Pick the next node based on the roulette wheel selection technique
        return utils.roulette_wheel_selection(probabilities)

    def take_step(self) -> None:
        """Compute and update the ant position"""
        # Mark the current node as visited
        self.visited_nodes.add(self.current_node)

        # Pick the next node of the ant
        next_node = self._choose_next_node()

        # Check if ant is stuck at current node or has reached destination
        if not next_node:
            if self.current_node == self.destination:
                self.is_fit = True
            return

        # If backtracking (solution ant only)
        if next_node in self.path:
            # Remove all nodes after the backtrack point
            idx = self.path.index(next_node)
            # Remove path cost for edges we're removing
            for i in range(len(self.path) - 2, idx - 1, -1):
                u, v = self.path[i], self.path[i + 1]
                self.path_cost -= self.graph_api.get_edge_cost(u, v)
            # Truncate path
            self.path = self.path[:idx + 1]
            self.current_node = next_node
            # Remove these nodes from visited set to allow revisiting
            for node in self.visited_nodes.copy():
                if node not in self.path:
                    self.visited_nodes.remove(node)
            return

        # Standard case: add the new node to the path
        self.path.append(next_node)
        self.path_cost += self.graph_api.get_edge_cost(self.current_node, next_node)
        self.current_node = next_node

    def deposit_pheromones_on_path(self) -> None:
        """Updates the pheromones along all the edges in the path"""
        # Avoid division by zero
        deposit_amount = 1.0 / max(self.path_cost, 0.1)
        
        for i in range(len(self.path) - 1):
            u, v = self.path[i], self.path[i + 1]
            self.graph_api.deposit_pheromones(u, v, deposit_amount)