#!/bin/bash
# Запуск deadlock тестів для 600с та 1200с

cd /home/perepilka/Code/dining-philosophers-problem

echo "🔴 DEADLOCK ТЕСТИ - 600с та 1200с"
echo "===================================="

for TIME in 600 1200; do
    echo ""
    echo "⏱️  Запускаю deadlock для ${TIME}s..."
    
    # Змінюємо конфігурацію
    sed -i "s/SIMULATION_TIME = [0-9]\+/SIMULATION_TIME = $TIME/" run_tests.py
    
    # Запускаємо тести
    python3 run_tests.py
    
    echo "✅ Завершено тести для ${TIME}s"
    sleep 2
done

echo ""
echo "🎉 Всі deadlock тести завершені!"
