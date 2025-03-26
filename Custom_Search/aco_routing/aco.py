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
        ant_random_spawn: bool = True,
        evaporation_rate: float = 0.1,
        alpha: float = 0.7,
        beta: float = 0.3,
        mode: int = 0
    ):
        """Initialize the ACO (Ant Colony Optimization) algorithm.
        
        Args:
            graph: Network object containing the graph structure
            ant_max_steps: Maximum number of steps an ant is allowed to take
            num_iterations: Number of cycles/waves of search ants to be deployed
            ant_random_spawn: Indicates if search ants should spawn at random nodes
            evaporation_rate: Rate at which pheromones evaporate (0-1)
            alpha: Pheromone bias (importance of pheromone trails)
            beta: Edge cost bias (importance of shorter paths)
            mode: Search mode (0: find any destination, 1: find all destinations)
        """
        # Store all parameters
        self.graph = graph
        self.ant_max_steps = ant_max_steps
        self.num_iterations = num_iterations
        self.ant_random_spawn = ant_random_spawn
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.mode = mode
        
        # Initialize other fields
        self.search_ants = []
        self.best_path = []
        self.best_path_cost = float("inf")
        
        # Initialize the Graph API
        self.graph_api = GraphApi(self.graph, self.evaporation_rate)
        
        # Initialize all edges of the graph with a pheromone value of 1.0
        for u, v in self.graph.get_edges():
            self.graph_api.set_edge_pheromones(u, v, 1.0)

    def _deploy_forward_search_ants(self) -> None:
        for ant in self.search_ants:
            step_count = 0
            # Process each ant until it reaches destination or max steps
            while not ant.reached_destination() and step_count < self.ant_max_steps:
                ant.take_step()
                step_count += 1
            
            if ant.reached_destination():
                ant.is_fit = True
                ant.deposit_pheromones_on_path(elitist_param = 0) # Local pheromone update no elitist
                
                if ant.path_cost < self.best_path_cost:
                    self.best_path = ant.path.copy()
                    self.best_path_cost = ant.path_cost
                    
                    ant.deposit_pheromones_on_path(elitist_param = 1) # Elitist pheromone update
                    
    # def _deploy_backward_search_ants(self) -> None:
    #     pass

    def _deploy_search_ants(self, source: str, destination: str, num_ants: int) -> None:
        for iteration in range(self.num_iterations):
            # Clear previous ants
            self.search_ants.clear()
            
            # Create new ants (only create what we need)
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
                    mode=self.mode
                )
                self.search_ants.append(ant)

            # Deploy ants
            self._deploy_forward_search_ants()
            # self._deploy_backward_search_ants()        
            
            # Evaporate pheromones after each iteration
            self.graph_api.evaporate_pheromones() #Global pheromone update

    def _deploy_solution_ant(self, source: str, destination: str) -> Ant:
        """Deploy the pheromone-greedy solution to find the shortest path

        Args:
            source (str): The source node in the graph
            destination (str): The destination node in the graph

        Returns:
            Ant: The solution ant with the computed shortest path and cost
        """
        # Otherwise, create a new solution ant
        ant = Ant(
            self.graph_api,
            source,
            destination,
            is_solution_ant=True,
            # Use higher beta for solution ant to favor shorter paths
            beta=self.beta,
            alpha=self.alpha * 2,
            mode=self.mode
        )
        
        steps = 0
        solution_max_steps = self.ant_max_steps * 2  # Give solution ant more steps
        
        while not ant.reached_destination() and steps < solution_max_steps:
            ant.take_step()
            steps += 1
        
        if not ant.reached_destination():
            raise Exception(f"Solution ant could not reach destination after {steps} steps.")
            
        return ant

    def find_shortest_path(
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
        for dest in destination:
            if dest not in self.graph.nodes():
                raise ValueError(f"Destination node {dest} not in graph")
        
        # Do the actual search
        self._deploy_search_ants(
            source,
            destination,
            num_ants,
        )
        
        solution_ant = self._deploy_solution_ant(source, destination)
        
        return solution_ant.path, solution_ant.path_cost
