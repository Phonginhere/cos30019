# COS30019: Introduction to Artificial Intelligence

This repository contains the implementation of various search algorithms for path finding problems, created collaboratively by our team.

## Search Algorithms

### Uninformed Search Algorithms
1. **BFS (Breadth-First Search)** - Implemented by Phong
2. **DFS (Depth-First Search)** - Implemented by Phong

### Informed Search Algorithms
1. **GBFS (Greedy Best-First Search)** - Implemented by Tuan
2. **AS (A* Search)** - Implemented by Tuan

### Custom Search Algorithms
1. **CUS1 (Dijkstras Algorithm Search)** - Implemented by Phong
2. **CUS2 (Ant Colony Optimization)** - Implemented by Pink

## Usage

### Running the search.py main file

You can run any of the search algorithms from the command line using:

```bash
python search.py <algorithm> [optional arguments]
```

Where `<algorithm>` is one of:
- `BFS` - Breadth-First Search
- `DFS` - Depth-First Search
- `GBFS` - Greedy Best-First Search
- `AS` - A* Search
- `CUS1` - Uniform Cost Search
- `CUS2` - Ant Colony Optimization

### Example:

```bash
python search.py CUS2
```

### Requirements
- Python 3.6+ 
- Matplotlib

### Installation:
```bash
pip install matplotlib
```
#### Implementation Details

The ACO implementation includes several advanced features:

1. **Optimization Modes**:
   - Mode 0: Find any path to a single destination (if multi destinations provided, it will return shortest destination)
   - Mode 1: Find paths to all destinations (From source -> all destination)
   - Mode 2: Solve TSP (visit all nodes with minimal cost/ Random spawn)

2. **Parameter Tuning**:
   - `alpha`: Controls pheromone importance (default: 1)
   - `beta`: Controls heuristic information importance (default: 2)
   - `evaporation_rate`: Learning rate of gradient descent (default: 0.5)

3. **Performance Optimizations**:
   - Edge cost caching: Pre-computes and stores edge costs
   - Neighbor caching: Pre-computes and stores neighbor lists
   - Desirability caching: Stores repeated calculations for path selection

4. **Visualization**:
   - Real-time algorithm progress visualization
   - Pheromone level indication (red: high, green: low)
   - Path highlighting with node and edge details

#### Advanced Configuration

For advanced usage, you can modify the parameters in the `aco_search.py` file:

```python
# Key parameters to adjust
ant_max_steps = node_count + 1  # Maximum steps an ant can take
iterations = 2000               # Number of algorithm iterations
"""
I suggest that the iterations can be set from range 300-2000 depend on the complexity of problem and how well solution you want. For TSP ~~ 50 nodes, normally the Algorithm will convergence from iteration 300-500 and start to micro adjust from 500-2000.
"""
num_ants = node_count           # Number of ants to deploy
alpha = 1                       # Pheromone influence factor
beta = 2                        # Heuristic influence factor
evaporation_rate = 0.5          # Learning rate, the smaller evaporation_rate the bigger pheromone update (1/evaporation_rate)
```

#### Visualization Controls

The ACO visualization shows:

- **Nodes**: Path nodes (red) and unused nodes (light blue, 20% opacity)
- **Edges**: Colored by pheromone level (red = high, green = low)
- **Path**: Highlighted with increased opacity and width
- **Information**: Edge costs and pheromone levels shown on path edges
- **Progress**: Current iteration and best path cost

To adjust visualization:
```python
aco = ACO(
    # ... other parameters ...
    visualize=True,              # Enable/disable visualization
    visualization_step=10        # Update frequency (iterations)
)