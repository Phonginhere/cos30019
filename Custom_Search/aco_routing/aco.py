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


class ACO:
    def __init__(
        self,
        graph: Network,
        ant_max_steps: int,
        num_iterations: int,
        evaporation_rate: float = 0.1,
        alpha: float = 0.7,
        beta: float = 0.3,
        mode: int = 0,
        min_scaling_factor: float = 0.01,
        log_step : int= None,
    ):
        """Initialize the ACO (Ant Colony Optimization) algorithm.
        
        Args:
            graph: Network object containing the graph structure
            ant_max_steps: Maximum number of steps an ant is allowed to take
            num_iterations: Number of cycles/waves of search ants to be deployed
            evaporation_rate: Rate at which pheromones evaporate (0-1)
            alpha: Pheromone bias (importance of pheromone trails)
            beta: Edge cost bias (importance of shorter paths)
            mode: Search mode (0: find any destination, 1: find all destinations, 2: TSP mode)
            min_scaling_factor: Minimum pheromone scaling factor (0-1)
            log_step: Number of iterations between logs
        """
        # Store all parameters
        self.graph = graph
        self.ant_max_steps = ant_max_steps
        self.num_iterations = num_iterations
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.mode = mode
        self.min_scaling_factor = min_scaling_factor
        self.log_step = log_step
        
        # Initialize other fields
        self.search_ants = []
        self.best_path = []
        self.best_path_cost = float("inf")
        
        # Initialize gradient descent parameters
        self.gt = 0.0 # Gradient
        self.acc = 0.0 # Accumulated gradient
        self.d_acc = 0.0 # Delta accumulated gradient
        
        # Initialize the Graph API
        self.graph_api = GraphApi(self.graph, self.evaporation_rate)
        
        # Initialize all edges of the graph with a stochastic pheromone value and delta pheromone of 0.0
        max_temp = 1.0
        min_temp = max_temp * self.min_scaling_factor
        k = 0.5 # control distribution
        for u, v in self.graph.get_edges():
            r = random.uniform(min_temp, max_temp) # Random pheromone value between 0.1 and 1.0
            self.graph_api.set_edge_pheromones(u, v, max_temp - k * r * (max_temp-min_temp)) # Stochastic pheromone value
            self.graph_api.set_edge_delta_pheromones(u, v, 0.0)

    def _deploy_forward_search_ants(self) -> float:
        iteration_best_path_cost = float("inf")
        for ant in self.search_ants:
            # Process each ant until it reaches destination or max steps
            for _ in range(self.ant_max_steps):
                if ant.reached_destination():
                    ant.is_fit = True
                    if ant.path_cost <= self.best_path_cost:
                        self.best_path = ant.path.copy()
                        self.best_path_cost = ant.path_cost
                    if ant.path_cost <= iteration_best_path_cost:
                        iteration_best_path_cost = ant.path_cost
                    break
                ant.take_step()
        print(f"Best path cost in iteration: {iteration_best_path_cost:.2f}")
        return iteration_best_path_cost
            
    def _deploy_backward_search_ants(self, iteration, num_ants, iteration_best_path_cost) -> (float, float):
        # Incase no fit ant
        max_pheromone = 0.0
        min_pheromone = 0.0
        for ant in self.search_ants:
            if ant.is_fit and ant.path_cost <= iteration_best_path_cost:
                # Max Min Ant System (MMAS) pheromone update
                if float(iteration) / float(self.num_iterations) < 0.75: # Both local and global best can update pheromones
                    ant.deposit_pheromones_on_path(elitist_param = 0) # Local pheromone update no elitist

                    if ant.path_cost == self.best_path_cost:
                        ant.deposit_pheromones_on_path(elitist_param = 0.2) # Elitist pheromone update

                    max_pheromone = num_ants * self.graph_api.pheromone_deposit_weight/ant.path_cost
                else:
                    # Only global best can update pheromones
                    self.graph_api.deposit_pheromones_for_path(self.best_path)
                    max_pheromone = num_ants * self.graph_api.pheromone_deposit_weight/self.best_path_cost
                min_pheromone = self.min_scaling_factor * max_pheromone
        return max_pheromone, min_pheromone
                
    def _deploy_search_ants(self, source: str, destination: str, num_ants: int) -> None:
        for iteration in range(self.num_iterations):
            # Clear previous ants
            self.search_ants.clear()
            
            # Create new ants
            for _ in range(num_ants):
                if self.mode == 2:  # TSP mode
                    # For TSP, randomly select a spawn point
                    spawn_point = random.choice(list(self.graph.nodes()))
                    
                    # All nodes are potential destinations in TSP
                    all_nodes = list(self.graph.nodes())
                    
                    # Create ant starting at random node
                    ant = Ant(
                        self.graph_api,
                        spawn_point,  # Random spawn
                        all_nodes,    # All nodes are destinations
                        alpha=self.alpha,
                        beta=self.beta,
                        mode=self.mode
                    )
                    self.search_ants.append(ant)
                else:
                    spawn_point = source
                    ant = Ant(
                        self.graph_api,
                        spawn_point,
                        destination,
                        alpha=self.alpha,
                        beta=self.beta,
                        mode=self.mode
                    )
                    self.search_ants.append(ant)

            # Rest of method remains the same
            iteration_best_path_cost = self._deploy_forward_search_ants()
            max_pheromon, min_pheromon = self._deploy_backward_search_ants(iteration, num_ants, iteration_best_path_cost)        
            
            # update pheromones after each iteration
            self.acc, self.d_acc = self.graph_api.update_pheromones(max_pheromon, min_pheromon, self.acc, self.d_acc)
            
            # Logging 
            if self.log_step != None and ((iteration + 1) % self.log_step == 0):
                print(f"Iteration {iteration + 1}/{self.num_iterations} completed. Best path cost: {self.best_path_cost:.2f}")

    def find_shortest_path(
        self,
        source: str,
        destination: str,
        num_ants: int,
    ) -> Tuple[List[str], float]:
        """Finds the shortest path according to the current mode
        
        In TSP mode (2): Finds a tour that visits all nodes once and returns to source
        """
        # Verify the graph has the required nodes
        if source not in self.graph.nodes():
            raise ValueError(f"Source node {source} not in graph")
        
        if self.mode != 2:  # Only check destination for non-TSP modes
            for dest in destination:
                if dest not in self.graph.nodes():
                    raise ValueError(f"Destination node {dest} not in graph")
        
        # Reset best path and cost
        self.best_path = []
        self.best_path_cost = float("inf")
        
        # Do the actual search
        self._deploy_search_ants(
            source,
            destination,
            num_ants,
        )
        
        # For TSP mode, validate the path includes all nodes
        if self.mode == 2 and self.best_path:
            all_nodes = set(self.graph.nodes())
            path_nodes = set(self.best_path)
            
            # Check for missing nodes
            missing_nodes = all_nodes - path_nodes
            if missing_nodes:
                print(f"Warning: Current best TSP tour is missing nodes: {missing_nodes}")
                
                # If we found any valid path, ensure source is last node
                if self.best_path and self.best_path[-1] != self.best_path[0]:
                    # Ensure tour returns to starting point
                    self.best_path.append(self.best_path[0])
        return self.best_path, self.best_path_cost