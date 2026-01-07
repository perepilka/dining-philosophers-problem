#!/usr/bin/env python3
"""
Automated testing script for Dining Philosophers Problem
Runs tests for different configurations and collects statistics
"""

import subprocess
import re
import time
import csv
from datetime import datetime

# Test configurations
STRATEGIES = ['deadlock', 'hierarchy', 'asymmetric']
NUM_PHILOSOPHERS_LIST = [3, 5, 16, 32]
SIMULATION_TIME = 60  # seconds for this run

def run_test(strategy, num_philosophers, simulation_time):
    """Run a single test and parse results"""
    print(f"\n{'='*70}")
    print(f"🧪 Testing: {strategy} | {num_philosophers} philosophers | {simulation_time}s")
    print(f"{'='*70}")
    
    # Modify the Python script temporarily or pass parameters
    # For now, we'll use a simpler approach: modify config and run
    
    # Read original file
    with open('dining_philosophers.py', 'r') as f:
        original_content = f.read()
    
    # Modify configuration
    modified_content = original_content
    modified_content = re.sub(
        r'NUM_PHILOSOPHERS = \d+',
        f'NUM_PHILOSOPHERS = {num_philosophers}',
        modified_content
    )
    modified_content = re.sub(
        r'SIMULATION_TIME = \d+',
        f'SIMULATION_TIME = {simulation_time}',
        modified_content
    )
    
    # Write modified file
    with open('dining_philosophers.py', 'w') as f:
        f.write(modified_content)
    
    # Run the test
    start_time = time.time()
    try:
        result = subprocess.run(
            ['python3', 'dining_philosophers.py', strategy],
            capture_output=True,
            text=True,
            timeout=simulation_time + 10  # Add buffer
        )
        actual_time = time.time() - start_time
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        actual_time = time.time() - start_time
        output = "TIMEOUT"
        result = None
    
    # Restore original file
    with open('dining_philosophers.py', 'w') as f:
        f.write(original_content)
    
    # Parse results
    data = parse_output(output, strategy, num_philosophers, simulation_time, actual_time)
    
    return data

def parse_output(output, strategy, num_philosophers, simulation_time, actual_time):
    """Parse test output and extract metrics"""
    data = {
        'strategy': strategy,
        'num_philosophers': num_philosophers,
        'simulation_time_seconds': simulation_time,
        'actual_elapsed_time': round(actual_time, 2),
        'total_meals': 0,
        'avg_meals_per_philosopher': 0,
        'min_meals': 0,
        'max_meals': 0,
        'std_deviation_meals': 0,
        'deadlock_detected': 'unknown',
        'blocked_philosophers': 0,
        'throughput_meals_per_second': 0,
        'fairness_coefficient': 0,
        'cpu_usage_percent': '',
        'memory_usage_mb': '',
        'notes': ''
    }
    
    # Extract total meals
    total_match = re.search(r'📈 Total meals: (\d+)', output)
    if total_match:
        data['total_meals'] = int(total_match.group(1))
        data['avg_meals_per_philosopher'] = round(data['total_meals'] / num_philosophers, 2)
        if actual_time > 0:
            data['throughput_meals_per_second'] = round(data['total_meals'] / actual_time, 2)
    
    # Extract blocked philosophers
    blocked_match = re.search(r'⚠️  Philosophers still blocked: (\d+)', output)
    if blocked_match:
        data['blocked_philosophers'] = int(blocked_match.group(1))
    
    # Detect deadlock
    if 'DEADLOCK DETECTED' in output or data['blocked_philosophers'] > 0:
        data['deadlock_detected'] = 'yes'
    elif 'All philosophers finished successfully' in output:
        data['deadlock_detected'] = 'no'
    
    # Extract individual philosopher meals
    meals_list = []
    for match in re.finditer(r'Philosopher \d+: (\d+) meals', output):
        meals_list.append(int(match.group(1)))
    
    if meals_list:
        data['min_meals'] = min(meals_list)
        data['max_meals'] = max(meals_list)
        
        # Calculate standard deviation
        if len(meals_list) > 1:
            mean = sum(meals_list) / len(meals_list)
            variance = sum((x - mean) ** 2 for x in meals_list) / len(meals_list)
            data['std_deviation_meals'] = round(variance ** 0.5, 2)
        
        # Calculate fairness coefficient
        if data['max_meals'] > 0:
            data['fairness_coefficient'] = round((data['min_meals'] / data['max_meals']) * 100, 2)
    
    return data

def update_csv(data, csv_file='performance_analysis.csv'):
    """Update CSV file with test results"""
    # Read existing CSV
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    # Find and update the matching row
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('#') or line.startswith('strategy,') or not line.strip():
            continue
        
        parts = line.strip().split(',')
        if len(parts) >= 3:
            if (parts[0] == data['strategy'] and 
                parts[1] == str(data['num_philosophers']) and
                parts[2] == str(data['simulation_time_seconds'])):
                
                # Update this row
                new_line = f"{data['strategy']},{data['num_philosophers']},{data['simulation_time_seconds']},"
                new_line += f"{data['actual_elapsed_time']},{data['total_meals']},"
                new_line += f"{data['avg_meals_per_philosopher']},{data['min_meals']},{data['max_meals']},"
                new_line += f"{data['std_deviation_meals']},{data['deadlock_detected']},"
                new_line += f"{data['blocked_philosophers']},{data['throughput_meals_per_second']},"
                new_line += f"{data['fairness_coefficient']},{data['cpu_usage_percent']},"
                new_line += f"{data['memory_usage_mb']},{data['notes']}\n"
                
                lines[i] = new_line
                updated = True
                break
    
    # Write back to CSV
    if updated:
        with open(csv_file, 'w') as f:
            f.writelines(lines)
        print(f"✅ Updated CSV: {data['strategy']}, {data['num_philosophers']} phil, {data['simulation_time_seconds']}s")
    else:
        print(f"⚠️  No matching row found in CSV")

def main():
    """Run all tests"""
    print("🚀 Starting automated testing...")
    print(f"⏱️  Simulation time: {SIMULATION_TIME} seconds per test")
    print(f"📊 Total tests: {len(STRATEGIES) * len(NUM_PHILOSOPHERS_LIST)}")
    
    results = []
    
    for strategy in STRATEGIES:
        for num_phil in NUM_PHILOSOPHERS_LIST:
            try:
                data = run_test(strategy, num_phil, SIMULATION_TIME)
                results.append(data)
                
                # Print summary
                print(f"\n📊 Results:")
                print(f"   Total meals: {data['total_meals']}")
                print(f"   Avg per philosopher: {data['avg_meals_per_philosopher']}")
                print(f"   Throughput: {data['throughput_meals_per_second']} meals/s")
                print(f"   Deadlock: {data['deadlock_detected']}")
                print(f"   Blocked: {data['blocked_philosophers']}")
                print(f"   Fairness: {data['fairness_coefficient']}%")
                
                # Update CSV
                update_csv(data)
                
                # Small delay between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error testing {strategy} with {num_phil} philosophers: {e}")
                continue
    
    print("\n" + "="*70)
    print("✅ All tests completed!")
    print(f"📄 Results saved to: performance_analysis.csv")
    print("="*70)

if __name__ == "__main__":
    main()
