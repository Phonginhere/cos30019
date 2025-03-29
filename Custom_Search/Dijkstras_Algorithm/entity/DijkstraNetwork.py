import os
import sys
import heapq

# Fix the path imports
current_dir = os.path.dirname(os.path.abspath(__file__))
print("Current directory:", current_dir)
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
print("Parent directory:", parent_dir)

# Import the intermediate parent class
common_dir = os.path.join(parent_dir, "Uninformed_Search", "entity")
sys.path.append(common_dir)

from SearchNetwork import SearchNetwork

class DijkstraNetwork(SearchNetwork):
    """
    Extended Network class with Dijkstra's algorithm for finding shortest paths.
    """
    
    def dijkstra(self, start, goal):
        """Find the shortest path from start to goal using Dijkstra's algorithm."""
        # Priority queue with (cost, node, path)
        heap = [(0, start, [start])]
        # Track visited nodes to avoid cycles
        visited = set()
        
        while heap:
            cost, node, path = heapq.heappop(heap)
            
            # If we've reached the goal, return the path and cost
            if node == goal:
                return path, cost
            
            # Skip if we've already visited this node
            if node in visited:
                continue
            
            visited.add(node)
            
            # Explore neighbors
            for neighbor in self.neighbors(node):
                if neighbor not in visited:
                    edge_data = self.get_edge_data(node, neighbor)
                    edge_cost = edge_data.get('weight', 1)  # Default to 1 if no weight specified
                    new_cost = cost + edge_cost
                    new_path = path + [neighbor]
                    heapq.heappush(heap, (new_cost, neighbor, new_path))
        
        # No path found
        return None, float('inf')
    
    def find_shortest_path_to_destinations(self, origin, destinations):
        """Find the shortest path from origin to any of the destinations."""
        shortest_path = None
        shortest_dest = None
        shortest_cost = float('inf')
        
        for dest in destinations:
            path, cost = self.dijkstra(origin, dest)
            if path and cost < shortest_cost:
                shortest_cost = cost
                shortest_path = path
                shortest_dest = dest
        
        return shortest_path, shortest_dest, shortest_cost