import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import heapq
import re

class Node:
    def __init__(self, start, heuristic):
        self.start = start
        self.heuristic = heuristic

    def __lt__(self,  other):
        return self.heuristic < other.heuristic
    
def find_next_node(graph, current, heuristic, visited_list):
    heuristic_value = []

    for i in graph[current]:
        if i not in visited_list:
            heapq.heappush(heuristic_value, Node(i, heuristic[(current, i)]))

    return heapq.heappop(heuristic_value)
        

def GBFS_search(graph, start, goal, heuristic):
    # path dictionary to track the explored paths
    path = {start:None}

    visited = set() # to keep track of visited nodes

    # Priority queue to hold nodes to explore, sorted by heuristic value
    priority_queue = []
    first = Node(start, 0)
    heapq.heappush(priority_queue, first)

    while priority_queue:
        current_node = heapq.heappop(priority_queue).start
        
        visited.add(current_node)

        # if the goal is reached, reconstruct the path
        if goal in visited:
            return reconstruct_path(path, start, goal)

        # find next node
        next_node = find_next_node(graph, current_node, heuristic, visited)
        heapq.heappush(priority_queue, next_node)
        if next_node.start not in path:
            path[next_node.start] = current_node

        print(path)
        
    return None

def reconstruct_path(path, start, goal):
    current = goal
    result_path = []

    while current is not None:
        result_path.append(current)
        current = path[current]
        print(f"Result path: {result_path}")
    result_path.reverse()
    print("Path from {} to {}: {}".format(start, goal, result_path))
    return result_path


def visualise(paths, pos, edges):
    fig, (ax1, ax2) = plt.subplots(1,2)
    ax1.set_xticks(range(11))
    ax1.set_yticks(range(11))

    ax2.set_xticks(range(11))
    ax2.set_yticks(range(11))

    ax1.grid(True, which='both', linestyle='-', linewidth=0.5)
    ax2.grid(True, which='both', linestyle='-', linewidth=0.5)

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)

    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)

    ax1.set_xlabel('x')
    ax1.set_ylabel('y')

    ax2.set_xlabel('x')
    ax2.set_ylabel('y')

    # plot the edge
    for edge in edges.keys():
        p1, p2 = edge

        x_values = [pos[p1][0], pos[p2][0]]
        y_values = [pos[p1][1], pos[p2][1]]

        ax1.plot(x_values, y_values, marker='o', color='blue')
        ax2.plot(x_values, y_values, marker='o', color='blue')

    # Annotate the points
    for point, coord in pos.items():
        ax1.text(coord[0], coord[1], point, fontsize=12, color='black', ha='right')
        ax2.text(coord[0], coord[1], point, fontsize=12, color='black', ha='right')
    
    xpoints = []
    ypoints = []
    for i in range(len(paths[0])):
        xpoints.append(pos[paths[0][i]][0])
        ypoints.append(pos[paths[0][i]][1])

    ax1.plot(xpoints, ypoints, marker='o', color='red')

    xpoints = []
    ypoints = []
    for i in range(len(paths[1])):
        xpoints.append(pos[paths[1][i]][0])
        ypoints.append(pos[paths[1][i]][1])

    ax2.plot(xpoints, ypoints, marker='o', color='lightgreen')

    plt.show()

graph = {
    '1': ['3','4'],
    '2': ['1','3'],
    '3': ['1','2','5','6'],
    '4': ['1','3','5'],
    '5': ['3','4'],
    '6': ['3']
}

import re

def parse_graph_file(file_path):
    """
    Parses a text file containing graph data and extracts nodes, edges, origin, and destinations.
    
    Args:
        file_path (str): Path to the text file containing the graph data.
    
    Returns:
        tuple: A tuple containing:
            - nodes (dict): Mapping of node IDs to coordinates {node_id: (x, y)}.
            - edges (dict): Mapping of edge pairs to weights {(node1, node2): weight}.
            - origin (str): The origin node.
            - destinations (set): List of destination nodes.
    """
    nodes = {}
    edges = {}
    origin = None
    destinations = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Nodes:"):
                section = "nodes"
                continue
            elif line.startswith("Edges:"):
                section = "edges"
                continue
            elif line.startswith("Origin:"):
                section = "origin"
                continue
            elif line.startswith("Destinations:"):
                section = "destinations"
                continue
            
            if section == "nodes":
                match = re.match(r"(\d+): \((\d+),(\d+)\)", line)
                if match:
                    node_id = str(match.group(1))
                    x, y = int(match.group(2)), int(match.group(3))
                    nodes[node_id] = (x, y)
            
            elif section == "edges":
                match = re.match(r"\((\d+),(\d+)\): (\d+)", line)
                if match:
                    node1, node2, weight = str(match.group(1)), str(match.group(2)), int(match.group(3))
                    edges[(node1, node2)] = weight
            
            elif section == "origin":
                origin = str(line)
            
            elif section == "destinations":
                destinations = list([d.strip() for d in line.split(';') if d.strip()])
    
    return nodes, edges, origin, destinations

# Example usage:
if __name__ == "__main__":
    file_path = "a.txt"  # Replace with your actual file name
    nodes, edges, origin, destinations = parse_graph_file(file_path)
    
    print("Nodes:", nodes)
    print("Edges:", edges)
    print("Origin:", origin)
    print("Destinations:", destinations)

    result_paths = []
    for dest in destinations:
        result_path = GBFS_search(graph, origin, dest, edges)
        result_paths.append(result_path)

    visualise(result_paths, nodes, edges)
