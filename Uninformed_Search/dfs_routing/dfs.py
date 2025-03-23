from dataclasses import dataclass, field
import random
from typing import List, Tuple, Set, Dict, Optional
import networkx as nx

from dfs_routing.graph_api import GraphApi

@dataclass
class Dfs:
    visited_nodes: Set = field(default_factory=set)
    path: List[str] = field(default_factory=list)
    path_cost: float = 0.0
    def __init__(self, graph_api: GraphApi, source: str, destination: str) -> None:
        self.graph_api = graph_api
        self.source = source
        self.destination = destination
        self.post_init()
    
    def post_init(self) -> None:
        # Set the spawn node as the current and first node
        self.current_node = self.source
        self.path = [self.source]
        self.visited_nodes = set([self.source])
        self.frontier = []  # Frontier to store paths to explore
        
        # Initialize frontier with paths from the source
        neighbors = self.graph_api.neighbors(self.source)
        for neighbor, cost in neighbors:
            if neighbor not in self.visited_nodes:
                self.frontier.append({
                    'path': [self.source, neighbor],
                    'cost': cost,
                    'current': neighbor
                })
    
    def find_path(self) -> Tuple[List[str], int]:
        """
        Uses DFS with a frontier-based approach to find a path 
        from source to destination.
        
        Returns:
            Tuple[List[str], int]: The path found and its total cost
        """
        # Check if source is already the destination
        if self.source == self.destination:
            return [self.source], 0
        
        # While there are still paths to explore in the frontier
        while self.frontier:
            # Get the next path to explore (from the end for DFS behavior)
            current = self.frontier.pop()
            current_path = current['path']
            current_cost = current['cost']
            current_node = current['current']
            
            # Mark the current node as visited
            self.visited_nodes.add(current_node)
            
            # Check if we've reached the destination
            if current_node == self.destination:
                return current_path, current_cost
            
            # Get all neighbors of the current node
            neighbors = self.graph_api.get_neighbors(current_node)
            
            # Add unvisited neighbors to the frontier
            for neighbor, edge_cost in neighbors:
                if neighbor not in self.visited_nodes and neighbor not in [node['current'] for node in self.frontier]:
                    new_path = current_path.copy()
                    new_path.append(neighbor)
                    
                    # Add to frontier (at the end for DFS behavior)
                    self.frontier.append({
                        'path': new_path,
                        'cost': current_cost + edge_cost,
                        'current': neighbor
                    })
        
        # If no path is found
        return [], 0
    
    def get_visited_nodes(self) -> Set[str]:
        """
        Returns the set of nodes that were visited during the search.
        """
        return self.visited_nodes
    
    def get_path_with_cost(self) -> Tuple[List[str], int]:
        """
        Runs the DFS algorithm and returns the found path with its cost.
        
        Returns:
            Tuple[List[str], int]: The found path and its total cost
        """
        return self.find_path()
    
    def get_path(self) -> List[str]:
        """
        Returns just the path found by DFS.
        
        Returns:
            List[str]: The found path
        """
        path, _ = self.find_path()
        return path
    
    def get_cost(self) -> int:
        """
        Returns just the cost of the path found by DFS.
        
        Returns:
            int: The total cost of the found path
        """
        _, cost = self.find_path()
        return cost
    
    def __str__(self) -> str:
        """
        Returns a string representation of the DFS algorithm results.
        
        Returns:
            str: Information about the path and visited nodes
        """
        path, cost = self.get_path_with_cost()
        
        if not path:
            return f"No path found from {self.source} to {self.destination}"
        
        path_str = " -> ".join(path)
        visited_str = ", ".join(sorted(self.visited_nodes))
        
        return (f"Path found: {path_str}\n"
                f"Total cost: {cost}\n"
                f"Nodes visited: {visited_str}\n"
                f"Total nodes visited: {len(self.visited_nodes)}")