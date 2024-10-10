#!/bin/bash

# Define the environment name
ENV_NAME="hbs_temp_python_environment"

# Function to check for Python 3 and pip
check_python() {
    # Capture the output of python3 --version
    PY_VERSION=$(python3 --version 2>&1)
    if [[ "$PY_VERSION" =~ Python\ 3 ]]; then
        PYTHON_CMD="python3"
        PIP_CMD="python3 -m pip"
        return 0
    else
        PY_VERSION=$(python --version 2>&1)
        if [[ "$PY_VERSION" =~ Python\ 3 ]]; then
            PYTHON_CMD="python"
            PIP_CMD="python -m pip"
            return 0
        else
            echo "Python 3 is not installed."
            exit 1
        fi
    fi
}

# Function to activate Anaconda if available
activate_conda() {
    # Try to load the module first
    module load anaconda3 &> /dev/null
    if [ $? -eq 0 ]; then
        echo "Anaconda module loaded successfully."
    else
        echo "Anaconda module could not be loaded. Checking local installation..."
    fi

    if command -v conda &> /dev/null; then
        echo "Activating Anaconda environment..."
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda create --name $ENV_NAME python=3.8 -y
        conda activate $ENV_NAME
        PYTHON_CMD=python
        PIP_CMD=pip
        return 0
    else
        echo "Trying to look in home folder for Anaconda next."
    fi

    conda info --base &> /dev/null
    if [ $? -eq 0 ]; then
        echo "Activating Anaconda environment..."
        conda activate
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        # Check for Homebrew installation of Conda
        # Intel mac
        if [ -f "/usr/local/anaconda3/bin/conda" ]; then
            echo "Found Anaconda via Homebrew at /usr/local/anaconda3. Activating..."
            source "/usr/local/anaconda3/bin/activate"
            conda create --name $ENV_NAME python=3.8 -y
            conda activate $ENV_NAME
            PYTHON_CMD="python"
            PIP_CMD="pip"
            return 0
        # Silicon mac
        elif [ -f "/opt/homebrew/anaconda3/bin/conda" ]; then
            echo "Found Anaconda via Homebrew at /opt/homebrew/anaconda3. Activating..."
            source "/opt/homebrew/anaconda3/bin/activate"
            conda create --name $ENV_NAME python=3.8 -y
            conda activate $ENV_NAME
            PYTHON_CMD="python"
            PIP_CMD="pip"
            return 0
        else
          # Check for local installation if module load fails
          if [ -f "$HOME/anaconda3/bin/conda" ]; then
              echo "Found Anaconda at $HOME/anaconda3. Activating..."
              source "$HOME/anaconda3/bin/activate"
              conda create --name $ENV_NAME python=3.8 -y
              conda activate $ENV_NAME
              PYTHON_CMD="python"
              PIP_CMD="pip"
          else
              echo "Anaconda is not installed. We'll try to find manual Python install next."
              exit 1
          fi
        fi
    fi
}

# Function to check if tkinter is available
check_tkinter() {
    $PYTHON_CMD -c "import tkinter" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "tkinter is available."
        return 0
    else
        echo "tkinter is not available yet, trying to activate conda next."
        return 1
    fi
}

# Main script execution starts here
check_tkinter
[ $? -ne 0 ] && activate_conda
check_tkinter
[ $? -ne 0 ] && check_python
check_tkinter
[ $? -ne 0 ] && exit 1

echo "Installing required Python packages..."
$PIP_CMD install -r requirements.txt

echo "Running the application..."
$PYTHON_CMD app.py
