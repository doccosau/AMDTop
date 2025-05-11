# AMDTop

A TUI (Text User Interface) application for monitoring AMD CPU/GPU systems in real-time.

## Features

- **CPU Monitoring**: Real-time CPU usage graph
- **GPU Monitoring**: Real-time GPU temperature graph
- **Memory Monitoring**: Real-time RAM usage graph
- **Disk I/O Monitoring**: Real-time disk read/write speeds
- **Network Monitoring**: Real-time network upload/download speeds
- **Process Monitoring**: Display of top CPU-consuming processes
- **Customizable**: Configuration file for colors, update intervals, and display options

## Installation

1. Clone this repository:
   \`\`\`
   git clone https://github.com/yourusername/amdtop.git
   cd amdtop
   \`\`\`

2. Install the required dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

3. For AMD GPU monitoring, you'll need to install pyamdgpu:
   \`\`\`
   pip install pyamdgpu
   \`\`\`
   Note: This might require additional system dependencies.

## Usage

Run the application:

\`\`\`
python amdtop.py
\`\`\`

### Command Line Options

- `-c, --config`: Specify a custom configuration file path
- `--create-config`: Create a default configuration file in the current directory

Example:
\`\`\`
python amdtop.py --create-config
python amdtop.py -c /path/to/your/config.yaml
\`\`\`

## Configuration

AMDTop can be customized using a YAML configuration file. The application looks for configuration in the following locations (in order):

1. Path specified with the `-c` or `--config` command line option
2. `./config.yaml` (current directory)
3. `~/.config/amdtop/config.yaml` (user's home directory)
4. `/etc/amdtop/config.yaml` (system-wide configuration)

To create a default configuration file:

\`\`\`
python amdtop.py --create-config
\`\`\`

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
  
  # UI theme colors
  background: "#1f1d2e"
  header_background: "#2d2b3a"
  widget_background: "#252336"
  widget_border: "#3d3b4a"
  tab_active: "#4d4b5a"
  tab_hover: "#3d3b4a"
  
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
default_tab: "system"  # Options: system, disk, network
\`\`\`

## Requirements

- Python 3.7+
- AMD CPU/GPU
- Linux operating system

## Dependencies

- textual: For the TUI interface
- psutil: For system monitoring
- matplotlib: For graph generation
- numpy: For numerical operations
- pillow: For image processing
- pyamdgpu: For AMD GPU monitoring
- pyyaml: For configuration file parsing

## Troubleshooting

If you encounter issues with AMD GPU monitoring:

1. Make sure you have an AMD GPU installed
2. Check that the appropriate AMD drivers are installed
3. Verify that pyamdgpu is installed correctly

If pyamdgpu is not available, the application will fall back to mock GPU data.
\`\`\`

```plaintext file="requirements.txt"
textual>=0.27.0
psutil>=5.9.0
matplotlib>=3.5.0
numpy>=1.22.0
pillow>=9.0.0
pyamdgpu>=0.2.0  # Required for AMD GPU monitoring
pyyaml>=6.0      # Required for configuration file parsing
