#!/usr/bin/env python3
"""
ШВИДКИЙ тестовий скрипт для Dining Philosophers Problem
Оптимізації:
1. Паралельне виконання тестів
2. Короткий timeout для deadlock (3с замість 40с)
3. Без затримок між тестами
4. Вимкнення детального логування
"""

import subprocess
import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

# Test configurations
STRATEGIES = ['hierarchy', 'asymmetric', 'deadlock']  # deadlock в кінці
NUM_PHILOSOPHERS_LIST = [3, 5, 16, 32]
SIMULATION_TIME = 30  # seconds for this run
DEADLOCK_TIMEOUT = 3  # секунди для швидкої перевірки deadlock

def run_single_test(args):
    """Run a single test (для паралельного виконання)"""
    strategy, num_philosophers, simulation_time = args
    
    # Визначаємо timeout
    if strategy == 'deadlock':
        timeout = DEADLOCK_TIMEOUT + 5
        actual_sim_time = DEADLOCK_TIMEOUT
    else:
        timeout = simulation_time + 10
        actual_sim_time = simulation_time
    
    # Читаємо оригінальний файл
    with open('dining_philosophers.py', 'r') as f:
        original_content = f.read()
    
    # Модифікуємо конфігурацію
    modified_content = original_content
    modified_content = re.sub(
        r'NUM_PHILOSOPHERS = \d+',
        f'NUM_PHILOSOPHERS = {num_philosophers}',
        modified_content
    )
    modified_content = re.sub(
        r'SIMULATION_TIME = \d+',
        f'SIMULATION_TIME = {actual_sim_time}',
        modified_content
    )
    
    # Вимикаємо детальне логування для швидкості
    modified_content = re.sub(
        r'level=logging\.INFO',
        'level=logging.WARNING',
        modified_content
    )
    
    # Створюємо тимчасовий файл для цього тесту
    temp_file = f'temp_test_{strategy}_{num_philosophers}.py'
    with open(temp_file, 'w') as f:
        f.write(modified_content)
    
    # Запускаємо тест
    start_time = time.time()
    try:
        result = subprocess.run(
            ['python3', temp_file, strategy],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        actual_time = time.time() - start_time
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        actual_time = time.time() - start_time
        output = (e.stdout or '').decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
        output += (e.stderr or '').decode() if isinstance(e.stderr, bytes) else (e.stderr or '')
    finally:
        # Видаляємо тимчасовий файл
        try:
            import os
            os.remove(temp_file)
        except:
            pass
    
    # Парсимо результати
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
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('#') or line.startswith('strategy,') or not line.strip():
            continue
        
        parts = line.strip().split(',')
        if len(parts) >= 3:
            if (parts[0] == data['strategy'] and 
                parts[1] == str(data['num_philosophers']) and
                parts[2] == str(data['simulation_time_seconds'])):
                
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
    
    if updated:
        with open(csv_file, 'w') as f:
            f.writelines(lines)

def main():
    """Run all tests in parallel"""
    print("🚀 ШВИДКЕ ТЕСТУВАННЯ (ПАРАЛЕЛЬНЕ)")
    print(f"⏱️  Simulation time: {SIMULATION_TIME}s (deadlock: {DEADLOCK_TIMEOUT}s)")
    print(f"📊 Total tests: {len(STRATEGIES) * len(NUM_PHILOSOPHERS_LIST)}")
    print(f"⚡ Паралельність: до {min(4, len(STRATEGIES) * len(NUM_PHILOSOPHERS_LIST))} одночасних тестів")
    print()
    
    # Створюємо список всіх тестів
    test_args = []
    for strategy in STRATEGIES:
        for num_phil in NUM_PHILOSOPHERS_LIST:
            test_args.append((strategy, num_phil, SIMULATION_TIME))
    
    start_total = time.time()
    completed_count = 0
    
    # Виконуємо тести паралельно
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_single_test, args): args for args in test_args}
        
        for future in as_completed(futures):
            args = futures[future]
            strategy, num_phil, sim_time = args
            
            try:
                data = future.result()
                completed_count += 1
                
                # Коротке резюме
                status = "🔴 DEADLOCK" if data['deadlock_detected'] == 'yes' else "✅ OK"
                print(f"[{completed_count}/{len(test_args)}] {status} {strategy:12} {num_phil:2} phil: "
                      f"{data['total_meals']:4} meals, {data['throughput_meals_per_second']:5.1f} m/s")
                
                # Оновлюємо CSV
                update_csv(data)
                
            except Exception as e:
                print(f"❌ Error testing {strategy} with {num_phil} philosophers: {e}")
    
    elapsed_total = time.time() - start_total
    
    print()
    print("="*70)
    print(f"✅ All tests completed in {elapsed_total:.1f} seconds!")
    print(f"📄 Results saved to: performance_analysis.csv")
    print("="*70)

if __name__ == "__main__":
    main()
