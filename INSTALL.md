# AMDTop Installation Guide

This guide will help you install and run AMDTop on your system.

## Prerequisites

- Python 3.7 or higher
- Linux operating system (Ubuntu, Fedora, Arch, etc.)
- For AMD GPU monitoring: AMD GPU with appropriate drivers
- For temperature monitoring: lm-sensors package

## Installation Steps

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/yourusername/amdtop.git
cd amdtop
\`\`\`

### 2. Create a Virtual Environment (Optional but Recommended)

\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 3. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Install System Dependencies

#### For Temperature Monitoring (lm-sensors)

On Ubuntu/Debian:
\`\`\`bash
sudo apt-get update
sudo apt-get install lm-sensors
sudo sensors-detect --auto  # Configure sensors
\`\`\`

On Fedora:
\`\`\`bash
sudo dnf install lm_sensors
sudo sensors-detect --auto  # Configure sensors
\`\`\`

On Arch Linux:
\`\`\`bash
sudo pacman -S lm_sensors
sudo sensors-detect --auto  # Configure sensors
\`\`\`

#### For AMD GPU Monitoring

Ensure you have the appropriate AMD drivers installed for your GPU.

### 5. Create a Default Configuration

\`\`\`bash
python amdtop.py --create-config
\`\`\`

This will create a default configuration file in the current directory. You can edit this file to customize AMDTop.

## Running AMDTop

### Basic Usage

\`\`\`bash
python amdtop.py
\`\`\`

### Using a Custom Configuration File

\`\`\`bash
python amdtop.py -c /path/to/your/config.yaml
\`\`\`

## Configuration

The configuration file is in YAML format and can be found in one of these locations (in order of precedence):

1. Path specified with the `-c` or `--config` command line option
2. `./config.yaml` (current directory)
3. `~/.config/amdtop/config.yaml` (user's home directory)
4. `/etc/amdtop/config.yaml` (system-wide configuration)

### Configuration Options

\`\`\`yaml
# Update intervals (in seconds)
intervals:
  # How often to update the graphs and metrics
  graphs: 1.0
  processes: 2.0
  
# Colors for graphs and UI elements
colors:
  # Graph colors
  cpu_graph: "green"
  gpu_graph: "red"
  memory_graph: "blue"
  disk_read: "blue"
  disk_write: "red"
  network_download: "green"
  network_upload: "orange"
  
# Display settings
display:
  # Number of data points to keep in graphs (history length)
  graph_history: 60
  # Number of processes to show in the top processes list
  process_count: 10
  # Number of partitions to show in disk metrics
  partition_count: 3
  # Number of network interfaces to show in network metrics
  interface_count: 3
  
# Default tab to show on startup
default_tab: "system"  # Options: system, disk, network, temperature

# Theme setting
theme: "dark"  # Options: dark, light
\`\`\`

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
