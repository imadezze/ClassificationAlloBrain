#!/bin/bash
# Test runner script for AlloBrain

set -e  # Exit on error

echo "🧪 Running AlloBrain Tests"
echo "=========================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Run tests with various options
case "${1:-all}" in
    "all")
        echo "📋 Running all tests..."
        pytest tests/ -v
        ;;

    "coverage")
        echo "📊 Running tests with coverage..."
        pytest tests/ --cov=src --cov-report=html --cov-report=term -v
        echo ""
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;

    "few-shot")
        echo "📚 Running few-shot examples tests..."
        pytest tests/test_few_shot_examples.py -v
        ;;

    "watch")
        echo "👀 Running tests in watch mode..."
        if ! command -v pytest-watch &> /dev/null; then
            echo "Installing pytest-watch..."
            pip install pytest-watch
        fi
        pytest-watch tests/ -v
        ;;

    "quick")
        echo "⚡ Running quick tests (no verbose)..."
        pytest tests/ -q
        ;;

    *)
        echo "Usage: ./run_tests.sh [all|coverage|few-shot|watch|quick]"
        echo ""
        echo "Options:"
        echo "  all       - Run all tests (default)"
        echo "  coverage  - Run with coverage report"
        echo "  few-shot  - Run only few-shot examples tests"
        echo "  watch     - Run in watch mode (reruns on file changes)"
        echo "  quick     - Run without verbose output"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"
