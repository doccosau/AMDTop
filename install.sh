#!/bin/bash
# AMDTop Installation Script

set -e  # Exit on error

# Color definitions
readonly BLUE='\e[1;34m'
readonly RED='\e[1;31m'
readonly GREEN='\e[1;32m'
readonly YELLOW='\e[1;33m'
readonly NC='\e[0m'  # No Color

# Configuration
readonly MIN_PYTHON_VERSION="3.7.0"
readonly INSTALL_DIR="$HOME/.local/bin"
readonly CONFIG_DIR="$HOME/.config/amdtop"
readonly DESKTOP_ENTRY_DIR="$HOME/.local/share/applications"

# Function to display messages
print_message() {
    echo -e "${BLUE}$1${NC}"
}

# Function to display errors
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

# Function to display success messages
print_success() {
    echo -e "${GREEN}$1${NC}"
}

# Function to display warnings
print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Function to check Python version
check_python_version() {
    local python_version
    if ! python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'); then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! python3 -c "from packaging import version; exit(0 if version.parse('$python_version') >= version.parse('$MIN_PYTHON_VERSION') else 1)"; then
        print_error "Python $MIN_PYTHON_VERSION or higher is required (found $python_version)"
        exit 1
    fi
    
    print_success "Found Python $python_version"
}

# Function to setup virtual environment
setup_venv() {
    print_message "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Existing virtual environment found. Removing..."
        rm -rf venv
    fi
    
    if ! python3 -m venv venv; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
}

# Function to install system dependencies
install_system_deps() {
    print_message "Checking system dependencies..."
    
    # Detect distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case $ID in
            ubuntu|debian)
                sudo apt-get update
                sudo apt-get install -y lm-sensors python3-dev build-essential
                ;;
            fedora)
                sudo dnf install -y lm_sensors python3-devel gcc
                ;;
            arch|manjaro)
                sudo pacman -Sy --noconfirm lm_sensors python-pip gcc
                ;;
            *)
                print_warning "Unsupported distribution: $ID. Please install dependencies manually."
                ;;
        esac
    else
        print_warning "Could not detect distribution. Please install dependencies manually."
    fi
}

# Function to create launcher script
create_launcher() {
    print_message "Creating launcher script..."
    
    mkdir -p "$INSTALL_DIR"
    cat > "$INSTALL_DIR/amdtop" << EOF
#!/bin/bash
# AMDTop launcher script
AMDTOP_DIR="$(pwd)"
source "\$AMDTOP_DIR/venv/bin/activate"
exec python3 "\$AMDTOP_DIR/amdtop.py" "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/amdtop"
    print_success "Launcher script created at $INSTALL_DIR/amdtop"
}

# Function to create desktop entry
create_desktop_entry() {
    print_message "Creating desktop entry..."
    
    mkdir -p "$DESKTOP_ENTRY_DIR"
    cat > "$DESKTOP_ENTRY_DIR/amdtop.desktop" << EOF
[Desktop Entry]
Name=AMDTop
GenericName=System Monitor
Comment=AMD CPU/GPU monitoring tool
Exec=$INSTALL_DIR/amdtop
Terminal=true
Type=Application
Categories=System;Monitor;
Keywords=system;monitor;cpu;gpu;amd;
Icon=$(pwd)/icons/amdtop.png
EOF
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null; then
        update-desktop-database "$DESKTOP_ENTRY_DIR"
    fi
}

# Main installation process
main() {
    print_message "Starting AMDTop installation..."
    
    # Check requirements
    check_python_version
    install_system_deps
    
    # Setup Python environment
    setup_venv
    
    # Install Python dependencies
    print_message "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install the package
    print_message "Installing AMDTop..."
    pip install -e .
    
    # Create configuration
    print_message "Creating configuration..."
    mkdir -p "$CONFIG_DIR"
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        python3 -c "from amdtop.config_loader import create_default_config; create_default_config('$CONFIG_DIR/config.yaml')"
    else
        print_warning "Configuration file already exists, skipping..."
    fi
    
    # Create launcher and desktop entry
    create_launcher
    create_desktop_entry
    
    print_success "Installation completed successfully!"
    print_message "\nYou can now run AMDTop using:"
    print_message "  amdtop"
    print_message "\nOr launch it from your application menu."
}

# Run main installation
main "$@"
