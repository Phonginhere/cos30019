# This script generates all edges for a complete graph with nodes
# Each node is connected to every other node bidirectionally
# Edge costs are calculated as Euclidean distances

import math
import os
import sys
import re

# Function to calculate Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Read the node data from file
def read_nodes_from_file(filename):
    nodes = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                # Try parsing different formats
                # Format 1: "node_id x y"
                parts = line.split()
                if len(parts) == 3:
                    try:
                        node_id = int(parts[0])
                        x = int(parts[1])
                        y = int(parts[2])
                        nodes.append({"id": node_id, "x": x, "y": y})
                        continue
                    except ValueError:
                        pass
                
                # Format 2: "node_id: (x, y)"
                match = re.match(r'(\d+)\s*:\s*\((\d+),\s*(\d+)\)', line)
                if match:
                    try:
                        node_id = int(match.group(1))
                        x = int(match.group(2))
                        y = int(match.group(3))
                        nodes.append({"id": node_id, "x": x, "y": y})
                        continue
                    except ValueError:
                        pass
                
                print(f"Warning: Couldn't parse line: {line}")
        
        print(f"Successfully parsed {len(nodes)} nodes from {filename}")
        
        if len(nodes) == 0:
            print("Error: No valid nodes found in the input file.")
            print("Ensure the file contains nodes in one of these formats:")
            print("  Format 1: 'node_id x y'        Example: '1 7810 6053'")
            print("  Format 2: 'node_id: (x, y)'    Example: '1: (7810, 6053)'")
    
    except FileNotFoundError:
        print(f"Error: Could not find input file: {filename}")
        print(f"Current working directory: {os.getcwd()}")
        print("Make sure the file exists and the path is correct.")
    
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return nodes

# Create directory if it doesn't exist
def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    return True

# Generate all edges and save to file
def generate_and_save_edges(nodes_file, output_file):
    nodes = read_nodes_from_file(nodes_file)
    
    if not nodes:
        print("No nodes to process. Exiting.")
        return
    
    # Ensure the output directory exists
    if not ensure_directory_exists(output_file):
        print(f"Could not ensure directory exists for {output_file}")
        return
    
    try:
        with open(output_file, 'w') as edges_file:
            edges_file.write("Edges:\n")
            
            edge_count = 0
            total_edges = len(nodes) * (len(nodes) - 1)
            
            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    # Skip self-connections
                    if i == j:
                        continue
                    
                    node1 = nodes[i]
                    node2 = nodes[j]
                    distance = calculate_distance(node1["x"], node1["y"], node2["x"], node2["y"])
                    # Round to integer for simplicity
                    cost = round(distance)
                    
                    edges_file.write(f"({node1['id']},{node2['id']}): {cost}\n")
                    edge_count += 1
                    
                    # Log progress
                    if edge_count % 50000 == 0:
                        percentage = (edge_count / total_edges) * 100
                        print(f"Generated {edge_count} edges so far... ({percentage:.1f}%)")
            
            print(f"Generated and saved {edge_count} edges to {output_file}")
    
    except Exception as e:
        print(f"Error generating edges: {e}")

# If you want to run this as a standalone script
if __name__ == "__main__":
    # Allow command line arguments for filenames
    if len(sys.argv) > 2:
        nodes_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Default filenames
        nodes_file = 'Data/TSP_Test_case_4.txt'
        output_file = 'Data/all_edges.txt'
    
    print(f"Input file: {nodes_file}")
    print(f"Output file: {output_file}")
    
    generate_and_save_edges(nodes_file, output_file)