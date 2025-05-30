#!/bin/bash

echo "Starting scraper script..."

# Check if pip is available
if ! command -v pip &> /dev/null
then
    echo "Error: pip could not be found. Please install pip."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies. Please check requirements.txt and your pip installation."
    exit 1
fi
echo "Dependencies installed successfully."

# Check if python is available
if ! command -v python &> /dev/null
then
    # Try python3 if python is not found
    if ! command -v python3 &> /dev/null
    then
        echo "Error: python or python3 could not be found. Please install Python."
        exit 1
    else
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python"
fi

# Execute the Python scraper script
echo "Executing Python scraper script (main.py)..."
$PYTHON_CMD main.py
if [ $? -ne 0 ]; then
    echo "Error: Python scraper script failed to execute."
    # Note: The Python script itself has internal error handling and messages.
    # This error message indicates the script interpreter encountered an issue or the script exited with an error code.
    exit 1
fi

echo "Scraper script finished."
exit 0
