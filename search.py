import sys
import subprocess
import os
import importlib.util
import traceback

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
            # Get paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            custom_search_dir = os.path.join(current_dir, "Custom_Search")
            module_path = os.path.join(custom_search_dir, "aco_search.py")
            
            # Add Custom_Search directory to sys.path so its modules can be found
            if custom_search_dir not in sys.path:
                sys.path.insert(0, custom_search_dir)
            
            # Check if the module exists
            if os.path.exists(module_path):
                print(f"Loading ACO module from: {module_path}")
                
                # Import the module
                spec = importlib.util.spec_from_file_location("aco_search", module_path)
                aco_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(aco_module)
                
                # Pass remaining args to sys.argv for the module to access
                # Save original argv
                original_argv = sys.argv.copy()
                
                # Update argv to pass the input file path if provided
                if remaining_args:
                    sys.argv = [module_path] + remaining_args
                else:
                    sys.argv = [module_path]
                
                # Run the main function
                aco_module.main()
                
                # Restore original argv
                sys.argv = original_argv
            else:
                print(f"Error: Module {module_path} not found!")
                sys.exit(1)
        except Exception as e:
            print(f"Error executing ACO search: {e}")
            traceback.print_exc()  # Print the full stack trace for debugging
            sys.exit(1)
    
    elif algorithm == "BFS":
        print("Breadth-First Search")
        # Add BFS implementation here
        try:
            # Get paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bfs_path = os.path.join(current_dir, "Uninformed_Search", "bfs.py")
            
            # Add Uninformed_Search directory to sys.path
            uninformed_search_dir = os.path.join(current_dir, "Uninformed_Search")
            if uninformed_search_dir not in sys.path:
                sys.path.insert(0, uninformed_search_dir)
            
            # Check if the module exists
            if os.path.exists(bfs_path):
                print(f"Loading BFS module from: {bfs_path}")
                
                # Import the module
                spec = importlib.util.spec_from_file_location("bfs", bfs_path)
                bfs_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bfs_module)
                
                # Save original argv
                original_argv = sys.argv.copy()
                
                # Update argv to pass the input file path if provided
                if remaining_args:
                    sys.argv = [bfs_path] + remaining_args
                else:
                    sys.argv = [bfs_path]
                
                # Execute the BFS code (it runs automatically when imported)
                
                # Restore original argv
                sys.argv = original_argv
            else:
                print(f"Error: BFS module {bfs_path} not found!")
                sys.exit(1)
        except Exception as e:
            print(f"Error executing BFS search: {e}")
            traceback.print_exc()
            sys.exit(1)
    
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
        print("CUS1")
        # Add Uniform Cost Search implementation here
        try:
            # Get paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bfs_path = os.path.join(current_dir, "Custom_Search", "Dijkstras_Algorithm", "dijk.py")
            
            # Add Custom Search directory to sys.path
            uninformed_search_dir = os.path.join(current_dir, "Dijkstras_Algorithm")
            if uninformed_search_dir not in sys.path:
                sys.path.insert(0, uninformed_search_dir)
            
            # Check if the module exists
            if os.path.exists(bfs_path):
                print(f"Loading Dijkstras module from: {bfs_path}")
                
                # Import the module
                spec = importlib.util.spec_from_file_location("bfs", bfs_path)
                bfs_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bfs_module)
                
                # Save original argv
                original_argv = sys.argv.copy()
                
                # Update argv to pass the input file path if provided
                if remaining_args:
                    sys.argv = [bfs_path] + remaining_args
                else:
                    sys.argv = [bfs_path]
                
                # Execute the BFS code (it runs automatically when imported)
                
                # Restore original argv
                sys.argv = original_argv
            else:
                print(f"Error: BFS module {bfs_path} not found!")
                sys.exit(1)
        except Exception as e:
            print(f"Error executing BFS search: {e}")
            traceback.print_exc()
            sys.exit(1)
        
    else:
        print(f"Unknown algorithm: {algorithm}")
        sys.exit(1)

if __name__ == "__main__":
    main()