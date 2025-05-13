#!/bin/bashstallation Guide
# AMDTop Installation Script
This guide will help you install and run AMDTop on your system.
set -e  # Exit on error

# Color definitions
readonly BLUE='\e[1;34m' Python 3.7 or higher
readonly RED='\e[1;31m'- Linux operating system (Ubuntu, Fedora, Arch, etc.)
readonly GREEN='\e[1;32m'D GPU with appropriate drivers
readonly YELLOW='\e[1;33m're monitoring: lm-sensors package
readonly NC='\e[0m'  # No Color
# Installation Steps
# Configuration
readonly MIN_PYTHON_VERSION="3.7.0"
readonly INSTALL_DIR="$HOME/.local/bin"
readonly CONFIG_DIR="$HOME/.config/amdtop"
readonly DESKTOP_ENTRY_DIR="$HOME/.local/share/applications"it clone https://github.com/yourusername/amdtop.git
cd amdtop
# Function to display messages
print_message() {
    echo -e "${BLUE}$1${NC}"tional but Recommended)
}

# Function to display errorson -m venv venv
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}
### 3. Install Dependencies
# Function to display success messages
print_success() {
    echo -e "${GREEN}$1${NC}"xt
}

# Function to display warnings
print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"## For Temperature Monitoring (lm-sensors)
}

# Function to check Python version
check_python_version() {
    local python_versionsudo apt-get install lm-sensors
    if ! python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'); thenauto  # Configure sensors
        print_error "Python 3 is not installed"
        exit 1
    fi
    \`bash
    if ! python3 -c "from packaging import version; exit(0 if version.parse('$python_version') >= version.parse('$MIN_PYTHON_VERSION') else 1)"; then
        print_error "Python $MIN_PYTHON_VERSION or higher is required (found $python_version)"rs-detect --auto  # Configure sensors
        exit 1\`\`
    fi
    
    print_success "Found Python $python_version"
}

# Function to setup virtual environment\`
setup_venv() {
    print_message "Setting up virtual environment..." For AMD GPU Monitoring
    
    if [ -d "venv" ]; then installed for your GPU.
        print_warning "Existing virtual environment found. Removing..."
        rm -rf venv
    fi
    
    if ! python3 -m venv venv; then
        print_error "Failed to create virtual environment"
        exit 1
    fin the current directory. You can edit this file to customize AMDTop.
    
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
}

# Function to install system dependencies
install_system_deps() {
    print_message "Checking system dependencies..."
    
    # Detect distributioning a Custom Configuration File
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case $ID inml
            ubuntu|debian)
                sudo apt-get update
                sudo apt-get install -y lm-sensors python3-dev build-essential
                ;;
            fedora)e configuration file is in YAML format and can be found in one of these locations (in order of precedence):
                sudo dnf install -y lm_sensors python3-devel gcc
                ;;` or `--config` command line option
            arch|manjaro)
                sudo pacman -Sy --noconfirm lm_sensors python-pip gccig.yaml` (user's home directory)
                ;;configuration)
            *)
                print_warning "Unsupported distribution: $ID. Please install dependencies manually."Configuration Options
                ;;
        esac\`\`yaml
    else# Update intervals (in seconds)
        print_warning "Could not detect distribution. Please install dependencies manually."
    fitrics
}

# Function to create launcher script
create_launcher() {r graphs and UI elements
    print_message "Creating launcher script..."
    
    mkdir -p "$INSTALL_DIR""green"
    cat > "$INSTALL_DIR/amdtop" << EOFd"
#!/bin/bash
# AMDTop launcher scriptisk_read: "blue"
AMDTOP_DIR="$(pwd)"
source "\$AMDTOP_DIR/venv/bin/activate"  network_download: "green"
exec python3 "\$AMDTOP_DIR/amdtop.py" "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/amdtop"
    print_success "Launcher script created at $INSTALL_DIR/amdtop"s to keep in graphs (history length)
}tory: 60
to show in the top processes list
# Function to create desktop entry
create_desktop_entry() { Number of partitions to show in disk metrics
    print_message "Creating desktop entry..."nt: 3
    rics
    mkdir -p "$DESKTOP_ENTRY_DIR"  interface_count: 3
    cat > "$DESKTOP_ENTRY_DIR/amdtop.desktop" << EOF
[Desktop Entry]
Name=AMDTopptions: system, disk, network, temperature
GenericName=System Monitor
Comment=AMD CPU/GPU monitoring tool
Exec=$INSTALL_DIR/amdtoptheme: "dark"  # Options: dark, light






















































main "$@"# Run main installation}    print_message "\nOr launch it from your application menu."    print_message "  amdtop"    print_message "\nYou can now run AMDTop using:"    print_success "Installation completed successfully!"        create_desktop_entry    create_launcher    # Create launcher and desktop entry        fi        print_warning "Configuration file already exists, skipping..."    else        python3 -c "from amdtop.config_loader import create_default_config; create_default_config('$CONFIG_DIR/config.yaml')"    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then    mkdir -p "$CONFIG_DIR"    print_message "Creating configuration..."    # Create configuration        pip install -e .    print_message "Installing AMDTop..."    # Install the package        pip install -r requirements.txt    print_message "Installing Python dependencies..."    # Install Python dependencies        setup_venv    # Setup Python environment        install_system_deps    check_python_version    # Check requirements        print_message "Starting AMDTop installation..."main() {# Main installation process}    fi        update-desktop-database "$DESKTOP_ENTRY_DIR"    if command -v update-desktop-database >/dev/null; then    # Update desktop database    EOFIcon=$(pwd)/icons/amdtop.pngKeywords=system;monitor;cpu;gpu;amd;Categories=System;Monitor;Type=ApplicationTerminal=true\`\`\`

## Keyboard Shortcuts

- `1`: Switch to System tab
- `2`: Switch to Disk I/O tab
- `3`: Switch to Network tab
- `4`: Switch to Temperature tab
- `t`: Toggle between dark and light themes
- `h`: Show/hide help screen
- `q`: Quit the application

## Troubleshooting

### Temperature Monitoring Not Working

If temperature monitoring is not working, ensure that lm-sensors is installed and configured:

\`\`\`bash
sudo sensors-detect --auto
sudo service kmod start  # Start the kernel modules
\`\`\`

### GPU Monitoring Not Working

If GPU monitoring is not working:

1. Ensure you have an AMD GPU
2. Check that the appropriate AMD drivers are installed
3. Verify that pyamdgpu is installed: `pip install pyamdgpu`

If you don't have an AMD GPU or pyamdgpu is not available, AMDTop will fall back to mock GPU data.

### Display Issues

If you encounter display issues:

1. Ensure your terminal supports TrueColor
2. Try resizing your terminal window
3. Check that all dependencies are installed correctly

## Building a Standalone Executable (Optional)

You can build a standalone executable using PyInstaller:

\`\`\`bash
pip install pyinstaller
pyinstaller --onefile --name amdtop amdtop.py
\`\`\`

The executable will be created in the `dist` directory.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
