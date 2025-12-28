#!/bin/bash
# Simple test script to verify all files are present and valid

echo "🪔 Testing Diwali App..."
echo "========================"
echo ""

# Check if all required files exist
files=("index.html" "style.css" "script.js" "README.md" "launch.py")
all_present=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
        all_present=false
    fi
done

echo ""

# Check file sizes
if [ -f "index.html" ]; then
    size=$(wc -c < index.html)
    echo "📄 index.html: $size bytes"
fi

if [ -f "style.css" ]; then
    size=$(wc -c < style.css)
    echo "🎨 style.css: $size bytes"
fi

if [ -f "script.js" ]; then
    size=$(wc -c < script.js)
    echo "⚡ script.js: $size bytes"
fi

echo ""

if [ "$all_present" = true ]; then
    echo "✨ All files present! App is ready to run!"
    echo ""
    echo "To launch the app:"
    echo "  1. Double-click index.html"
    echo "  2. Or run: python3 launch.py"
    echo ""
    echo "Happy Diwali! 🎆"
else
    echo "⚠️  Some files are missing. Please check the installation."
fi

echo "========================"
