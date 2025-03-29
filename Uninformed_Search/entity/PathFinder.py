import heapq

class PathFinder:
    """Provides various pathfinding algorithms for graphs."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def dijkstra(self, start, goal):
        """
        Find shortest path using Dijkstra's algorithm.
        
        Returns:
            tuple: (goal_node, path_length, path, cost) or (None, float('inf')) if no path exists
        """
        visited = set()
        heap = [(0, start, [start])]
        
        while heap:
            cost, node, path = heapq.heappop(heap)
            
            if node == goal:  # Check if we've reached the goal
                return node, len(path), path, cost
            
            if node in visited:
                continue
            
            visited.add(node)

            for neighbor, edge_cost in self.graph.get_neighbors(node):
                if neighbor not in visited:
                    heapq.heappush(heap, (cost + edge_cost, neighbor, path + [neighbor]))
            
        return None, float('inf')