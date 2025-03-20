import matplotlib.pyplot as plt
import numpy as np

# Define the nodes with their coordinates
nodes = {
    1: (4, 1),
    2: (2, 2),
    3: (4, 4),
    4: (6, 3),
    5: (5, 6),
    6: (7, 5)
}

# Define the edges with their weights
edges = {
    (2, 1): 4,
    (3, 1): 5,
    (1, 3): 5,
    (2, 3): 4,
    (3, 2): 5,
    (4, 1): 6,
    (1, 4): 6,
    (4, 3): 5,
    (3, 5): 6,
    (5, 3): 6,
    (4, 5): 7,
    (5, 4): 8,
    (6, 3): 7,
    (3, 6): 7
}

# Extract the x and y coordinates
x_coords = [coord[0] for coord in nodes.values()]
y_coords = [coord[1] for coord in nodes.values()]

# Create the plot
plt.figure(figsize=(10, 8))
plt.scatter(x_coords, y_coords, color='blue', zorder=3)

# Annotate the nodes
for node, (x, y) in nodes.items():
    plt.text(x, y, str(node), fontsize=12, ha='right', zorder=4)

# Draw the edges with arrows and labels
for (start, end), weight in edges.items():
    start_x, start_y = nodes[start]
    end_x, end_y = nodes[end]
    
    # Calculate the offset for bidirectional edges
    offset = 0.1 * np.array([end_y - start_y, start_x - end_x]) / np.linalg.norm([end_x - start_x, end_y - start_y])
    
    # Scale down the arrow length
    scale = 0.9  # Adjust this value to make arrows shorter or longer
    dx = (end_x - start_x) * scale
    dy = (end_y - start_y) * scale
    
    # Draw the arrow
    plt.arrow(start_x + offset[0], start_y + offset[1], dx, dy, 
              head_width=0.05, length_includes_head=True, color='black', linewidth=0.5, zorder=2)
    
    # Annotate the edge
    mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
    plt.text(mid_x + offset[0], mid_y + offset[1], str(weight), fontsize=10, color='red', zorder=4)

# Set the labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Node and Edge Plot')

# Show the grid
plt.grid(True)

# Show the plot
plt.show()