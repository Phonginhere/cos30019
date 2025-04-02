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

### Running the Search Algorithms

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
