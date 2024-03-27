#!/bin/bash

# Check if autopep8 is installed
if ! command -v autopep8 &> /dev/null; then
    echo "Error: autopep8 is not installed. Please install autopep8."
    exit 1
fi

# Define the directory containing Python files
DIRECTORY=".."

# Format each Python file in the directory using autopep8
find "$DIRECTORY" -type f -name "*.py" -print0 | while IFS= read -r -d '' file; do
    echo "Formatting $file"
    autopep8 --in-place "$file"
done

echo "Formatting completed for all Python files in $DIRECTORY"
