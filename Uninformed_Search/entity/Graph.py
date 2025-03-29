class Graph:
    """Represents a graph with nodes and weighted edges."""
    
    def __init__(self):
        self.nodes = []
        self.edges = {}
        self.adjacency_list = {}
    
    def load_from_data(self, nodes, edges):
        """Initialize graph from node and edge data."""
        self.nodes = nodes
        self.edges = edges
        self._build_adjacency_list()
        
    def _build_adjacency_list(self):
        """Build an adjacency list representation of the graph."""
        self.adjacency_list = {node: [] for node in self.nodes}
        for (src, tgt), weight in self.edges.items():
            self.adjacency_list[src].append((tgt, weight))
    
    def get_neighbors(self, node):
        """Get all neighbors of a node with their edge weights."""
        return self.adjacency_list.get(node, [])
    
    def node_count(self):
        """Return the number of nodes in the graph."""
        return len(self.nodes)