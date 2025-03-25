from typing import List, Dict
import matplotlib.pyplot as plt
import os
import sys
import numpy as np

# Add the parent directory to the system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from aco_routing.network import Network


class GraphApi:
    def __init__(self, graph: Network, evaporation_rate: float):
        """Initialize the GraphApi with a network and evaporation rate.
        
        Args:
            graph: Network object containing the graph structure
            evaporation_rate: Rate at which pheromones evaporate (0-1)
        """
        self.graph = graph
        self.evaporation_rate = evaporation_rate
        
        # Precompute and cache edge costs
        self._edge_cost_cache = {}
        self._neighbor_cache = {}
        
        # Precompute edge costs
        for u, v in self.graph.get_edges():
            self._edge_cost_cache[(u, v)] = self.graph.edges.get((u, v), {}).get("cost", float('inf'))
        
        # Precompute neighbors for each node
        for node in self.graph.nodes():
            self._neighbor_cache[node] = list(self.graph.neighbors(node))

    def set_edge_pheromones(self, u: str, v: str, pheromone_value: float) -> None:
        if (u, v) in self.graph.edges:
            self.graph.edges[(u, v)]["pheromones"] = pheromone_value

    def get_edge_pheromones(self, u: str, v: str) -> float:
        return self.graph.edges.get((u, v), {}).get("pheromones", 0.0)

    def deposit_pheromones(self, u: str, v: str, pheromone_amount: float) -> None:
        if (u, v) in self.graph.edges:
            pheromones = self.graph.edges[(u, v)].get("pheromones", 0.0)
            new_pheromone = (1 - self.evaporation_rate) * pheromones + pheromone_amount
            self.graph.edges[(u, v)]["pheromones"] = max(new_pheromone, 1e-13)

    def get_edge_cost(self, u: str, v: str) -> float:
        """Get edge cost with caching for better performance"""
        # Use cached value if available
        if hasattr(self, '_edge_cost_cache') and (u, v) in self._edge_cost_cache:
            return self._edge_cost_cache[(u, v)]
        
        # Fallback to original implementation
        return self.graph.edges.get((u, v), {}).get("cost", float('inf'))

    def get_all_nodes(self) -> List[str]:
        return list(self.graph.nodes())

    def get_neighbors(self, node: str) -> List[str]:
        """Get neighbors with caching for better performance"""
        # Use cached value if available
        if hasattr(self, '_neighbor_cache') and node in self._neighbor_cache:
            return self._neighbor_cache[node]
        
        # Fallback to original implementation
        return list(self.graph.neighbors(node))
    
    def get_pheromone_levels(self) -> Dict:
        """Get all pheromone levels in the graph for debugging"""
        result = {}
        for (u, v) in self.graph.get_edges():
            result[(u, v)] = self.get_edge_pheromones(u, v)
        return result

    def visualize_graph(self, shortest_path: List[str], shortest_path_cost=None) -> None:
        """Visualize the graph with the shortest path highlighted
        
        Args:
            shortest_path: List of nodes representing the path to highlight
            shortest_path_cost: The cost of the shortest path (optional)
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Ensure all nodes in the path are strings
            shortest_path = [str(node) for node in shortest_path]
            
            # Create a figure with a specific size
            plt.figure(figsize=(12, 10))
            
            # Create positions for nodes (simple grid layout)
            pos = self.graph.spring_layout()
            
            # Convert all position keys to strings for consistency
            pos = {str(k): v for k, v in pos.items()}
            
            # Create a set of path edges for easy lookup
            path_edges = set()
            for i in range(len(shortest_path) - 1):
                path_edges.add((shortest_path[i], shortest_path[i + 1]))
            
            # Draw ALL nodes in the graph
            path_nodes = set(shortest_path)
            all_nodes = list(self.graph.nodes())
            
            # Draw non-path nodes first (in the background)
            non_path_nodes = [node for node in all_nodes if str(node) not in path_nodes]
            non_path_xs = [pos[str(node)][0] for node in non_path_nodes if str(node) in pos]
            non_path_ys = [pos[str(node)][1] for node in non_path_nodes if str(node) in pos]
            plt.scatter(non_path_xs, non_path_ys, s=700, c='skyblue', edgecolors='black', zorder=1)
            
            # Draw path nodes on top (highlighted)
            path_xs = [pos[node][0] for node in path_nodes if node in pos]
            path_ys = [pos[node][1] for node in path_nodes if node in pos]
            plt.scatter(path_xs, path_ys, s=900, c='lightcoral', edgecolors='black', zorder=2)
            
            # FIRST draw ALL edges with low opacity
            for u, v in self.graph.get_edges():
                # Skip if either node position is missing
                if str(u) not in pos or str(v) not in pos:
                    continue
                    
                x1, y1 = pos[str(u)]
                x2, y2 = pos[str(v)]
                
                # Draw unused edge with low opacity
                plt.plot([x1, x2], [y1, y2], color='grey', linewidth=1.5, alpha=0.3, zorder=0)
                
                # Add small arrow to show direction
                dx = x2 - x1
                dy = y2 - y1
                length = np.sqrt(dx**2 + dy**2)
                dx, dy = dx/length, dy/length  # Normalize
                
                plt.arrow(
                    x1 + 0.8*dx*length, y1 + 0.8*dy*length, 
                    0.05*dx*length, 0.05*dy*length, 
                    head_width=0.03, 
                    head_length=0.05, 
                    fc='grey', ec='grey',
                    alpha=0.3,
                    zorder=0
                )
                
                # Add faded edge cost label closer to the arrow head
                # Position the label at 75% along the edge (closer to target)
                label_x = x1 + 0.75 * dx * length
                label_y = y1 + 0.75 * dy * length
                
                # Try to get the edge data
                edge_data = self.graph.edges.get((u, v), None)
                if not edge_data:
                    edge_data = self.graph.edges.get((str(u), str(v)), None)
                
                if edge_data:
                    cost = edge_data.get("cost", 0)
                    plt.text(label_x, label_y, f"{cost}", fontsize=10, alpha=0.3,
                            bbox=dict(facecolor='white', alpha=0.2, edgecolor='lightgrey'),
                            ha='center', va='center',  # Center the text
                            zorder=0)
            
            # THEN draw the path edges on top with high visibility
            for i in range(len(shortest_path) - 1):
                u, v = shortest_path[i], shortest_path[i + 1]
                
                # Skip if either node position is missing
                if u not in pos or v not in pos:
                    continue
                    
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                
                # Draw path edge
                plt.plot([x1, x2], [y1, y2], color='red', linewidth=3, zorder=3)
                
                # Add arrow to show direction
                dx = x2 - x1
                dy = y2 - y1
                length = np.sqrt(dx**2 + dy**2)
                dx, dy = dx/length, dy/length  # Normalize
                
                # Arrow position
                arrow_x = x1 + 0.8*dx*length
                arrow_y = y1 + 0.8*dy*length
                
                plt.arrow(
                    arrow_x, arrow_y, 
                    0.1*dx*length, 0.1*dy*length, 
                    head_width=0.05, 
                    head_length=0.1, 
                    fc='red', ec='red',
                    zorder=4
                )
                
                # Add edge label closer to the head of the arrow
                # Position label at 80% along the edge
                label_x = x1 + 0.8 * dx * length
                label_y = y1 + 0.8 * dy * length
                
                # Offset the label slightly to avoid overlapping with the arrow
                offset = 0.05
                # Perpendicular offset to avoid overlapping the edge
                label_x += offset * (-dy)  # Perpendicular to edge direction
                label_y += offset * dx     # Perpendicular to edge direction
                
                # Try both string and original forms of edge for lookup
                edge_data = None
                edge_pairs = [
                    (u, v),
                    (int(u) if u.isdigit() else u, int(v) if v.isdigit() else v),
                    (str(u), str(v))
                ]
                
                for edge_pair in edge_pairs:
                    if edge_pair in self.graph.edges:
                        edge_data = self.graph.edges[edge_pair]
                        break
                
                if edge_data:
                    cost = edge_data.get("cost", 0)
                    label = f"cost: {cost}"
                    plt.text(label_x, label_y, label, fontsize=12, fontweight='bold',
                            bbox=dict(facecolor='mistyrose', alpha=0.8, edgecolor='gray'),
                            ha='center', va='center',  # Center the text
                            zorder=5)
            
            # Add node labels for ALL nodes
            for node in all_nodes:
                str_node = str(node)
                if str_node not in pos:
                    continue
                    
                x, y = pos[str_node]
                # Highlight path node labels
                if str_node in path_nodes:
                    plt.text(x, y, str_node, fontsize=14, fontweight='bold', ha='center', va='center', zorder=6)
                else:
                    plt.text(x, y, str_node, fontsize=12, fontweight='normal', ha='center', va='center', zorder=6)
            
            # Add grid
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Add title
            path_str = " → ".join(shortest_path)
            cost_str = f", Cost: {shortest_path_cost}" if shortest_path_cost is not None else ""
            plt.title(f"Shortest Path: {path_str}{cost_str}", fontsize=14)
            
            # Add a legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='red', lw=3, label='Path edge'),
                Line2D([0], [0], color='grey', lw=1.5, alpha=0.3, label='Unused edge'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                    markersize=15, label='Path node'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', 
                    markersize=15, label='Regular node'),
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Show the plot
            plt.show()
        
        except Exception as e:
            import traceback
            print(f"Detailed visualization error: {e}")
            traceback.print_exc()
        
    def visualize_original_graph(self) -> None:
        # Create a figure with a specific size
        plt.figure(figsize=(12, 10))
        
        # Create positions for nodes (simple grid layout)
        pos = self.graph.spring_layout()
        
        # Draw nodes
        node_xs = [pos[node][0] for node in self.graph.nodes()]
        node_ys = [pos[node][1] for node in self.graph.nodes()]
        plt.scatter(node_xs, node_ys, s=700, c='skyblue', edgecolors='black')
        
        # Track bidirectional edges
        bidirectional_edges = {}
        
        # First pass: identify bidirectional edges
        for u, v in self.graph.get_edges():
            if self.graph.has_edge(v, u):
                # This is a bidirectional edge
                if (v, u) not in bidirectional_edges:  # Avoid duplicates
                    bidirectional_edges[(u, v)] = True
                    bidirectional_edges[(v, u)] = True
        
        # Draw regular edges (not bidirectional)
        for u, v in self.graph.get_edges():
            if (u, v) not in bidirectional_edges:
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                plt.plot([x1, x2], [y1, y2], color='blue', linewidth=2, alpha=0.7)
                
                # Add arrow to show direction
                dx = x2 - x1
                dy = y2 - y1
                plt.arrow(
                    x1 + 0.8*dx, y1 + 0.8*dy, 
                    0.1*dx, 0.1*dy, 
                    head_width=0.05, 
                    head_length=0.1, 
                    fc='blue', ec='blue'
                )
        
        # Draw bidirectional edges with curved lines
        for u, v in bidirectional_edges:
            # Only draw each bidirectional edge once
            if u < v:  # Arbitrary ordering to avoid duplicates
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                
                # Calculate curve control point
                midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
                normal_x, normal_y = -(y2 - y1), (x2 - x1)  # Normal to the line
                length = (normal_x**2 + normal_y**2)**0.5
                normal_x, normal_y = normal_x/length*0.2, normal_y/length*0.2  # Normalize and scale
                
                # Forward edge (u to v) - green curved arrow
                plt.annotate(
                    "", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(
                        arrowstyle="->", color="green", lw=2,
                        connectionstyle=f"arc3,rad=0.2"
                    )
                )
                
                # Backward edge (v to u) - red curved arrow
                plt.annotate(
                    "", xy=(x1, y1), xytext=(x2, y2),
                    arrowprops=dict(
                        arrowstyle="->", color="red", lw=2,
                        connectionstyle=f"arc3,rad=0.2"
                    )
                )
        
        # Add node labels
        for node in self.graph.nodes():
            x, y = pos[node]
            plt.text(x, y, node, fontsize=12, fontweight='bold', ha='center', va='center')
        
        # Add edge cost labels
        for u, v in self.graph.get_edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            midx, midy = (x1 + x2) / 2, (y1 + y2) / 2
            
            # Adjust label position for bidirectional edges
            if (u, v) in bidirectional_edges:
                if u < v:  # Forward edge
                    normal_x, normal_y = -(y2 - y1), (x2 - x1)  # Normal to the line
                    length = (normal_x**2 + normal_y**2)**0.5
                    normal_x, normal_y = normal_x/length*0.1, normal_y/length*0.1  # Normalize and scale
                    midx += normal_x
                    midy += normal_y
                else:  # Backward edge
                    normal_x, normal_y = (y2 - y1), -(x2 - x1)  # Normal to the line
                    length = (normal_x**2 + normal_y**2)**0.5
                    normal_x, normal_y = normal_x/length*0.1, normal_y/length*0.1  # Normalize and scale
                    midx += normal_x
                    midy += normal_y
            
            cost = str(self.graph.edges[(u, v)].get("cost", ""))
            plt.text(midx, midy, cost, fontsize=10, 
                    bbox=dict(facecolor='white', alpha=0.7))
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels and title
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.title('Graph Visualization with Bidirectional Edges')
        
        # Add a legend for edge types
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='One-way edge'),
            Line2D([0], [0], color='green', lw=2, label='Two-way edge (forward)'),
            Line2D([0], [0], color='red', lw=2, label='Two-way edge (reverse)')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Show the plot
        plt.show()