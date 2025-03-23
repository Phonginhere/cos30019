import sys
import subprocess
import os
import importlib.util

def main():
    # Check if algorithm name is provided
    if len(sys.argv) < 2:
        print("Usage: python search.py <algorithm> [optional arguments]")
        print("Available algorithms: aco, bfs, dfs, astar, etc.")
        sys.exit(1)

    # Get the algorithm name from command line
    algorithm = sys.argv[1]

    # The remaining arguments
    remaining_args = sys.argv[2:]

    if algorithm == "CUS2":
        # Option 1: Use importlib to run the module function
        try:
            # Check if the module exists
            module_path = os.path.join(os.path.dirname(__file__), "Custom_Search", "aco_search.py")
            if os.path.exists(module_path):
                # Import the module
                spec = importlib.util.spec_from_file_location("aco_search", module_path)
                aco_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(aco_module)
                
                # Run the main function
                aco_module.main()
            else:
                print(f"Error: Module {module_path} not found!")
                sys.exit(1)
        except Exception as e:
            print(f"Error executing ACO search: {e}")
            sys.exit(1)
    
    elif algorithm == "BFS":
        # Add BFS implementation here
        print("BFS algorithm selected (not implemented yet)")
    
    elif algorithm == "DFS":
        # Add DFS implementation here
        print("DFS algorithm selected (not implemented yet)")
    
    elif algorithm == "AS":
        # Add A* implementation here
        print("A* algorithm selected (not implemented yet)")
        
    elif algorithm == "GBFS":
        # Add Greedy Best-First Search implementation here
        print("Greedy Best-First Search algorithm selected (not implemented yet)")
        
    elif algorithm == "CUS1":
        # Add Uniform Cost Search implementation here
        print("Uniform Cost Search algorithm selected (not implemented yet)")
        
    
    else:
        print(f"Unknown algorithm: {algorithm}")
        sys.exit(1)

if __name__ == "__main__":
    main()