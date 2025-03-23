from dataclasses import dataclass
from typing import List
import networkx as nx
import matplotlib.pyplot as plt


@dataclass
class GraphApi:
    graph: nx.DiGraph
    evaporation_rate: float

    def set_edge_pheromones(self, u: str, v: str, pheromone_value: float) -> None:
        self.graph[u][v]["pheromones"] = pheromone_value

    def get_edge_pheromones(self, u: str, v: str) -> float:
        return self.graph[u][v]["pheromones"]

    def deposit_pheromones(self, u: str, v: str, pheromone_amount: float) -> None:
        self.graph[u][v]["pheromones"] += max(
            (1 - self.evaporation_rate) + pheromone_amount, 1e-13
        )

    def get_edge_cost(self, u: str, v: str) -> float:
        return self.graph[u][v]["cost"]

    def get_all_nodes(self) -> List[str]:
        return list(self.graph.nodes)

    def get_neighbors(self, node: str) -> List[str]:
        return list(self.graph.neighbors(node))

    def visualize_graph(self, shortest_path: List[str]) -> None:
        for edge in self.graph.edges:
            source, destination = edge[0], edge[1]
            self.graph[source][destination]["pheromones"] = round(
                self.graph[source][destination]["pheromones"]
            )

        pos = nx.spring_layout(self.graph, seed=2)
        nx.draw(self.graph, pos, width=4)

        nx.draw_networkx_nodes(self.graph, pos, node_size=700)

        # nx.draw_networkx_edges(G, pos, width=2)
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=list(zip(shortest_path, shortest_path[1:])),
            edge_color="r",
            width=4,
        )

        # node labels
        nx.draw_networkx_labels(self.graph, pos, font_size=20)
        # edge cost labels
        edge_labels = nx.get_edge_attributes(self.graph, "pheromones")
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels)

        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()
        
    def visualize_original_graph(self) -> None:
        # Create a figure with a specific size
        plt.figure(figsize=(12, 10))
        
        # Create a grid layout that positions nodes on x,y coordinates
        pos = nx.spring_layout(self.graph, seed=2)
        
        # Draw the graph nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=700, node_color='skyblue', edgecolors='black')
        
        # Draw the edges with curved arrows for bidirectional edges
        # Create a dictionary to track bidirectional edges
        bidirectional_edges = {}
        
        # First pass: identify bidirectional edges
        for u, v in self.graph.edges():
            if self.graph.has_edge(v, u):
                # This is a bidirectional edge
                if (v, u) not in bidirectional_edges:  # Avoid duplicates
                    bidirectional_edges[(u, v)] = True
                    bidirectional_edges[(v, u)] = True
        
        # Draw regular edges (not bidirectional)
        regular_edges = [(u, v) for u, v in self.graph.edges() if (u, v) not in bidirectional_edges]
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=regular_edges,
            edge_color="blue",
            width=2,
            alpha=0.7,
            arrowsize=15
        )
        
        # Draw bidirectional edges with curved arrows
        for u, v in bidirectional_edges:
            # Only draw each bidirectional edge once
            if u < v:  # Arbitrary ordering to avoid duplicates
                # Draw curved edge from u to v
                nx.draw_networkx_edges(
                    self.graph,
                    pos,
                    edgelist=[(u, v)],
                    edge_color="green",
                    width=2,
                    alpha=0.7,
                    arrowsize=15,
                    connectionstyle="arc3,rad=0.2"  # Curved edge
                )
                
                # Draw curved edge from v to u
                nx.draw_networkx_edges(
                    self.graph,
                    pos,
                    edgelist=[(v, u)],
                    edge_color="red",
                    width=2,
                    alpha=0.7,
                    arrowsize=15,
                    connectionstyle="arc3,rad=0.2"  # Curved edge in opposite direction
                )
        
        # Draw node labels
        nx.draw_networkx_labels(self.graph, pos, font_size=12, font_weight='bold')
        
        # Custom edge label positioning for bidirectional edges
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            edge_labels[(u, v)] = data["cost"]
        
        # Draw edge cost labels with adjusted positions
        nx.draw_networkx_edge_labels(
            self.graph, 
            pos, 
            edge_labels=edge_labels, 
            font_size=10,
            label_pos=0.3  # Adjust label position for better visibility
        )
        
        # Get axis object
        ax = plt.gca()
        
        # Turn on the axis
        plt.axis('on')
        
        # Set the axis limits based on node positions
        x_values = [x for x, y in pos.values()]
        y_values = [y for x, y in pos.values()]
        
        # Add some padding to the limits
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        padding = 0.1
        
        plt.xlim(x_min - padding, x_max + padding)
        plt.ylim(y_min - padding, y_max + padding)
        
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
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Show the plot
        plt.show()
