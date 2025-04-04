import os
import sys

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print("Parent directory:", parent_dir)
# Add the path to the common search network class
common_dir = os.path.join(parent_dir, "Custom_Search", "Dijkstras_Algorithm")
sys.path.append(common_dir)

# Import the intermediate parent class
from SearchNetwork import SearchNetwork

class DfsNetwork(SearchNetwork):
    """
    Extended Network class with DFS functionalities for path finding.
    """
    
    def dfs_traverse(self, start):
        """
        Perform a DFS traversal from the start node.
        
        Returns:
            List of nodes in DFS traversal order
        """
        visited = set()
        traversal = []
        
        def dfs_recursive(node):
            visited.add(node)
            traversal.append(node)
            
            for neighbor in self.neighbors(node):
                if neighbor not in visited:
                    dfs_recursive(neighbor)
        
        dfs_recursive(start)
        return traversal
    
    def dfs_path(self, start, goal):
        """
        Find a path from start to goal using DFS.
        
        Returns:
            tuple: (path, weight) where path is a list of nodes and weight is the total path weight.
                   If no path is found, returns (None, float('inf')).
        """
        if start == goal:
            return [start], 0
        
        visited = set()
        
        def dfs_recursive(current, path=None, weight=0):
            if path is None:
                path = [current]
            
            visited.add(current)
            
            if current == goal:
                return path, weight
            
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    edge_weight = self.get_edge_data(current, neighbor).get('weight', 1)
                    new_weight = weight + edge_weight
                    result_path, result_weight = dfs_recursive(neighbor, path + [neighbor], new_weight)
                    
                    if result_path:  # If a path was found
                        return result_path, result_weight
            
            return None, float('inf')
        
        return dfs_recursive(start)
    
    def find_path(self, start, goal):
        """Implementation of the abstract method using DFS"""
        return self.dfs_path(start, goal)