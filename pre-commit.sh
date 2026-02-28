#!/bin/bash
# Pre-commit hook for clawsync
echo "🧪 Running tests..."

python3 -m pytest test_clawsync.py -v --tb=short

if [ $? -ne 0 ]; then
    echo "❌ Tests failed!"
    exit 1
fi

echo "✅ Tests passed!"
exit 0
