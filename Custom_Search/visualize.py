import os
import sys
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import numpy as np
from datetime import datetime

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

from aco_routing.aco import ACO
from aco_routing.network import Network

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))

from parser import parse_graph_file

class ACOVisualizer:
    def __init__(self, graph_file):
        """Initialize the ACO visualizer with a graph file"""
        self.graph_file = graph_file
        self.nodes, self.edges, self.origin, self.destinations = parse_graph_file(graph_file)
        
        # Create the Network graph
        self.G = Network()
        self.G.graph = {node: [] for node in self.nodes}
        self.G.pos = self.nodes
        
        # Add edges
        for (start, end), weight in self.edges.items():
            self.G.add_edge(start, end, cost=float(weight))
            
        # Calculate parameters
        self.node_count = self.G.number_of_nodes()
        self.ant_max_steps = self.node_count * 2
        self.iterations = 300
        self.num_ants = self.node_count
        self.alpha = 1.0
        self.beta = 2.0
        self.evaporation_rate = 0.1
        
        # Initialize ACO
        self.aco = ACO(
            self.G,
            ant_max_steps=self.ant_max_steps,
            num_iterations=self.iterations,
            evaporation_rate=self.evaporation_rate,
            alpha=self.alpha,
            beta=self.beta,
            mode=2,  # TSP mode
            log_step=None  # No logging to console
        )
        
        # Initialize visualization
        plt.style.use('ggplot')
        self.fig = plt.figure(figsize=(15, 10))
        
        # Setup subplots
        self.graph_ax = self.fig.add_subplot(2, 2, 1)  # Graph visualization
        self.cost_ax = self.fig.add_subplot(2, 2, 2)   # Cost over time
        self.path_ax = self.fig.add_subplot(2, 1, 2)   # Current best path
        
        # Data for plotting
        self.iteration_data = []
        self.cost_data = []
        self.best_path = []
        self.best_cost = float('inf')
        self.animation = None
        
    def initialize_plot(self):
        """Initialize the plot with empty data"""
        # Clear all axes
        self.graph_ax.clear()
        self.cost_ax.clear()
        self.path_ax.clear()
        
        # Set titles and labels
        self.fig.suptitle(f'ACO TSP Solver Visualization - Nodes: {self.node_count}', fontsize=16)
        self.graph_ax.set_title('Graph Structure')
        self.cost_ax.set_title('Best Solution Cost Over Iterations')
        self.cost_ax.set_xlabel('Iteration')
        self.cost_ax.set_ylabel('Cost')
        self.path_ax.set_title('Current Best Path')
        
        # Draw the graph structure (nodes and edges)
        self._plot_graph_structure()
        
        # Initialize cost plot with empty data
        self.cost_line, = self.cost_ax.plot([], [], 'r-', linewidth=2)
        self.cost_ax.grid(True)
        
        # Return the objects that will be updated
        return self.cost_line,
    
    def _plot_graph_structure(self):
        """Plot the basic graph structure without the path"""
        # Create networkx graph from our data for visualization
        G_nx = nx.DiGraph()
        
        # Add nodes with positions
        for node, pos in self.G.pos.items():
            G_nx.add_node(node, pos=pos)
        
        # Add edges
        for u, v in self.G.get_edges():
            cost = self.G.get_edge_data(u, v).get('cost', 1.0)
            G_nx.add_edge(u, v, weight=cost)
        
        # Get positions from our graph
        pos = {node: self.G.pos[node] for node in self.G.pos}
        
        # Draw nodes
        nx.draw_networkx_nodes(G_nx, pos, node_size=700, node_color='skyblue', 
                              edgecolors='black', ax=self.graph_ax)
        
        # Draw edges
        nx.draw_networkx_edges(G_nx, pos, width=1.0, edge_color='gray', 
                              alpha=0.7, arrows=True, ax=self.graph_ax)
        
        # Draw labels
        nx.draw_networkx_labels(G_nx, pos, font_size=10, font_weight='bold', ax=self.graph_ax)
        
        # Highlight the origin node
        nx.draw_networkx_nodes(G_nx, pos, nodelist=[self.origin], node_size=900, 
                              node_color='green', edgecolors='black', ax=self.graph_ax)
    
    def update_plot(self, frame):
        """Update the plot for each frame"""
        # Run one iteration of ACO
        self._run_iteration(frame)
        
        # Update cost plot
        self.iteration_data.append(frame)
        self.cost_data.append(self.best_cost)
        self.cost_line.set_data(self.iteration_data, self.cost_data)
        
        # Adjust cost plot limits
        if self.cost_data:
            min_cost = min(self.cost_data)
            max_cost = max(self.cost_data)
            padding = (max_cost - min_cost) * 0.1 if max_cost > min_cost else 1.0
            self.cost_ax.set_xlim(0, frame + 5)
            self.cost_ax.set_ylim(min_cost - padding, max_cost + padding)
        
        # Update path visualization
        self._plot_current_best_path()
        
        # Return the objects that were updated
        return self.cost_line,
    
    def _run_iteration(self, iteration):
        """Run one iteration of the ACO algorithm"""
        # Clear previous ants
        self.aco.search_ants.clear()
        
        # Create new ants
        for _ in range(self.num_ants):
            # For TSP, choose spawn point
            spawn_point = self.origin
            all_nodes = list(self.G.nodes())
            
            # Create ant 
            ant = self.aco.search_ants.append(
                self.aco.graph_api,
                spawn_point,
                all_nodes,
                alpha=self.alpha,
                beta=self.beta,
                mode=2  # TSP mode
            )
            self.aco.search_ants.append(ant)
        
        # Run forward and backward phases
        self.aco._deploy_forward_search_ants()
        max_pheromon, min_pheromon = self.aco._deploy_backward_search_ants(iteration, self.num_ants)
        
        # Update pheromones
        self.aco.acc, self.aco.d_acc = self.aco.graph_api.update_pheromones(
            max_pheromon, min_pheromon, self.aco.acc, self.aco.d_acc
        )
        
        # Update best path data for visualization
        if self.aco.best_path and self.aco.best_path_cost < self.best_cost:
            self.best_path = self.aco.best_path.copy()
            self.best_cost = self.aco.best_path_cost
    
    def _plot_current_best_path(self):
        """Plot the current best path found by the ACO algorithm"""
        self.path_ax.clear()
        self.path_ax.set_title(f'Current Best Path (Cost: {self.best_cost:.2f})')
        
        if not self.best_path:
            self.path_ax.text(0.5, 0.5, 'No path found yet', 
                             ha='center', va='center', fontsize=14)
            return
        
        # Create a networkx graph for the best path
        G_path = nx.DiGraph()
        
        # Add nodes with positions
        for node in self.best_path:
            if node in self.G.pos:
                G_path.add_node(node, pos=self.G.pos[node])
        
        # Add edges in the best path
        for i in range(len(self.best_path) - 1):
            u, v = self.best_path[i], self.best_path[i + 1]
            cost = self.G.get_edge_data(u, v).get('cost', 1.0)
            G_path.add_edge(u, v, weight=cost)
        
        # Get positions
        pos = {node: self.G.pos[node] for node in G_path.nodes()}
        
        # Draw all nodes lightly
        all_nodes = list(self.G.nodes())
        all_pos = {node: self.G.pos[node] for node in all_nodes if node in self.G.pos}
        nx.draw_networkx_nodes(nx.DiGraph(), all_pos, node_size=500, 
                              node_color='lightgray', alpha=0.3, ax=self.path_ax)
        
        # Draw path nodes
        nx.draw_networkx_nodes(G_path, pos, node_size=700, 
                              node_color='lightcoral', edgecolors='black', 
                              ax=self.path_ax)
        
        # Highlight first and last node
        if self.best_path:
            first_node = self.best_path[0]
            if first_node in pos:
                nx.draw_networkx_nodes(G_path, {first_node: pos[first_node]}, 
                                      nodelist=[first_node], node_size=900, 
                                      node_color='green', edgecolors='black', 
                                      ax=self.path_ax)
        
        # Draw path edges with arrows
        nx.draw_networkx_edges(G_path, pos, width=2.0, edge_color='red', 
                              arrows=True, arrowsize=20, ax=self.path_ax)
        
        # Draw labels
        nx.draw_networkx_labels(G_path, pos, font_size=10, 
                               font_weight='bold', ax=self.path_ax)
        
        # Draw edge labels (costs)
        edge_labels = {(u, v): f"{G_path[u][v]['weight']:.1f}" 
                      for u, v in G_path.edges()}
        nx.draw_networkx_edge_labels(G_path, pos, edge_labels=edge_labels, 
                                   font_size=8, ax=self.path_ax)
        
        # Add path sequence as text
        path_text = " → ".join(self.best_path)
        self.path_ax.text(0.5, -0.1, f"Path: {path_text}", 
                         ha='center', va='center', fontsize=10, 
                         bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'),
                         transform=self.path_ax.transAxes)
    
    def run_animation(self):
        """Run the animation"""
        # Initialize ACO algorithm
        self.aco.best_path = []
        self.aco.best_path_cost = float('inf')
        self.best_path = []
        self.best_cost = float('inf')
        self.iteration_data = []
        self.cost_data = []
        
        # Create animation
        self.animation = FuncAnimation(
            self.fig, 
            self.update_plot, 
            frames=range(self.iterations),
            init_func=self.initialize_plot,
            interval=200,  # 200ms between frames
            repeat=False,
            blit=True
        )
        
        # Show plot
        plt.tight_layout()
        plt.show()
    
    def save_animation(self, filename=None):
        """Save the animation as a video file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aco_visualization_{timestamp}.mp4"
        
        try:
            # Needs ffmpeg installed
            print(f"Saving animation to {filename}...")
            self.animation.save(filename, fps=5, extra_args=['-vcodec', 'libx264'])
            print(f"Animation saved to {filename}")
        except Exception as e:
            print(f"Error saving animation: {e}")
            print("Make sure you have ffmpeg installed and in your PATH")

def main():
    # Get graph file from command line argument
    graph_file = sys.argv[1] if len(sys.argv) > 1 else "Data/TSP_Test_case_4.txt"
    
    # Create visualizer
    visualizer = ACOVisualizer(graph_file)
    
    # Run visualization
    visualizer.run_animation()
    
    # Optionally save the animation
    # visualizer.save_animation()

if __name__ == "__main__":
    main()