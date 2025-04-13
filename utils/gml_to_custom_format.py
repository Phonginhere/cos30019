import re
import random
import os
import sys

def parse_gml(gml_file_path):
    """Parse the GML file and extract nodes and edges"""
    with open(gml_file_path, 'r') as file:
        content = file.read()
    
    # Extract nodes
    nodes = {}
    node_pattern = r'node\s*\[\s*id\s+(\d+)\s+label\s+"([^"]+)"\s*\]'
    for match in re.finditer(node_pattern, content):
        node_id = int(match.group(1))
        label = match.group(2)
        nodes[node_id] = label
    
    # Extract edges
    edges = []
    edge_pattern = r'edge\s*\[\s*source\s+(\d+)\s+target\s+(\d+)\s+value\s+(\d+)\s*\]'
    for match in re.finditer(edge_pattern, content):
        source = int(match.group(1))
        target = int(match.group(2))
        value = int(match.group(3))
        edges.append((source, target, value))
    
    return nodes, edges

def generate_random_coordinates(nodes, scale=100):
    """Generate random x,y coordinates for each node"""
    node_coords = {}
    for node_id in nodes:
        x = random.randint(1, scale)
        y = random.randint(1, scale)
        node_coords[node_id] = (x, y)
    return node_coords

def write_custom_format(output_file_path, nodes, edges, node_coords):
    """Write the data in the custom format"""
    with open(output_file_path, 'w') as file:
        # Write header
        file.write(f"### Converted from {os.path.basename(gml_file_path)}\n")
        
        # Write nodes
        file.write("Nodes:\n")
        for node_id in sorted(nodes.keys()):
            label = nodes[node_id]
            x, y = node_coords[node_id]
            file.write(f"{label}: ({x},{y})\n")
        
        # Write edges
        file.write("Edges:\n")
        for source, target, value in edges:
            source_label = nodes[source]
            target_label = nodes[target]
            file.write(f"({source_label},{target_label}): {value}\n")
        
        # Write placeholder for Origin and Destinations
        file.write("Origin:\n1\n")
        file.write("Destinations:\n2; 3\n")
        
        print(f"Conversion complete. Output written to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gml_to_custom_format.py <path_to_gml_file>")
        gml_file_path = "celegansneural.gml"  # Default if no argument provided
    else:
        gml_file_path = sys.argv[1]
    
    output_file_path = os.path.splitext(gml_file_path)[0] + "_converted.txt"
    
    print(f"Converting {gml_file_path} to custom format...")
    nodes, edges = parse_gml(gml_file_path)
    node_coords = generate_random_coordinates(nodes)
    write_custom_format(output_file_path, nodes, edges, node_coords)
