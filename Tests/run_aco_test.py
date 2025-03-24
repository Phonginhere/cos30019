import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def run_test(test_file_path):
    """
    Run ACO algorithm on the given test file and return the results.
    """
    start_time = time.time()
    
    # Run the ACO algorithm on the test file
    cmd = [sys.executable, 
           str(project_root / "Custom_Search" / "aco_search.py"), 
           test_file_path]
    
    try:
        result = subprocess.run(cmd, 
                               capture_output=True, 
                               text=True, 
                               timeout=60) # 60 second timeout
        
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "execution_time": execution_time
            }
        
        # Parse the output
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) < 3:
            return {
                "success": False,
                "error": "Incomplete output from ACO algorithm",
                "output": result.stdout,
                "execution_time": execution_time
            }
        
        algorithm_info = output_lines[0]
        goal_info = output_lines[1]
        path = output_lines[2]
        cost = output_lines[3] if len(output_lines) > 3 else "N/A"
        
        return {
            "success": True,
            "algorithm_info": algorithm_info,
            "goal_info": goal_info,
            "path": path,
            "cost": cost,
            "execution_time": execution_time
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Test timed out after 60 seconds",
            "execution_time": 60
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time
        }

def main():
    # Create test results directory if it doesn't exist
    results_dir = project_root / "Tests" / "Results"
    results_dir.mkdir(exist_ok=True)
    
    # Get list of all test files
    test_cases_dir = project_root / "Tests" / "TestCases"
    test_files = sorted([f for f in test_cases_dir.glob("*.txt")])
    
    if not test_files:
        print("No test files found in", test_cases_dir)
        return
    
    # Run tests and collect results
    results = []
    total_tests = len(test_files)
    success_count = 0
    
    for i, test_file in enumerate(test_files, 1):
        print(f"Running test {i}/{total_tests}: {test_file.name}")
        result = run_test(str(test_file))
        result["test_file"] = test_file.name
        results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"  ✓ Success (Time: {result['execution_time']:.3f}s, Cost: {result['cost']})")
        else:
            print(f"  ✗ Failed: {result['error']}")
    
    # Generate summary report
    with open(results_dir / "summary_report.txt", "w") as f:
        f.write(f"# ACO Algorithm Test Results\n")
        f.write(f"Tests run: {total_tests}\n")
        f.write(f"Successful: {success_count}\n")
        f.write(f"Failed: {total_tests - success_count}\n\n")
        
        for result in results:
            f.write(f"## Test: {result['test_file']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Execution time: {result['execution_time']:.3f} seconds\n")
            
            if result['success']:
                f.write(f"Algorithm info: {result['algorithm_info']}\n")
                f.write(f"Goal info: {result['goal_info']}\n")
                f.write(f"Path: {result['path']}\n")
                f.write(f"Cost: {result['cost']}\n")
            else:
                f.write(f"Error: {result['error']}\n")
            
            f.write("\n")
    
    # Generate detailed individual reports
    for result in results:
        test_name = Path(result["test_file"]).stem
        with open(results_dir / f"{test_name}_report.txt", "w") as f:
            f.write(f"# Test Results for {result['test_file']}\n\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Execution time: {result['execution_time']:.3f} seconds\n\n")
            
            if result['success']:
                f.write(f"Algorithm info: {result['algorithm_info']}\n")
                f.write(f"Goal info: {result['goal_info']}\n")
                f.write(f"Path: {result['path']}\n")
                f.write(f"Cost: {result['cost']}\n")
            else:
                f.write(f"Error: {result['error']}\n")
                if 'output' in result:
                    f.write(f"\nPartial output:\n{result['output']}\n")
    
    print(f"\nTesting complete. {success_count}/{total_tests} tests passed.")
    print(f"See {results_dir} for detailed results.")

if __name__ == "__main__":
    main()