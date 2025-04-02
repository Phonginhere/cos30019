import os
import sys
from collections import deque

# Get the path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Parent directory:", parent_dir)
# Add the path to the common search network class
common_dir = os.path.join(parent_dir, "Custom_Search", "Dijkstras_Algorithm")
sys.path.append(common_dir)

# Import the intermediate parent class
from SearchNetwork import SearchNetwork

class UninformNetwork(SearchNetwork):
    """
    Extended Network class with BFS functionalities for path finding.
    """
    
    def bfs_traverse(self, start):
        """
        Perform a BFS traversal from the start node.
        
        Returns:
            List of nodes in BFS traversal order
        """
        visited = set()
        queue = deque([start])
        visited.add(start)
        traversal = []
        
        while queue:
            node = queue.popleft()
            traversal.append(node)
            
            for neighbor in self.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return traversal
    
    def bfs_path(self, start, goal):
        """
        Find the shortest path from start to goal considering edge weights.
        
        Returns:
            tuple: (path, weight) where path is a list of nodes and weight is the total path weight.
                   If no path is found, returns (None, float('inf')).
        """
        if start == goal:
            return [start], 0
        
        # Track best path to each node
        best_paths = {start: ([start], 0)}  # {node: (path_to_node, total_weight)}
        queue = deque([start])
        
        while queue:
            current = queue.popleft()
            current_path, current_weight = best_paths[current]
            
            for neighbor in self.neighbors(current):
                edge_weight = self.get_edge_data(current, neighbor).get('weight', 1)
                new_weight = current_weight + edge_weight
                new_path = current_path + [neighbor]
                
                # Only explore if we haven't seen this node yet or if we found a better path
                if neighbor not in best_paths or new_weight < best_paths[neighbor][1]:
                    best_paths[neighbor] = (new_path, new_weight)
                    # Only add to queue if not the goal (to continue exploration)
                    if neighbor != goal:
                        queue.append(neighbor)
        
        # Return the best path to the goal if found
        if goal in best_paths:
            return best_paths[goal]  # Returns (path, weight) tuple
        else:
            return None, float('inf')
    
    def find_shortest_path_to_destinations(self, origin, destinations):
        """
        Find the shortest path from origin to any of the destinations.
        
        Returns:
            tuple: (path, destination, weight) of the shortest path
        """
        shortest_path = None
        shortest_dest = None
        shortest_weight = float('inf')
        
        for dest in destinations:
            path, weight = self.bfs_path(origin, dest)
            if path and weight < shortest_weight:
                shortest_weight = weight
                shortest_path = path
                shortest_dest = dest
                
        return shortest_path, shortest_dest, shortest_weight
    