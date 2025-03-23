from dataclasses import dataclass, field
import random
from typing import List, Tuple
import os
import sys

# Import paths setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing.ant import Ant
from aco_routing.graph_api import GraphApi
from aco_routing.network import Network


@dataclass
class ACO:
    graph: Network
    # Maximum number of steps an ant is allowed is to take in order to reach the destination
    ant_max_steps: int
    # Number of cycles/waves of search ants to be deployed
    num_iterations: int
    # Indicates if the search ants should spawn at random nodes in the graph
    ant_random_spawn: bool = True
    # Evaporation rate (rho)
    evaporation_rate: float = 0.1
    # Pheromone bias
    alpha: float = 0.7
    # Edge cost bias
    beta: float = 0.3
    # Search ants
    search_ants: List[Ant] = field(default_factory=list)
    # Best path found so far
    best_path: List[str] = field(default_factory=list)
    # Cost of the best path
    best_cost: float = float('inf')

    def __post_init__(self):
        # Initialize the Graph API
        self.graph_api = GraphApi(self.graph, self.evaporation_rate)
        # Initialize all edges of the graph with a pheromone value of 1.0
        for u, v in self.graph.get_edges():
            self.graph_api.set_edge_pheromones(u, v, 1.0)

    def _deploy_forward_search_ants(self) -> None:
        """Deploy forward search ants in the graph"""
        for ant in self.search_ants:
            for _ in range(self.ant_max_steps):
                if ant.reached_destination():
                    ant.is_fit = True
                    break
                ant.take_step()

    def _deploy_backward_search_ants(self) -> None:
        """Deploy fit search ants back towards their source node while dropping pheromones on the path"""
        for ant in self.search_ants:
            if ant.is_fit:
                # Add extra deposit for shorter paths
                ant.deposit_pheromones_on_path()
                
                # Update best path if this one is better
                if ant.path_cost < self.best_cost:
                    self.best_path = ant.path.copy()
                    self.best_cost = ant.path_cost

    def _deploy_search_ants(
        self,
        source: str,
        destination: str,
        num_ants: int,
    ) -> None:
        """Deploy search ants that traverse the graph to find the shortest path

        Args:
            source (str): The source node in the graph
            destination (str): The destination node in the graph
            num_ants (int): The number of ants to be spawned
        """
        # Reset best path tracking
        self.best_path = []
        self.best_cost = float('inf')
        
        for iteration in range(self.num_iterations):
            self.search_ants.clear()

            for _ in range(num_ants):
                spawn_point = source
                if self.ant_random_spawn:
                    spawn_point = random.choice(list(self.graph.nodes()))
                
                ant = Ant(
                    self.graph_api,
                    spawn_point,
                    destination,
                    alpha=self.alpha,
                    beta=self.beta,
                )
                self.search_ants.append(ant)

            self._deploy_forward_search_ants()
            self._deploy_backward_search_ants()
            
            # Gradually increase beta to favor shorter paths in later iterations
            if iteration > self.num_iterations / 2:
                self.beta = min(self.beta * 1.05, 5.0)

    def _deploy_solution_ant(self, source: str, destination: str) -> Ant:
        """Deploy the pheromone-greedy solution to find the shortest path

        Args:
            source (str): The source node in the graph
            destination (str): The destination node in the graph

        Returns:
            Ant: The solution ant with the computed shortest path and cost
        """
        # If we already found a good path with the search ants, use it
        if self.best_path and self.best_path[0] == source and self.best_path[-1] == destination:
            return Ant.from_path(self.graph_api, self.best_path, self.best_cost, is_solution_ant=True)
        
        # Otherwise, create a new solution ant
        ant = Ant(
            self.graph_api,
            source,
            destination,
            is_solution_ant=True,
            # Use higher beta for solution ant to favor shorter paths
            beta=max(self.beta * 2, 3.0)
        )
        
        steps = 0
        solution_max_steps = self.ant_max_steps * 2  # Give solution ant more steps
        
        while not ant.reached_destination() and steps < solution_max_steps:
            ant.take_step()
            steps += 1
            
        if not ant.reached_destination():
            # If solution ant failed but we have a best path, use that instead
            if self.best_path and self.best_path[0] == source and self.best_path[-1] == destination:
                return Ant.from_path(self.graph_api, self.best_path, self.best_cost, is_solution_ant=True)
            
            raise Exception(f"Solution ant could not reach destination after {steps} steps.")
            
        return ant

    def find_path_with_single_destination(
        self,
        source: str,
        destination: str,
        num_ants: int,
    ) -> Tuple[List[str], float]:
        """Finds the shortest path from the source to the destination in the graph

        Args:
            source (str): The source node in the graph
            destination (str): The destination node in the graph
            num_ants (int): The number of search ants to be deployed

        Returns:
            List[str]: The shortest path found by the ants
            float: The cost of the computed shortest path
        """
        # Verify the graph has the required nodes
        if source not in self.graph.nodes():
            raise ValueError(f"Source node {source} not in graph")
        if destination not in self.graph.nodes():
            raise ValueError(f"Destination node {destination} not in graph")
        
        # Do the actual search
        self._deploy_search_ants(
            source,
            destination,
            num_ants,
        )
        solution_ant = self._deploy_solution_ant(source, destination)
        return solution_ant.path, solution_ant.path_cost

    def find_path_with_multiple_destinations(self, source: str, destinations: List[str], num_ants: int = 100) -> Tuple[List[str], float]:
        """Find the shortest path that visits all destinations in a greedy manner.
        
        Args:
            source: The starting node
            destinations: List of destination nodes to visit
            num_ants: The number of ants to use for each path finding
        
        Returns:
            Tuple[List[str], float]: A tuple containing the path and its cost
        """
        # Initialize the combined path with the source node
        combined_path = [source]
        total_cost = 0.0
        
        # Start from the source
        current_source = source
        remaining_destinations = destinations.copy()
        
        # Continue until all destinations are visited
        while remaining_destinations:
            # Find paths to each destination from current_source
            best_path = None
            best_cost = float('inf')
            best_dest = None
            
            for dest in remaining_destinations:
                try:
                    path, cost = self.find_path_with_single_destination(
                        source=current_source,
                        destination=dest,
                        num_ants=num_ants
                    )
                    
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path
                        best_dest = dest
                except Exception:
                    # Continue with other destinations silently
                    continue
            
            # If no path was found to any remaining destination, stop
            if best_path is None:
                raise ValueError("Could not find a path to any of the remaining destinations.")
            
            # Add the path (excluding the first node which is already in the combined path)
            combined_path.extend(best_path[1:])
            total_cost += best_cost
            
            # Update current_source and remove the destination we just reached
            current_source = best_dest
            remaining_destinations.remove(best_dest)
        
        return combined_path, total_cost