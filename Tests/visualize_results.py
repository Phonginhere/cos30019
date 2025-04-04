import os
import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path

def parse_results_directory(results_dir):
    """
    Parse all test results from the results directory.
    """
    results = []
    
    # Parse summary report to get basic info
    summary_path = os.path.join(results_dir, "summary_report.txt")
    if not os.path.exists(summary_path):
        print(f"Summary report not found at {summary_path}")
        return []
    
    # Get all individual test reports
    for file in os.listdir(results_dir):
        if file.startswith("test_case_") and file.endswith("_report.txt"):
            report_path = os.path.join(results_dir, file)
            
            # Extract test case number
            match = re.search(r'test_case_(\d+)', file)
            if not match:
                continue
            
            test_num = int(match.group(1))
            
            # Parse the report
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Extract key information
            success_match = re.search(r'Success: (True|False)', content)
            time_match = re.search(r'Execution time: ([\d\.]+)', content)
            cost_match = re.search(r'Cost: ([\d\.]+)', content)
            
            success = success_match.group(1) == "True" if success_match else False
            time = float(time_match.group(1)) if time_match else 0
            cost = float(cost_match.group(1)) if cost_match and success else None
            
            results.append({
                "test_num": test_num,
                "success": success,
                "time": time,
                "cost": cost
            })
    
    # Sort by test number
    results.sort(key=lambda x: x["test_num"])
    return results

def create_visualizations(results, output_dir):
    """
    Create visualizations of the test results.
    """
    if not results:
        print("No results to visualize")
        return
    
    # Create execution time chart
    plt.figure(figsize=(12, 6))
    
    # Split into groups
    easy_tests = [r for r in results if 1 <= r["test_num"] <= 10]
    medium_tests = [r for r in results if 11 <= r["test_num"] <= 20]
    hard_tests = [r for r in results if 21 <= r["test_num"] <= 30]
    
    # Plot success/failure
    test_nums = [r["test_num"] for r in results]
    success_status = [1 if r["success"] else 0 for r in results]
    
    plt.figure(figsize=(12, 3))
    plt.bar(test_nums, success_status, color=['green' if s else 'red' for s in success_status])
    plt.yticks([0, 1], ['Failed', 'Success'])
    plt.xlabel('Test Case Number')
    plt.title('Test Success/Failure')
    plt.grid(axis='x')
    plt.savefig(os.path.join(output_dir, 'success_status.png'), dpi=300, bbox_inches='tight')
    
    # Plot execution times
    plt.figure(figsize=(12, 6))
    
    easy_times = [r["time"] for r in easy_tests]
    medium_times = [r["time"] for r in medium_tests]
    hard_times = [r["time"] for r in hard_tests]
    
    easy_nums = [r["test_num"] for r in easy_tests]
    medium_nums = [r["test_num"] for r in medium_tests]
    hard_nums = [r["test_num"] for r in hard_tests]
    
    plt.bar(easy_nums, easy_times, color='green', label='Easy')
    plt.bar(medium_nums, medium_times, color='orange', label='Medium')
    plt.bar(hard_nums, hard_times, color='red', label='Hard')
    
    plt.xlabel('Test Case Number')
    plt.ylabel('Execution Time (seconds)')
    plt.title('ACO Algorithm Execution Time by Test Case')
    plt.legend()
    plt.grid(axis='y')
    plt.savefig(os.path.join(output_dir, 'execution_times.png'), dpi=300, bbox_inches='tight')
    
    # Plot costs for successful tests
    plt.figure(figsize=(12, 6))
    
    successful_tests = [r for r in results if r["success"] and r["cost"] is not None]
    if successful_tests:
        test_nums = [r["test_num"] for r in successful_tests]
        costs = [r["cost"] for r in successful_tests]
        
        # Separate by difficulty
        easy_successful = [r for r in successful_tests if 1 <= r["test_num"] <= 10]
        medium_successful = [r for r in successful_tests if 11 <= r["test_num"] <= 20]
        hard_successful = [r for r in successful_tests if 21 <= r["test_num"] <= 30]
        
        easy_nums = [r["test_num"] for r in easy_successful]
        medium_nums = [r["test_num"] for r in medium_successful]
        hard_nums = [r["test_num"] for r in hard_successful]
        
        easy_costs = [r["cost"] for r in easy_successful]
        medium_costs = [r["cost"] for r in medium_successful]
        hard_costs = [r["cost"] for r in hard_successful]
        
        plt.bar(easy_nums, easy_costs, color='green', label='Easy')
        plt.bar(medium_nums, medium_costs, color='orange', label='Medium')
        plt.bar(hard_nums, hard_costs, color='red', label='Hard')
        
        plt.xlabel('Test Case Number')
        plt.ylabel('Path Cost')
        plt.title('ACO Algorithm Path Costs for Successful Tests')
        plt.legend()
        plt.grid(axis='y')
        plt.savefig(os.path.join(output_dir, 'path_costs.png'), dpi=300, bbox_inches='tight')
    
    print(f"Visualizations saved to {output_dir}")

def main():
    project_root = Path(__file__).parent.parent
    results_dir = project_root / "Tests" / "ACO_Results"
    output_dir = project_root / "Tests" / "Visualizations"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    results = parse_results_directory(results_dir)
    create_visualizations(results, output_dir)
    
    # Print a summary
    if results:
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)
        avg_time = sum(r["time"] for r in results) / total_count if total_count > 0 else 0
        
        print(f"Results summary:")
        print(f"  Total tests: {total_count}")
        print(f"  Successful tests: {success_count} ({success_count/total_count*100:.1f}%)")
        print(f"  Average execution time: {avg_time:.3f} seconds")

if __name__ == "__main__":
    main()