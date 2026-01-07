#!/usr/bin/env python3
"""
Dining Philosophers Problem - Comprehensive Implementation
Demonstrates deadlock scenario and two working solutions.
"""

import threading
import time
import sys
import logging
from enum import Enum
from typing import List

# ============================================================================
# CONFIGURATION
# ============================================================================
NUM_PHILOSOPHERS = 5
MODE = "deadlock"  # Options: "deadlock", "hierarchy", "asymmetric"
SIMULATION_TIME = 10  # seconds

# ============================================================================
# STRATEGY ENUM
# ============================================================================
class Strategy(Enum):
    DEADLOCK = "deadlock"
    HIERARCHY = "hierarchy"
    ASYMMETRIC = "asymmetric"


# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(threadName)-15s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FORK (RESOURCE)
# ============================================================================
class Fork:
    """Represents a fork (chopstick) as a shared resource."""
    
    def __init__(self, fork_id: int):
        self.id = fork_id
        self.lock = threading.Lock()
    
    def __repr__(self):
        return f"Fork({self.id})"


# ============================================================================
# PHILOSOPHER (THREAD)
# ============================================================================
class Philosopher(threading.Thread):
    """Represents a philosopher who thinks and eats."""
    
    def __init__(self, phil_id: int, left_fork: Fork, right_fork: Fork, 
                 strategy: Strategy, duration: int):
        super().__init__(name=f"Phil-{phil_id}")
        self.id = phil_id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.strategy = strategy
        self.duration = duration
        self.meals_eaten = 0
        self.running = True
    
    def log(self, message: str):
        """Log with philosopher ID prefix."""
        logger.info(f"🧑 Philosopher {self.id}: {message}")
    
    def think(self):
        """Philosopher is thinking."""
        self.log("💭 Thinking...")
        time.sleep(0.1)
    
    def eat(self):
        """Philosopher is eating."""
        self.log("🍝 EATING")
        time.sleep(0.2)
        self.meals_eaten += 1
        self.log(f"✅ Finished eating (total meals: {self.meals_eaten})")
    
    def run(self):
        """Main philosopher lifecycle."""
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.duration:
            self.think()
            
            if self.strategy == Strategy.DEADLOCK:
                self.deadlock_strategy()
            elif self.strategy == Strategy.HIERARCHY:
                self.hierarchy_strategy()
            elif self.strategy == Strategy.ASYMMETRIC:
                self.asymmetric_strategy()
        
        self.log(f"🛑 Stopping (ate {self.meals_eaten} meals)")
    
    # ========================================================================
    # SCENARIO 1: DEADLOCK (Naïve Approach)
    # ========================================================================
    def deadlock_strategy(self):
        """
        ❌ DEADLOCK SCENARIO
        All philosophers pick up left fork first, then right fork.
        This creates a circular wait condition leading to deadlock.
        """
        self.log(f"⬅️  Trying to pick up LEFT fork (Fork {self.left_fork.id})")
        
        with self.left_fork.lock:
            self.log(f"✋ Picked up LEFT fork (Fork {self.left_fork.id})")
            
            # CRITICAL: Sleep to ensure all philosophers pick up left fork
            # This guarantees deadlock will occur
            time.sleep(0.5)
            
            self.log(f"➡️  Trying to pick up RIGHT fork (Fork {self.right_fork.id})")
            
            with self.right_fork.lock:
                self.log(f"✋ Picked up RIGHT fork (Fork {self.right_fork.id})")
                self.eat()
                self.log(f"🔽 Put down RIGHT fork (Fork {self.right_fork.id})")
            
            self.log(f"🔽 Put down LEFT fork (Fork {self.left_fork.id})")
    
    # ========================================================================
    # SCENARIO 2: RESOURCE HIERARCHY (Dijkstra's Solution)
    # ========================================================================
    def hierarchy_strategy(self):
        """
        ✅ RESOURCE HIERARCHY SOLUTION
        Always acquire forks in ascending order by their global ID.
        This breaks the circular wait condition.
        """
        first_fork = min(self.left_fork, self.right_fork, key=lambda f: f.id)
        second_fork = max(self.left_fork, self.right_fork, key=lambda f: f.id)
        
        first_pos = "LEFT" if first_fork == self.left_fork else "RIGHT"
        second_pos = "RIGHT" if second_fork == self.right_fork else "LEFT"
        
        self.log(f"📊 Hierarchy: First={first_pos} (Fork {first_fork.id}), "
                f"Second={second_pos} (Fork {second_fork.id})")
        
        self.log(f"🔼 Trying to pick up FIRST fork (Fork {first_fork.id})")
        
        with first_fork.lock:
            self.log(f"✋ Picked up FIRST fork (Fork {first_fork.id})")
            
            self.log(f"🔼 Trying to pick up SECOND fork (Fork {second_fork.id})")
            
            with second_fork.lock:
                self.log(f"✋ Picked up SECOND fork (Fork {second_fork.id})")
                self.eat()
                self.log(f"🔽 Put down SECOND fork (Fork {second_fork.id})")
            
            self.log(f"🔽 Put down FIRST fork (Fork {first_fork.id})")
    
    # ========================================================================
    # SCENARIO 3: ASYMMETRIC SOLUTION (Even/Odd)
    # ========================================================================
    def asymmetric_strategy(self):
        """
        ✅ ASYMMETRIC SOLUTION
        Even-numbered philosophers: LEFT → RIGHT
        Odd-numbered philosophers: RIGHT → LEFT
        Breaking symmetry prevents circular wait.
        """
        if self.id % 2 == 0:
            # Even philosopher: Left → Right
            self.log(f"👥 EVEN philosopher: LEFT → RIGHT strategy")
            
            self.log(f"⬅️  Trying to pick up LEFT fork (Fork {self.left_fork.id})")
            with self.left_fork.lock:
                self.log(f"✋ Picked up LEFT fork (Fork {self.left_fork.id})")
                
                self.log(f"➡️  Trying to pick up RIGHT fork (Fork {self.right_fork.id})")
                with self.right_fork.lock:
                    self.log(f"✋ Picked up RIGHT fork (Fork {self.right_fork.id})")
                    self.eat()
                    self.log(f"🔽 Put down RIGHT fork (Fork {self.right_fork.id})")
                
                self.log(f"🔽 Put down LEFT fork (Fork {self.left_fork.id})")
        else:
            # Odd philosopher: Right → Left
            self.log(f"👤 ODD philosopher: RIGHT → LEFT strategy")
            
            self.log(f"➡️  Trying to pick up RIGHT fork (Fork {self.right_fork.id})")
            with self.right_fork.lock:
                self.log(f"✋ Picked up RIGHT fork (Fork {self.right_fork.id})")
                
                self.log(f"⬅️  Trying to pick up LEFT fork (Fork {self.left_fork.id})")
                with self.left_fork.lock:
                    self.log(f"✋ Picked up LEFT fork (Fork {self.left_fork.id})")
                    self.eat()
                    self.log(f"🔽 Put down LEFT fork (Fork {self.left_fork.id})")
                
                self.log(f"🔽 Put down RIGHT fork (Fork {self.right_fork.id})")
    
    def stop(self):
        """Signal the philosopher to stop."""
        self.running = False


# ============================================================================
# DINING TABLE (ORCHESTRATOR)
# ============================================================================
class DiningTable:
    """Manages the dining philosophers simulation."""
    
    def __init__(self, num_philosophers: int, strategy: Strategy, duration: int):
        self.num_philosophers = num_philosophers
        self.strategy = strategy
        self.duration = duration
        self.forks: List[Fork] = []
        self.philosophers: List[Philosopher] = []
    
    def setup(self):
        """Initialize forks and philosophers."""
        logger.info("=" * 70)
        logger.info(f"🍽️  DINING PHILOSOPHERS PROBLEM")
        logger.info(f"📊 Number of philosophers: {self.num_philosophers}")
        logger.info(f"🎯 Strategy: {self.strategy.value.upper()}")
        logger.info(f"⏱️  Simulation time: {self.duration} seconds")
        logger.info("=" * 70)
        
        # Create forks
        self.forks = [Fork(i) for i in range(self.num_philosophers)]
        logger.info(f"🍴 Created {len(self.forks)} forks")
        
        # Create philosophers
        for i in range(self.num_philosophers):
            left_fork = self.forks[i]
            right_fork = self.forks[(i + 1) % self.num_philosophers]
            
            philosopher = Philosopher(
                phil_id=i,
                left_fork=left_fork,
                right_fork=right_fork,
                strategy=self.strategy,
                duration=self.duration
            )
            self.philosophers.append(philosopher)
        
        logger.info(f"🧑 Created {len(self.philosophers)} philosophers")
        logger.info("")
        
        # Show fork assignments
        for phil in self.philosophers:
            logger.info(f"  Philosopher {phil.id}: "
                       f"Left=Fork {phil.left_fork.id}, Right=Fork {phil.right_fork.id}")
        logger.info("")
    
    def start(self):
        """Start the simulation."""
        logger.info("🚀 Starting simulation...")
        logger.info("")
        
        start_time = time.time()
        
        # Start all philosopher threads
        for philosopher in self.philosophers:
            philosopher.start()
        
        # Wait for simulation time or detect deadlock
        try:
            time.sleep(self.duration)
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
        
        elapsed = time.time() - start_time
        
        # Stop all philosophers
        for philosopher in self.philosophers:
            philosopher.stop()
        
        # Wait for all threads to finish (with timeout for deadlock)
        logger.info("\n⏳ Waiting for philosophers to finish...")
        for philosopher in self.philosophers:
            philosopher.join(timeout=2.0)
            if philosopher.is_alive():
                logger.warning(f"⚠️  Philosopher {philosopher.id} is still blocked (DEADLOCK)")
        
        self.report_results(elapsed)
    
    def report_results(self, elapsed_time: float):
        """Print final statistics."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 SIMULATION RESULTS")
        logger.info("=" * 70)
        logger.info(f"⏱️  Elapsed time: {elapsed_time:.2f} seconds")
        logger.info(f"🎯 Strategy: {self.strategy.value.upper()}")
        logger.info("")
        
        total_meals = sum(p.meals_eaten for p in self.philosophers)
        alive_count = sum(1 for p in self.philosophers if p.is_alive())
        
        logger.info("🍽️  Meals eaten per philosopher:")
        for phil in self.philosophers:
            status = "🔴 BLOCKED" if phil.is_alive() else "✅ Finished"
            logger.info(f"  Philosopher {phil.id}: {phil.meals_eaten} meals - {status}")
        
        logger.info("")
        logger.info(f"📈 Total meals: {total_meals}")
        logger.info(f"⚠️  Philosophers still blocked: {alive_count}")
        
        if alive_count > 0:
            logger.info("")
            logger.info("❌ DEADLOCK DETECTED! Some philosophers are still waiting for forks.")
        else:
            logger.info("")
            logger.info("✅ All philosophers finished successfully (No deadlock).")
        
        logger.info("=" * 70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    """Main function to run the simulation."""
    
    # Parse command line arguments
    strategy_name = MODE
    if len(sys.argv) > 1:
        strategy_name = sys.argv[1].lower()
    
    # Validate strategy
    try:
        strategy = Strategy(strategy_name)
    except ValueError:
        logger.error(f"❌ Invalid strategy: {strategy_name}")
        logger.error(f"   Valid options: deadlock, hierarchy, asymmetric")
        sys.exit(1)
    
    # Create and run simulation
    table = DiningTable(
        num_philosophers=NUM_PHILOSOPHERS,
        strategy=strategy,
        duration=SIMULATION_TIME
    )
    
    table.setup()
    table.start()


if __name__ == "__main__":
    main()
