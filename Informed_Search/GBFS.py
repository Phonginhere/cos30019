import matplotlib.pyplot as plt
import numpy as np
import heapq
import re
import sys, os

# Import parser to read the graph file
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "..", "data_reader"))
from parser import parse_graph_file


# Import Network class from custom search directory
aco_routing_dir = os.path.join(current_dir, '..', "Custom_Search", "aco_routing")
sys.path.append(aco_routing_dir)

from network import Network

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
    if heuristic_value == None:
        return None
    print("Heuristic value:", heuristic_value[0])
    return heapq.heappop(heuristic_value)
        

def GBFS_search(graph, start, goal, heuristic):
    # path dictionary to track the explored paths
    path = {start:None}

    visited = set() # to keep track of visited nodes

    # Priority queue to hold nodes to explore, sorted by heuristic value
    priority_queue = []
    first = Node(start, 0)
    heapq.heappush(priority_queue, first)
    print("Current node:", first.start)

    while priority_queue:
        current_node = heapq.heappop(priority_queue).start
        
        visited.add(current_node)

        # if the goal is reached, reconstruct the path
        for i in goal:
            if i in visited:
                return reconstruct_path(path, start, goal)

        # find next node
        
        next_node = find_next_node(graph, current_node, heuristic, visited)
        print("Next node:", next_node.start)
        if next_node == None:
            continue
        else:
            heapq.heappush(priority_queue, next_node)
            if next_node.start not in path:
                path[next_node.start] = current_node
        
    return None

def reconstruct_path(path, start, goal):
    current = goal
    result_path = []

    while current is not None:
        result_path.append(current)
        current = path[current]
        # print(f"Result path: {result_path}")
    result_path.reverse()
    # print("Path from {} to {}: {}".format(start, goal, result_path))
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

def main():
    # Check if file path is provided as command line argument
    # if len(sys.argv) >= 2:
    #     file_path = sys.argv[1]
    # else:
    #     # Default file for testing
    #     file_path = os.path.join("..", "Data", "Modified_TSP", "test_27.txt")
    
    file_path = "Data/Modified_TSP/test_11.txt"

    # Parse the file
    nodes, edges, origin, destinations = parse_graph_file(file_path)
    
    # Create Data Structure    
    G = Network()
    G.graph = {node: [] for node in nodes}
    
    # Add edges 
    for (start, end), weight in edges.items():
        G.add_edge(start, end, cost=float(weight))
    

    print("Graph:", G.graph)
    result_paths = []
    result_path = GBFS_search(G.graph, origin, destinations, edges)

    result_paths.append(result_path)

    path_weights = []
    
    for path in result_paths:
        weight = 0
        for i in range(len(path)-1):
            weight += edges[(path[i], path[i+1])]
        path_weights.append(weight)
    
    # Pick the shortest path
    min_weight = min(path_weights)
    min_index = path_weights.index(min_weight)
    
    # Print the results
    print(f"{file_path} GBFS")
    print(f"{destinations} {len(nodes)}")
    print(f"{result_paths[min_index]}")
    print(f"{min_weight}")
    
    # Optionally visualize
    # visualise(result_paths, nodes, edges)

# Example usage:
if __name__ == "__main__":
    main()
