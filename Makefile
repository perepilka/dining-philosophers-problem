# Makefile for Dining Philosophers Problem
# Python implementation

.PHONY: all deadlock hierarchy asymmetric test help

# Default target
all: help

# ============================================================================
# EXECUTION TARGETS
# ============================================================================

# Deadlock scenario
deadlock:
	@echo "🐍 Running DEADLOCK scenario..."
	python3 dining_philosophers.py deadlock

# Hierarchy solution
hierarchy:
	@echo "🐍 Running HIERARCHY solution..."
	python3 dining_philosophers.py hierarchy

# Asymmetric solution
asymmetric:
	@echo "🐍 Running ASYMMETRIC solution..."
	python3 dining_philosophers.py asymmetric

# ============================================================================
# TESTING
# ============================================================================

# Test all strategies
test:
	@echo ""
	@echo "========================================================================"
	@echo "🧪 TESTING ALL STRATEGIES"
	@echo "========================================================================"
	@echo ""
	@echo "--- Testing HIERARCHY ---"
	@python3 dining_philosophers.py hierarchy | tail -15
	@echo ""
	@echo "--- Testing ASYMMETRIC ---"
	@python3 dining_philosophers.py asymmetric | tail -15
	@echo ""

# ============================================================================
# UTILITY TARGETS
# ============================================================================

# Show help
help:
	@echo ""
	@echo "🍽️  DINING PHILOSOPHERS PROBLEM (Python)"
	@echo "========================================================================"
	@echo ""
	@echo "🚀 EXECUTION:"
	@echo "  make deadlock         - Run deadlock scenario (зависне!)"
	@echo "  make hierarchy        - Run hierarchy solution (працює)"
	@echo "  make asymmetric       - Run asymmetric solution (працює)"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  make test             - Test all working strategies"
	@echo ""
	@echo "📖 DOCUMENTATION:"
	@echo "  make help             - Show this help message"
	@echo ""
	@echo "========================================================================"
	@echo "💡 Quick start:"
	@echo "  make hierarchy        # Найкращий варіант для демонстрації"
	@echo "  python3 dining_philosophers.py hierarchy"
	@echo "========================================================================"
	@echo ""
