#!/bin/bash
# Local CI checks script for developers
# Run this before pushing your code to ensure CI will pass

set -e

echo "🚀 Running local CI checks..."
echo ""

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q flake8 black pylint mypy pytest-cov

echo ""
echo "🔍 Checking code formatting with Black..."
black --check --diff src/ tests/ || {
    echo "❌ Code formatting issues found!"
    echo "Run 'black src/ tests/' to fix"
    exit 1
}
echo "✅ Code formatting check passed"

echo ""
echo "🔍 Linting with Flake8..."
flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src/ tests/ --count --max-complexity=10 --max-line-length=127 --statistics --exit-zero
echo "✅ Linting passed"

echo ""
echo "🔍 Running Pylint..."
pylint src/ --exit-zero || true
echo "✅ Static analysis complete"

echo ""
echo "🔍 Type checking with Mypy..."
mypy src/ --ignore-missing-imports --no-strict-optional || true
echo "✅ Type checking complete"

echo ""
echo "🧪 Running tests with coverage..."
pytest tests/ -v --cov=src --cov-report=term --cov-report=html
echo "✅ All tests passed"

echo ""
echo "✨ All local CI checks passed! You're ready to push."
echo "📊 Coverage report generated in htmlcov/index.html"
