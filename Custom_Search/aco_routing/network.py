class Network:
    def __init__(self):
        self.graph = {}  # Stores adjacency list: node -> list of neighbors
        self.edges = {}  # Stores edge attributes: (u,v) -> attribute dict

    def add_edge(self, u, v, **attr):
        """Add an edge between u and v with optional attributes."""
        # Ensure nodes exist in the graph
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
            
        # Add v to u's neighbors if not already present
        if v not in self.graph[u]:
            self.graph[u].append(v)
            
        # Store edge attributes
        self.edges[(u, v)] = attr

    def number_of_nodes(self):
        """Return the number of nodes in the graph."""
        return len(self.graph)

    def number_of_edges(self):
        """Return the number of edges in the graph."""
        return len(self.edges)

    def nodes(self):
        """Return an iterator over the graph nodes."""
        return self.graph.keys()

    def neighbors(self, node):
        """Return a list of the node's neighbors."""
        return self.graph.get(node, [])

    def get_edge_data(self, u, v):
        """Return the attribute dictionary associated with edge (u,v)."""
        return self.edges.get((u, v), {})

    def has_edge(self, u, v):
        """Return True if the edge (u,v) is in the graph."""
        return (u, v) in self.edges
    
    def get_edge_attributes(self, attribute_name):
        """Returns a dictionary mapping edge tuples to attribute values."""
        return {edge: data.get(attribute_name, None) 
                for edge, data in self.edges.items() 
                if attribute_name in data}
                
    def get_edges(self, data=False):
        """Returns a list of edges, optionally with data."""
        if data:
            return [(u, v, self.edges[u, v]) for u, v in self.edges]
        else:
            return list(self.edges.keys())
            
    def __getitem__(self, node):
        """Allow dictionary-like access to node attributes."""
        if node in self.graph:
            # Create a NodeDict that simulates NetworkX node access
            return NodeDict(self, node)
        raise KeyError(f"Node {node} not in graph")
        
    def draw(self, pos, **kwargs):
        # Placeholder for drawing method
        pass

    def draw_networkx_nodes(self, pos, **kwargs):
        # Placeholder for drawing nodes method
        pass

    def draw_networkx_edges(self, pos, **kwargs):
        # Placeholder for drawing edges method
        pass

    def draw_networkx_labels(self, pos, **kwargs):
        # Placeholder for drawing labels method
        pass

    def draw_networkx_edge_labels(self, pos, edge_labels, **kwargs):
        # Placeholder for drawing edge labels method
        pass

    def spring_layout(self, **kwargs):
        """Return a dictionary of node positions in 2D."""
        pos = {}
        # Simple grid layout for visualization
        cols = max(int(len(self.graph) ** 0.5) + 1, 3)
        for i, node in enumerate(self.graph):
            row = i // cols
            col = i % cols
            # Add some jitter for better visualization
            jitter_x = (hash(str(node)) % 100) / 500
            jitter_y = (hash(str(node) + '1') % 100) / 500
            pos[node] = (col + jitter_x, row + jitter_y)
        return pos


class NodeDict:
    """Helper class to simulate NetworkX node dictionary access."""
    def __init__(self, network, node):
        self.network = network
        self.node = node
        
    def __getitem__(self, neighbor):
        """Allow access to edge attributes like: G[node1][node2]['attribute']"""
        if neighbor in self.network.neighbors(self.node):
            return self.network.edges.get((self.node, neighbor), {})
        raise KeyError(f"No edge from {self.node} to {neighbor}")