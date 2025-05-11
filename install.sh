#!/bin/bash
# AMDTop Installation Script

# Function to display messages
print_message() {
    echo -e "\e[1;34m$1\e[0m"
}

# Function to display errors
print_error() {
    echo -e "\e[1;31mERROR: $1\e[0m"
}

# Function to display success messages
print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

# Check Python version
print_message "Checking Python version..."
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Found Python $python_version"
else
    print_error "Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Create virtual environment
print_message "Creating virtual environment..."
if python3 -m venv venv; then
    print_success "Virtual environment created successfully."
else
    print_error "Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_message "Installing Python dependencies..."
if pip install -r requirements.txt; then
    print_success "Python dependencies installed successfully."
else
    print_error "Failed to install Python dependencies."
    exit 1
fi

# Check for lm-sensors
print_message "Checking for lm-sensors..."
if command -v sensors &>/dev/null; then
    print_success "lm-sensors is already installed."
else
    print_message "lm-sensors is not installed. Attempting to install..."
    
    # Detect distribution
    if command -v apt-get &>/dev/null; then
        # Debian/Ubuntu
        print_message "Detected Debian/Ubuntu system."
        sudo apt-get update
        sudo apt-get install -y lm-sensors
        sudo sensors-detect --auto
    elif command -v dnf &>/dev/null; then
        # Fedora
        print_message "Detected Fedora system."
        sudo dnf install -y lm_sensors
        sudo sensors-detect --auto
    elif command -v pacman &>/dev/null; then
        # Arch Linux
        print_message "Detected Arch Linux system."
        sudo pacman -S --noconfirm lm_sensors
        sudo sensors-detect --auto
    else
        print_error "Could not detect package manager. Please install lm-sensors manually."
    fi
    
    # Check if installation was successful
    if command -v sensors &>/dev/null; then
        print_success "lm-sensors installed successfully."
    else
        print_error "Failed to install lm-sensors. Temperature monitoring may not work."
    fi
fi

# Create default configuration
print_message "Creating default configuration..."
mkdir -p ~/.config/amdtop
if python3 amdtop.py --create-config; then
    print_success "Default configuration created successfully."
else
    print_error "Failed to create default configuration."
fi

# Create desktop entry
print_message "Creating desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/amdtop.desktop << EOF
[Desktop Entry]
Name=AMDTop
Comment=AMD CPU/GPU monitoring tool
Exec=$(pwd)/venv/bin/python3 $(pwd)/amdtop.py
Terminal=true
Type=Application
Categories=System;Monitor;
EOF
print_success "Desktop entry created successfully."

# Create executable script
print_message "Creating executable script..."
cat > amdtop << EOF
#!/bin/bash
# AMDTop launcher script
cd "$(pwd)"
source venv/bin/activate
python3 amdtop.py "\$@"
EOF
chmod +x amdtop
print_success "Executable script created successfully."

print_message "Installation complete!"
print_message "You can run AMDTop using:"
print_message "  ./amdtop"
print_message "Or by searching for 'AMDTop' in your application menu."
print_message "For more information, see the INSTALL.md file."
