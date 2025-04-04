import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import heapq

class Node:
    def __init__(self, start, end, heuristic):
        self.start = start
        self.end = end
        self.heuristic = heuristic

    def __lt__(self,  other):
        return self.heuristic < other.heuristic
    
def find_smallest_heuristic(current, heuristic):
    heuristic_value = []
    for i in graph[current]:
        heapq.heappush(heuristic_value, Node(current, i, heuristic[(current, i)]))
        
    return heapq.heappop(heuristic_value)
        

def GBFS_search(graph, start, goal, heuristic):
    # Priority queue to hold nodes to explore, sorted by heuristic value
    priority_queue = []
    heapq.heappush(priority_queue, find_smallest_heuristic(start, heuristic))

    visited = set() # to keep track of visited nodes

    # path dictionary to track the explored paths
    path = {start:None}

    while priority_queue:
        current_node = heapq.heappop(priority_queue).start

        # if the goal is reached, reconstruct the path
        if current_node == goal:
            return reconstruct_path(path, start, goal)
        
        visited.add(current_node)

        # explore neighbors
        for neighbor in graph[current_node]:
            if neighbor not in visited:
                heapq.heappush(priority_queue, find_smallest_heuristic(neighbor, heuristic))
                if neighbor not in path:
                    path[neighbor] = current_node
    return None

def reconstruct_path(path, start, goal):
    current = goal
    result_path = []

    while current is not None:
        result_path.append(current)
        current = path[current]
    result_path.reverse()
    return result_path


def visualise(path, pos):
    fig, ax = plt.subplots()
    ax.set_xticks(range(11))
    ax.set_yticks(range(11))

    ax.grid(True, which='both', linestyle='-', linewidth=0.5)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # plot the edge
    for edge in edges_and_heuristic.keys():
        p1, p2 = edge

        x_values = [pos[p1][0], pos[p2][0]]
        y_values = [pos[p1][1], pos[p2][1]]

        ax.plot(x_values, y_values, marker='o', color='blue')

    # Annotate the points
    for point, coord in pos.items():
        ax.text(coord[0], coord[1], point, fontsize=12, color='black', ha='right')
    
    xpoints = []
    ypoints = []
    for i in range(len(path)):
        xpoints.append(pos[path[i]][0])
        ypoints.append(pos[path[i]][1])

    plt.plot(xpoints, ypoints, marker='o', color='red')
    plt.show()

graph = {
    '1': ['3','4'],
    '2': ['3','1'],
    '3': ['1','2','5','6'],
    '4': ['1','3','5'],
    '5': ['3','4'],
    '6': ['3']
}

pos = {
    '1': (4,1),
    '2': (2,2),
    '3': (4,4),
    '4': (6,3),
    '5': (5,6),
    '6': (7,5)
}

edges_and_heuristic = {
    ('2','1'): 4,
    ('3','1'): 5,
    ('1','3'): 5,
    ('2','3'): 4,
    ('3','2'): 5,
    ('4','1'): 6,
    ('1','4'): 6,
    ('4','3'): 5,
    ('3','5'): 6,
    ('5','3'): 6,
    ('4','5'): 7,
    ('5','4'): 8,
    ('6','3'): 7,
    ('3','6'): 7

}

origin = '3'
destination = '4'

result_path = GBFS_search(graph, origin, destination, edges_and_heuristic)

print("Path from {} to {}: {}".format(origin, destination, result_path))

visualise(result_path, pos)