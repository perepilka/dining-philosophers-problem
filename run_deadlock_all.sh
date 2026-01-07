#!/bin/bash
# Запуск deadlock тестів для всіх часових інтервалів

cd /home/perepilka/Code/dining-philosophers-problem

echo "🔴 DEADLOCK ТЕСТИ - ВСІ ЧАСОВІ ІНТЕРВАЛИ"
echo "========================================"
echo ""

# Масиви часових інтервалів, які ще не заповнені
TIMES=(60 180 600 1200)

for TIME in "${TIMES[@]}"; do
    echo "⏱️  Тестую deadlock для ${TIME}s..."
    
    # Змінюємо конфігурацію
    sed -i "s/SIMULATION_TIME = [0-9]\+/SIMULATION_TIME = $TIME/" run_tests.py
    
    # Запускаємо тести
    python3 run_tests.py
    
    echo "✅ Завершено тести для ${TIME}s"
    echo ""
    sleep 2
done

echo "🎉 Всі deadlock тести завершені!"
