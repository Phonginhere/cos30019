import os
import matplotlib.pyplot as plt
import numpy as np
import re
import pandas as pd
from pathlib import Path
import seaborn as sns
from collections import defaultdict

def parse_results_directory(results_dir):
    """
    Parse all algorithm results from the results directory.
    
    Returns:
        dict: Dictionary with algorithm names as keys and lists of test results as values
    """
    algorithm_results = {}
    
    # Find all summary result files
    summary_files = [f for f in os.listdir(results_dir) if f.startswith("summary_result_") and f.endswith(".txt")]
    
    if not summary_files:
        print(f"No summary result files found in {results_dir}")
        return {}
    
    print(f"Found {len(summary_files)} algorithm summary files")
    
    # Process each algorithm's summary file
    for summary_file in summary_files:
        # Extract algorithm name from filename
        algo_match = re.search(r'summary_result_([A-Za-z0-9]+)\.txt', summary_file)
        if not algo_match:
            continue
            
        algorithm = algo_match.group(1)
        results = []
        
        # Read and parse the summary file
        summary_path = os.path.join(results_dir, summary_file)
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract test results from markdown table
            table_pattern = r'\|\s*(\d+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*([\d\.]+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|'
            matches = re.findall(table_pattern, content)
            
            for match in matches:
                test_num = int(match[0])
                origin = match[1].strip()
                destinations = match[2].strip()
                time = float(match[3])
                
                # Check if the test was successful by looking at cost
                cost_str = match[4].strip()
                success = cost_str.lower() != "failed"
                cost = float(cost_str) if success else None
                
                path = match[5].strip() if success else None
                
                results.append({
                    "test_num": test_num,
                    "origin": origin,
                    "destinations": destinations,
                    "success": success,
                    "time": time,
                    "cost": cost,
                    "path": path
                })
                
            # Sort by test number
            results.sort(key=lambda x: x["test_num"])
            algorithm_results[algorithm] = results
            print(f"Parsed {len(results)} test results for {algorithm}")
            
        except Exception as e:
            print(f"Error parsing {summary_file}: {str(e)}")
    
    return algorithm_results

def create_algorithm_visualizations(algorithm, results, output_dir):
    """
    Create visualizations for a specific algorithm.
    """
    if not results:
        print(f"No results to visualize for {algorithm}")
        return
    
    # Create algorithm-specific directory
    algo_dir = os.path.join(output_dir, algorithm)
    os.makedirs(algo_dir, exist_ok=True)
    
    # Plot success/failure
    test_nums = [r["test_num"] for r in results]
    success_status = [1 if r["success"] else 0 for r in results]
    
    plt.figure(figsize=(12, 3))
    plt.bar(test_nums, success_status, color=['green' if s else 'red' for s in success_status])
    plt.yticks([0, 1], ['Failed', 'Success'])
    plt.xlabel('Test Case Number')
    plt.title(f'{algorithm} - Test Success/Failure')
    plt.grid(axis='x')
    plt.savefig(os.path.join(algo_dir, 'success_status.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot execution times
    plt.figure(figsize=(12, 6))
    plt.bar(test_nums, [r["time"] for r in results], 
            color=['green' if r["success"] else 'red' for r in results])
    plt.xlabel('Test Case Number')
    plt.ylabel('Execution Time (seconds)')
    plt.title(f'{algorithm} - Execution Time by Test Case')
    plt.grid(axis='y')
    plt.savefig(os.path.join(algo_dir, 'execution_times.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot costs for successful tests
    successful_tests = [r for r in results if r["success"] and r["cost"] is not None]
    if successful_tests:
        test_nums = [r["test_num"] for r in successful_tests]
        costs = [r["cost"] for r in successful_tests]
        
        plt.figure(figsize=(12, 6))
        plt.bar(test_nums, costs, color='blue')
        plt.xlabel('Test Case Number')
        plt.ylabel('Path Cost')
        plt.title(f'{algorithm} - Path Costs for Successful Tests')
        plt.grid(axis='y')
        plt.savefig(os.path.join(algo_dir, 'path_costs.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # Print a summary for this algorithm
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    avg_time = sum(r["time"] for r in results) / total_count if total_count > 0 else 0
    avg_cost = sum(r["cost"] for r in successful_tests) / len(successful_tests) if successful_tests else 0
    
    print(f"\n{algorithm} Results summary:")
    print(f"  Total tests: {total_count}")
    print(f"  Successful tests: {success_count} ({success_rate:.1f}%)")
    print(f"  Average execution time: {avg_time:.3f} seconds")
    print(f"  Average path cost: {avg_cost:.3f}")
    
    # Save summary to text file
    with open(os.path.join(algo_dir, 'summary.txt'), 'w') as f:
        f.write(f"{algorithm} Results Summary\n")
        f.write(f"Total tests: {total_count}\n")
        f.write(f"Successful tests: {success_count} ({success_rate:.1f}%)\n")
        f.write(f"Average execution time: {avg_time:.3f} seconds\n")
        f.write(f"Average path cost: {avg_cost:.3f}\n")
    
    return {
        'algorithm': algorithm,
        'total_tests': total_count,
        'success_count': success_count,
        'success_rate': success_rate,
        'avg_time': avg_time,
        'avg_cost': avg_cost
    }

def create_comparative_visualizations(all_results, output_dir):
    """
    Create visualizations comparing all algorithms.
    """
    if not all_results:
        print("No algorithms to compare")
        return
    
    # Create comparative directory
    comp_dir = os.path.join(output_dir, "Comparison")
    os.makedirs(comp_dir, exist_ok=True)
    
    # Convert results to a format suitable for visualization
    algorithms = list(all_results.keys())
    
    # Create a DataFrame with all test results for easy manipulation
    all_data = []
    for algorithm in algorithms:
        for result in all_results[algorithm]:
            all_data.append({
                'Algorithm': algorithm,
                'Test': result['test_num'],
                'Success': result['success'],
                'Time': result['time'],
                'Cost': result['cost'] if result['success'] else float('nan')
            })
    
    df = pd.DataFrame(all_data)
    
    # 1. Success rate comparison
    success_rates = df.groupby('Algorithm')['Success'].mean() * 100
    plt.figure(figsize=(10, 6))
    success_rates.plot(kind='bar', color='green')
    plt.title('Success Rate by Algorithm')
    plt.xlabel('Algorithm')
    plt.ylabel('Success Rate (%)')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, 'success_rate_comparison.png'), dpi=300)
    plt.close()
    
    # 2. Execution time comparison
    plt.figure(figsize=(12, 8))
    
    # Box plot
    plt.subplot(2, 1, 1)
    sns.boxplot(x='Algorithm', y='Time', data=df)
    plt.title('Execution Time Distribution by Algorithm')
    plt.ylabel('Time (seconds)')
    plt.grid(axis='y')
    
    # Average time
    plt.subplot(2, 1, 2)
    avg_times = df.groupby('Algorithm')['Time'].mean().sort_values()
    avg_times.plot(kind='bar', color='blue')
    plt.title('Average Execution Time by Algorithm')
    plt.ylabel('Time (seconds)')
    plt.grid(axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, 'execution_time_comparison.png'), dpi=300)
    plt.close()
    
    # 3. Path cost comparison (only for successful tests)
    success_df = df[df['Success'] == True].dropna(subset=['Cost'])
    
    if not success_df.empty:
        plt.figure(figsize=(12, 8))
        
        # Box plot
        plt.subplot(2, 1, 1)
        sns.boxplot(x='Algorithm', y='Cost', data=success_df)
        plt.title('Path Cost Distribution by Algorithm (Successful Tests)')
        plt.ylabel('Path Cost')
        plt.grid(axis='y')
        
        # Average cost
        plt.subplot(2, 1, 2)
        avg_costs = success_df.groupby('Algorithm')['Cost'].mean().sort_values()
        avg_costs.plot(kind='bar', color='purple')
        plt.title('Average Path Cost by Algorithm')
        plt.ylabel('Path Cost')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.savefig(os.path.join(comp_dir, 'path_cost_comparison.png'), dpi=300)
        plt.close()
    
    # 4. Create a heatmap of success by algorithm and test case
    success_matrix = pd.pivot_table(
        df, 
        values='Success', 
        index='Algorithm', 
        columns='Test', 
        aggfunc=lambda x: int(any(x))
    ).fillna(0)
    
    plt.figure(figsize=(14, len(algorithms) * 0.8))
    sns.heatmap(success_matrix, cmap=['red', 'green'], cbar=False, 
                linewidths=.5, annot=True, fmt='d')
    plt.title('Test Success by Algorithm and Test Case')
    plt.savefig(os.path.join(comp_dir, 'success_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Direct algorithm comparison for each test case (execution time)
    pivot_time = pd.pivot_table(
        df, 
        values='Time', 
        index='Test', 
        columns='Algorithm'
    )
    
    plt.figure(figsize=(14, 8))
    pivot_time.plot(kind='bar')
    plt.title('Execution Time Comparison by Test Case')
    plt.xlabel('Test Case Number')
    plt.ylabel('Time (seconds)')
    plt.grid(axis='y')
    plt.legend(title='Algorithm')
    plt.savefig(os.path.join(comp_dir, 'time_by_test.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Radar chart of algorithm performance metrics
    # Create a summary DataFrame
    summaries = []
    for algorithm, results in all_results.items():
        success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
        avg_time = sum(r["time"] for r in results) / len(results)
        successful_results = [r for r in results if r["success"] and r["cost"] is not None]
        avg_cost = sum(r["cost"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        # For radar chart, lower is better for time and cost
        # Normalize time and cost so that lower values are better (1.0 is best)
        summaries.append({
            'Algorithm': algorithm,
            'Success Rate': success_rate,
            'Speed': 1.0 / (avg_time + 0.001),  # Invert so higher is better
            'Efficiency': 1.0 / (avg_cost + 0.001) if avg_cost > 0 else 0  # Invert so higher is better
        })
    
    summary_df = pd.DataFrame(summaries)
    
    # Normalize the metrics for better visualization
    for col in ['Success Rate', 'Speed', 'Efficiency']:
        if summary_df[col].max() > 0:
            summary_df[col] = summary_df[col] / summary_df[col].max() * 100
    
    # Create radar chart
    labels = ['Success Rate', 'Speed', 'Efficiency']
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    for i, algorithm in enumerate(summary_df['Algorithm']):
        values = summary_df.loc[summary_df['Algorithm'] == algorithm, labels].values.flatten().tolist()
        values += values[:1]  # Close the loop
        
        ax.plot(angles, values, linewidth=2, label=algorithm)
        ax.fill(angles, values, alpha=0.1)
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 105)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Algorithm Performance Comparison', size=20, y=1.05)
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, 'algorithm_radar.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. Create a summary markdown table
    with open(os.path.join(comp_dir, 'summary_comparison.md'), 'w') as f:
        f.write("# Algorithm Performance Comparison\n\n")
        f.write("| Algorithm | Success Rate | Avg Time (s) | Avg Cost |\n")
        f.write("|-----------|--------------|--------------|----------|\n")
        
        for algorithm, results in all_results.items():
            success_count = sum(1 for r in results if r["success"])
            total_count = len(results)
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            avg_time = sum(r["time"] for r in results) / total_count if total_count > 0 else 0
            
            successful_results = [r for r in results if r["success"] and r["cost"] is not None]
            avg_cost = sum(r["cost"] for r in successful_results) / len(successful_results) if successful_results else 0
            
            f.write(f"| {algorithm} | {success_rate:.1f}% | {avg_time:.3f} | {avg_cost:.3f} |\n")

def main():
    project_root = Path(__file__).parent.parent
    results_dir = project_root / "Tests" / "Results"
    output_dir = project_root / "Tests" / "Visualizations"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse all algorithm results
    all_results = parse_results_directory(results_dir)
    
    if not all_results:
        print("No algorithm results found")
        return
    
    # Process each algorithm's results
    algorithm_summaries = []
    for algorithm, results in all_results.items():
        summary = create_algorithm_visualizations(algorithm, results, output_dir)
        algorithm_summaries.append(summary)
    
    # Create comparative visualizations
    create_comparative_visualizations(all_results, output_dir)
    
    print(f"\nAll visualizations saved to {output_dir}")
    print("Individual algorithm visualizations are in algorithm-specific folders")
    print("Comparative visualizations are in the 'Comparison' folder")

if __name__ == "__main__":
    main()