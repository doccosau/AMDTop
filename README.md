# AMDTop

A powerful TUI (Text User Interface) application for monitoring AMD CPU/GPU systems in real-time, built with Python and Textual.

![AMDTop Screenshot](docs/images/amdtop-screenshot.png)

## ✨ Features

- 📊 **Real-time Monitoring**
  - CPU usage and frequency
  - GPU temperature and utilization
  - Memory usage and swap
  - Disk I/O speeds
  - Network traffic
  - Process activities

- 🎨 **Advanced UI**
  - Live updating graphs
  - Dark and light themes
  - Customizable colors
  - Keyboard shortcuts
  - Multiple view modes

- ⚙️ **Smart Configuration**
  - YAML-based configuration
  - Multiple config locations
  - Command-line options
  - Auto-saving settings

## 🚀 Quick Start

### Prerequisites

```bash
# For Ubuntu/Debian
sudo apt install python3-dev python3-pip lm-sensors

# For Fedora
sudo dnf install python3-devel python3-pip lm_sensors

# For Arch Linux
sudo pacman -S python-pip lm_sensors
```

### Installation

1. **Clone and Install**
```bash
git clone https://github.com/yourusername/amdtop.git
cd amdtop
./install.sh
```

2. **Run AMDTop**
```bash
amdtop
```

## ⌨️ Key Bindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `h` | Help |
| `t` | Toggle Theme |
| `1-4` | Switch Tabs |
| `r` | Reset Graphs |
| `p` | Pause/Resume |

## 🔧 Configuration

Create default config:
```bash
amdtop --create-config
```

Config locations (in priority order):
1. Custom path (`-c` option)
2. `./config.yaml`
3. `~/.config/amdtop/config.yaml`
4. `/etc/amdtop/config.yaml`

### Sample Configuration

```yaml
intervals:
  graphs: 1.0
  processes: 2.0
  temperature: 5.0
  network: 1.0

display:
  graph_history: 60
  process_count: 10
  compact_mode: false

theme: "dark"  # or "light"
```

## 🔍 Troubleshooting

### Common Issues

1. **GPU Monitoring Not Working**
   ```bash
   # Check AMD driver
   lsmod | grep amdgpu
   
   # Install driver if needed
   sudo apt install amdgpu-pro  # Ubuntu
   ```

2. **Temperature Sensors**
   ```bash
   # Configure sensors
   sudo sensors-detect --auto
   sudo systemctl restart kmod
   ```

3. **Permission Issues**
   ```bash
   # Add user to required groups
   sudo usermod -aG video,input $USER
   ```

## 📦 Dependencies

Core:
- Python ≥ 3.7
- textual ≥ 0.27.0
- psutil ≥ 5.9.0
- matplotlib ≥ 3.5.0
- pyamdgpu ≥ 0.2.0

Optional:
- notify2 ≥ 0.3.1 (notifications)
- pytest ≥ 7.0.0 (testing)

## 🛠️ Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- Create an [Issue](https://github.com/yourusername/amdtop/issues)
- Join our [Discord](https://discord.gg/yourdiscord)
- Email: support@amdtop.com

## 🙏 Acknowledgments

- [Textual](https://github.com/Textualize/textual) for the amazing TUI framework
- [pyamdgpu](https://github.com/yourusername/pyamdgpu) for AMD GPU support
````

```plaintext file="requirements.txt"
textual>=0.27.0
psutil>=5.9.0
matplotlib>=3.5.0
numpy>=1.22.0
pillow>=9.0.0
pyamdgpu>=0.2.0  # Required for AMD GPU monitoring
pyyaml>=6.0      # Required for configuration file parsing
