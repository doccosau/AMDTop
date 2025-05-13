#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Theme manager for AMDTop
Handles dark and light themes and custom theme support
"""
from typing import Dict, Any
import json
import os

# Dark theme colors
DARK_THEME = {
    "background": "#1f1d2e",
    "header_background": "#2d2b3a",
    "widget_background": "#252336",
    "widget_border": "#3d3b4a",
    "tab_active": "#4d4b5a",
    "tab_hover": "#3d3b4a",
    "text": "#ffffff",
    "text_muted": "#a9a7b7",
    "cpu_graph": "#50fa7b",
    "memory_graph": "#8be9fd",
    "gpu_graph": "#ff5555",
    "disk_read": "#bd93f9",
    "disk_write": "#ff79c6",
    "network_download": "#50fa7b",
    "network_upload": "#ffb86c",
    "temperature": "#ff5555",
}

# Light theme colors
LIGHT_THEME = {
    "background": "#f5f5f7",
    "header_background": "#e0e0e5",
    "widget_background": "#ffffff",
    "widget_border": "#d0d0d5",
    "tab_active": "#b8b8c0",
    "tab_hover": "#d0d0d5",
    "text": "#000000",
    "text_muted": "#555555",
    "cpu_graph": "#2ea043",
    "memory_graph": "#0366d6",
    "gpu_graph": "#d73a49",
    "disk_read": "#6f42c1",
    "disk_write": "#ea4aaa",
    "network_download": "#2ea043",
    "network_upload": "#f66a0a",
    "temperature": "#d73a49",
}

class ThemeManager:
    """
    Manages application themes including custom themes
    """
    def __init__(self, config: Dict[str, Any]):
        """Initialize theme manager with configuration"""
        self.config = config
        self.themes = {
            "dark": DARK_THEME,
            "light": LIGHT_THEME
        }
        
        # Load custom themes if they exist
        self._load_custom_themes()
        
        # Set current theme from config
        self.current_theme = config.get("theme", "dark")
        if self.current_theme not in self.themes:
            self.current_theme = "dark"
            
        self.theme_colors = self._get_theme_colors()

    def _load_custom_themes(self) -> None:
        """Load custom themes from config directory"""
        config_dir = os.path.expanduser("~/.config/amdtop/themes")
        if not os.path.exists(config_dir):
            return
            
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                theme_path = os.path.join(config_dir, filename)
                theme_name = filename[:-5]  # Remove .json
                try:
                    with open(theme_path, 'r') as f:
                        theme_data = json.load(f)
                        # Validate theme data
                        if self._validate_theme(theme_data):
                            self.themes[theme_name] = theme_data
                except (json.JSONDecodeError, OSError):
                    print(f"Error loading custom theme: {theme_path}")

    def _validate_theme(self, theme_data: Dict[str, str]) -> bool:
        """Validate that a theme contains all required colors"""
        required_colors = set(DARK_THEME.keys())
        theme_colors = set(theme_data.keys())
        return required_colors.issubset(theme_colors)

    def _get_theme_colors(self) -> Dict[str, str]:
        """Get colors for current theme"""
        return self.themes[self.current_theme]

    def toggle_theme(self) -> None:
        """Toggle between available themes"""
        # Get list of available themes
        theme_names = list(self.themes.keys())
        # Find current theme index
        current_index = theme_names.index(self.current_theme)
        # Get next theme
        next_index = (current_index + 1) % len(theme_names)
        self.current_theme = theme_names[next_index]
        
        # Update theme colors
        self.theme_colors = self._get_theme_colors()
        # Update config
        self.config["theme"] = self.current_theme

    def get_theme_colors(self) -> Dict[str, str]:
        """Get current theme colors"""
        return self.theme_colors

    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme

    def add_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Add a new custom theme"""
        if not self._validate_theme(colors):
            return False
            
        # Save theme to config directory
        config_dir = os.path.expanduser("~/.config/amdtop/themes")
        os.makedirs(config_dir, exist_ok=True)
        
        theme_path = os.path.join(config_dir, f"{name}.json")
        try:
            with open(theme_path, 'w') as f:
                json.dump(colors, f, indent=2)
            self.themes[name] = colors
            return True
        except OSError:
            return False

    def generate_css(self) -> str:
        """Generate CSS from current theme colors"""
        colors = self.get_theme_colors()
        css = f"""
        .app-grid {{
            background: {colors['background']};
            color: {colors['text']};
        }}
        
        Header {{
            background: {colors['header_background']};
        }}
        
        .widget {{
            background: {colors['widget_background']};
            border: 1px solid {colors['widget_border']};
        }}
        
        Tab {{
            color: {colors['text_muted']};
        }}
        
        Tab:hover {{
            background: {colors['tab_hover']};
        }}
        
        Tab.-active {{
            background: {colors['tab_active']};
            color: {colors['text']};
        }}
        
        #cpu_graph {{
            color: {colors['cpu_graph']};
        }}
        
        #memory_graph {{
            color: {colors['memory_graph']};
        }}
        
        #gpu_graph {{
            color: {colors['gpu_graph']};
        }}
        """
        return css

# Test the module if run directly
if __name__ == "__main__":
    config = {"theme": "dark"}
    theme_manager = ThemeManager(config)
    
    # Print current theme colors
    print("Current theme:", theme_manager.get_current_theme())
    print("\nTheme colors:")
    for key, value in theme_manager.get_theme_colors().items():
        print(f"{key}: {value}")
    
    # Test theme toggle
    print("\nToggling theme...")
    theme_manager.toggle_theme()
    print("New theme:", theme_manager.get_current_theme())
    
    # Test custom theme
    print("\nAdding custom theme...")
    custom_theme = DARK_THEME.copy()
    custom_theme["background"] = "#000000"
    success = theme_manager.add_custom_theme("custom", custom_theme)
    print("Custom theme added:", success)
    
    # Print generated CSS
    print("\nGenerated CSS:")
    print(theme_manager.generate_css())    #!/usr/bin/env python3
    """
    Theme manager for AMDTop
    Handles dark and light themes and custom theme support
    """
    from typing import Dict, Any
    import json
    import os
    
    # Dark theme colors
    DARK_THEME = {
        "background": "#1f1d2e",
        "header_background": "#2d2b3a",
        "widget_background": "#252336",
        "widget_border": "#3d3b4a",
        "tab_active": "#4d4b5a",
        "tab_hover": "#3d3b4a",
        "text": "#ffffff",
        "text_muted": "#a9a7b7",
        "cpu_graph": "#50fa7b",
        "memory_graph": "#8be9fd",
        "gpu_graph": "#ff5555",
        "disk_read": "#bd93f9",
        "disk_write": "#ff79c6",
        "network_download": "#50fa7b",
        "network_upload": "#ffb86c",
        "temperature": "#ff5555",
    }
    
    # Light theme colors
    LIGHT_THEME = {
        "background": "#f5f5f7",
        "header_background": "#e0e0e5",
        "widget_background": "#ffffff",
        "widget_border": "#d0d0d5",
        "tab_active": "#b8b8c0",
        "tab_hover": "#d0d0d5",
        "text": "#000000",
        "text_muted": "#555555",
        "cpu_graph": "#2ea043",
        "memory_graph": "#0366d6",
        "gpu_graph": "#d73a49",
        "disk_read": "#6f42c1",
        "disk_write": "#ea4aaa",
        "network_download": "#2ea043",
        "network_upload": "#f66a0a",
        "temperature": "#d73a49",
    }
    
    class ThemeManager:
        """
        Manages application themes including custom themes
        """
        def __init__(self, config: Dict[str, Any]):
            """Initialize theme manager with configuration"""
            self.config = config
            self.themes = {
                "dark": DARK_THEME,
                "light": LIGHT_THEME
            }
            
            # Load custom themes if they exist
            self._load_custom_themes()
            
            # Set current theme from config
            self.current_theme = config.get("theme", "dark")
            if self.current_theme not in self.themes:
                self.current_theme = "dark"
                
            self.theme_colors = self._get_theme_colors()
    
        def _load_custom_themes(self) -> None:
            """Load custom themes from config directory"""
            config_dir = os.path.expanduser("~/.config/amdtop/themes")
            if not os.path.exists(config_dir):
                return
                
            for filename in os.listdir(config_dir):
                if filename.endswith('.json'):
                    theme_path = os.path.join(config_dir, filename)
                    theme_name = filename[:-5]  # Remove .json
                    try:
                        with open(theme_path, 'r') as f:
                            theme_data = json.load(f)
                            # Validate theme data
                            if self._validate_theme(theme_data):
                                self.themes[theme_name] = theme_data
                    except (json.JSONDecodeError, OSError):
                        print(f"Error loading custom theme: {theme_path}")
    
        def _validate_theme(self, theme_data: Dict[str, str]) -> bool:
            """Validate that a theme contains all required colors"""
            required_colors = set(DARK_THEME.keys())
            theme_colors = set(theme_data.keys())
            return required_colors.issubset(theme_colors)
    
        def _get_theme_colors(self) -> Dict[str, str]:
            """Get colors for current theme"""
            return self.themes[self.current_theme]
    
        def toggle_theme(self) -> None:
            """Toggle between available themes"""
            # Get list of available themes
            theme_names = list(self.themes.keys())
            # Find current theme index
            current_index = theme_names.index(self.current_theme)
            # Get next theme
            next_index = (current_index + 1) % len(theme_names)
            self.current_theme = theme_names[next_index]
            
            # Update theme colors
            self.theme_colors = self._get_theme_colors()
            # Update config
            self.config["theme"] = self.current_theme
    
        def get_theme_colors(self) -> Dict[str, str]:
            """Get current theme colors"""
            return self.theme_colors
    
        def get_current_theme(self) -> str:
            """Get current theme name"""
            return self.current_theme
    
        def add_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
            """Add a new custom theme"""
            if not self._validate_theme(colors):
                return False
                
            # Save theme to config directory
            config_dir = os.path.expanduser("~/.config/amdtop/themes")
            os.makedirs(config_dir, exist_ok=True)
            
            theme_path = os.path.join(config_dir, f"{name}.json")
            try:
                with open(theme_path, 'w') as f:
                    json.dump(colors, f, indent=2)
                self.themes[name] = colors
                return True
            except OSError:
                return False
    
        def generate_css(self) -> str:
            """Generate CSS from current theme colors"""
            colors = self.get_theme_colors()
            css = f"""
            .app-grid {{
                background: {colors['background']};
                color: {colors['text']};
            }}
            
            Header {{
                background: {colors['header_background']};
            }}
            
            .widget {{
                background: {colors['widget_background']};
                border: 1px solid {colors['widget_border']};
            }}
            
            Tab {{
                color: {colors['text_muted']};
            }}
            
            Tab:hover {{
                background: {colors['tab_hover']};
            }}
            
            Tab.-active {{
                background: {colors['tab_active']};
                color: {colors['text']};
            }}
            
            #cpu_graph {{
                color: {colors['cpu_graph']};
            }}
            
            #memory_graph {{
                color: {colors['memory_graph']};
            }}
            
            #gpu_graph {{
                color: {colors['gpu_graph']};
            }}
            """
            return css
    
    # Test the module if run directly
    if __name__ == "__main__":
        config = {"theme": "dark"}
        theme_manager = ThemeManager(config)
        
        # Print current theme colors
        print("Current theme:", theme_manager.get_current_theme())
        print("\nTheme colors:")
        for key, value in theme_manager.get_theme_colors().items():
            print(f"{key}: {value}")
        
        # Test theme toggle
        print("\nToggling theme...")
        theme_manager.toggle_theme()
        print("New theme:", theme_manager.get_current_theme())
        
        # Test custom theme
        print("\nAdding custom theme...")
        custom_theme = DARK_THEME.copy()
        custom_theme["background"] = "#000000"
        success = theme_manager.add_custom_theme("custom", custom_theme)
        print("Custom theme added:", success)
        
        # Print generated CSS
        print("\nGenerated CSS:")
        print(theme_manager.generate_css())        #!/usr/bin/env python3
        """
        Theme manager for AMDTop
        Handles dark and light themes and custom theme support
        """
        from typing import Dict, Any
        import json
        import os
        
        # Dark theme colors
        DARK_THEME = {
            "background": "#1f1d2e",
            "header_background": "#2d2b3a",
            "widget_background": "#252336",
            "widget_border": "#3d3b4a",
            "tab_active": "#4d4b5a",
            "tab_hover": "#3d3b4a",
            "text": "#ffffff",
            "text_muted": "#a9a7b7",
            "cpu_graph": "#50fa7b",
            "memory_graph": "#8be9fd",
            "gpu_graph": "#ff5555",
            "disk_read": "#bd93f9",
            "disk_write": "#ff79c6",
            "network_download": "#50fa7b",
            "network_upload": "#ffb86c",
            "temperature": "#ff5555",
        }
        
        # Light theme colors
        LIGHT_THEME = {
            "background": "#f5f5f7",
            "header_background": "#e0e0e5",
            "widget_background": "#ffffff",
            "widget_border": "#d0d0d5",
            "tab_active": "#b8b8c0",
            "tab_hover": "#d0d0d5",
            "text": "#000000",
            "text_muted": "#555555",
            "cpu_graph": "#2ea043",
            "memory_graph": "#0366d6",
            "gpu_graph": "#d73a49",
            "disk_read": "#6f42c1",
            "disk_write": "#ea4aaa",
            "network_download": "#2ea043",
            "network_upload": "#f66a0a",
            "temperature": "#d73a49",
        }
        
        class ThemeManager:
            """
            Manages application themes including custom themes
            """
            def __init__(self, config: Dict[str, Any]):
                """Initialize theme manager with configuration"""
                self.config = config
                self.themes = {
                    "dark": DARK_THEME,
                    "light": LIGHT_THEME
                }
                
                # Load custom themes if they exist
                self._load_custom_themes()
                
                # Set current theme from config
                self.current_theme = config.get("theme", "dark")
                if self.current_theme not in self.themes:
                    self.current_theme = "dark"
                    
                self.theme_colors = self._get_theme_colors()
        
            def _load_custom_themes(self) -> None:
                """Load custom themes from config directory"""
                config_dir = os.path.expanduser("~/.config/amdtop/themes")
                if not os.path.exists(config_dir):
                    return
                    
                for filename in os.listdir(config_dir):
                    if filename.endswith('.json'):
                        theme_path = os.path.join(config_dir, filename)
                        theme_name = filename[:-5]  # Remove .json
                        try:
                            with open(theme_path, 'r') as f:
                                theme_data = json.load(f)
                                # Validate theme data
                                if self._validate_theme(theme_data):
                                    self.themes[theme_name] = theme_data
                        except (json.JSONDecodeError, OSError):
                            print(f"Error loading custom theme: {theme_path}")
        
            def _validate_theme(self, theme_data: Dict[str, str]) -> bool:
                """Validate that a theme contains all required colors"""
                required_colors = set(DARK_THEME.keys())
                theme_colors = set(theme_data.keys())
                return required_colors.issubset(theme_colors)
        
            def _get_theme_colors(self) -> Dict[str, str]:
                """Get colors for current theme"""
                return self.themes[self.current_theme]
        
            def toggle_theme(self) -> None:
                """Toggle between available themes"""
                # Get list of available themes
                theme_names = list(self.themes.keys())
                # Find current theme index
                current_index = theme_names.index(self.current_theme)
                # Get next theme
                next_index = (current_index + 1) % len(theme_names)
                self.current_theme = theme_names[next_index]
                
                # Update theme colors
                self.theme_colors = self._get_theme_colors()
                # Update config
                self.config["theme"] = self.current_theme
        
            def get_theme_colors(self) -> Dict[str, str]:
                """Get current theme colors"""
                return self.theme_colors
        
            def get_current_theme(self) -> str:
                """Get current theme name"""
                return self.current_theme
        
            def add_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
                """Add a new custom theme"""
                if not self._validate_theme(colors):
                    return False
                    
                # Save theme to config directory
                config_dir = os.path.expanduser("~/.config/amdtop/themes")
                os.makedirs(config_dir, exist_ok=True)
                
                theme_path = os.path.join(config_dir, f"{name}.json")
                try:
                    with open(theme_path, 'w') as f:
                        json.dump(colors, f, indent=2)
                    self.themes[name] = colors
                    return True
                except OSError:
                    return False
        
            def generate_css(self) -> str:
                """Generate CSS from current theme colors"""
                colors = self.get_theme_colors()
                css = f"""
                .app-grid {{
                    background: {colors['background']};
                    color: {colors['text']};
                }}
                
                Header {{
                    background: {colors['header_background']};
                }}
                
                .widget {{
                    background: {colors['widget_background']};
                    border: 1px solid {colors['widget_border']};
                }}
                
                Tab {{
                    color: {colors['text_muted']};
                }}
                
                Tab:hover {{
                    background: {colors['tab_hover']};
                }}
                
                Tab.-active {{
                    background: {colors['tab_active']};
                    color: {colors['text']};
                }}
                
                #cpu_graph {{
                    color: {colors['cpu_graph']};
                }}
                
                #memory_graph {{
                    color: {colors['memory_graph']};
                }}
                
                #gpu_graph {{
                    color: {colors['gpu_graph']};
                }}
                """
                return css
        
        # Test the module if run directly
        if __name__ == "__main__":
            config = {"theme": "dark"}
            theme_manager = ThemeManager(config)
            
            # Print current theme colors
            print("Current theme:", theme_manager.get_current_theme())
            print("\nTheme colors:")
            for key, value in theme_manager.get_theme_colors().items():
                print(f"{key}: {value}")
            
            # Test theme toggle
            print("\nToggling theme...")
            theme_manager.toggle_theme()
            print("New theme:", theme_manager.get_current_theme())
            
            # Test custom theme
            print("\nAdding custom theme...")
            custom_theme = DARK_THEME.copy()
            custom_theme["background"] = "#000000"
            success = theme_manager.add_custom_theme("custom", custom_theme)
            print("Custom theme added:", success)
            
            # Print generated CSS
            print("\nGenerated CSS:")
            print(theme_manager.generate_css())"""
AMDTop - Main Application File
A TUI for monitoring AMD CPU/GPU systems in real-time.
"""
import sys
import time
import threading
from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better performance
import matplotlib.pyplot as plt

from PIL import Image
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Label, Tabs, Tab, Button

from config_loader import load_config, create_default_config, save_config
from network_monitor import NetworkProcessMonitor
from temperature_monitor import TemperatureMonitor
from theme_manager import ThemeManager

# Import pyamdgpu for AMD GPU monitoring
try:
    import pyamdgpu
    PYAMDGPU_AVAILABLE = True
except ImportError:
    PYAMDGPU_AVAILABLE = False
    print("Warning: pyamdgpu not available. Using mock GPU data.")

class GPUInfo:
    """Class to get AMD GPU information using pyamdgpu."""
    def __init__(self):
        if PYAMDGPU_AVAILABLE:
            self.gpu = pyamdgpu.AMDGPU()
        else:
            self.gpu = None

    def get_temperature(self):
        if self.gpu:
            try:
                return self.gpu.query_temperature()
            except Exception:
                return None
        return None

    def get_usage(self):
        if self.gpu:
            try:
                return self.gpu.query_usage()
            except Exception:
                return None
        return None

    def get_memory_usage(self):
        if self.gpu:
            try:
                return self.gpu.query_vram_usage()
            except Exception:
                return None
        return None

class Graph(Static):
    """A widget to display a matplotlib graph."""
    def __init__(self, title, data_func, color="blue", max_points=60, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data_func = data_func
        self.color = color
        self.max_points = max_points
        self.data = []
        self.set_interval(1, self.update_data)

    def update_data(self):
        value = self.data_func()
        if value is not None:
            self.data.append(value)
            if len(self.data) > self.max_points:
                self.data.pop(0)
        self.update_graph()

    def update_graph(self):
        plt.clf()
        plt.figure(figsize=(4, 1.5))
        plt.plot(self.data, color=self.color)
        plt.title(self.title)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        self.update(img)

class MultiLineGraph(Static):
    """A widget to display a matplotlib graph with multiple lines."""
    def __init__(self, title, data_funcs, labels, colors, max_points=60, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data_funcs = data_funcs
        self.labels = labels
        self.colors = colors
        self.max_points = max_points
        self.data = [[] for _ in data_funcs]
        self.set_interval(1, self.update_data)

    def update_data(self):
        for i, func in enumerate(self.data_funcs):
            value = func()
            if value is not None:
                self.data[i].append(value)
                if len(self.data[i]) > self.max_points:
                    self.data[i].pop(0)
        self.update_graph()

    def update_graph(self):
        plt.clf()
        plt.figure(figsize=(4, 1.5))
        for i, d in enumerate(self.data):
            plt.plot(d, color=self.colors[i], label=self.labels[i])
        plt.title(self.title)
        plt.legend()
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        self.update(img)

class CPUGraph(Graph):
    """Widget to display CPU usage graph."""
    def __init__(self, color="green", max_points=60, **kwargs):
        import psutil
        super().__init__("CPU Usage (%)", lambda: psutil.cpu_percent(), color, max_points, **kwargs)

class GPUGraph(Graph):
    """Widget to display GPU temperature graph."""
    def __init__(self, gpu_info, color="red", max_points=60, **kwargs):
        super().__init__("GPU Temp (°C)", gpu_info.get_temperature, color, max_points, **kwargs)

class MemoryGraph(Graph):
    def __init__(self, color="blue", max_points=60, **kwargs):
        import psutil
        super().__init__("Memory Usage (%)", lambda: psutil.virtual_memory().percent, color, max_points, **kwargs)

class TemperatureGraph(Graph):
    def __init__(self, temp_monitor, color="orange", max_points=60, **kwargs):
        super().__init__("CPU Temp (°C)", temp_monitor.get_cpu_temperature, color, max_points, **kwargs)

class TopProcesses(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_interval(2, self.update_table)

    def update_table(self):
        import psutil
        procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                       key=lambda p: p.info['cpu_percent'], reverse=True)[:10]
        table = Table(title="Top Processes")
        table.add_column("PID")
        table.add_column("Name")
        table.add_column("CPU %")
        for p in procs:
            table.add_row(str(p.info['pid']), p.info['name'], str(p.info['cpu_percent']))
        self.update(table)

class ThemeToggleButton(Button):
    def __init__(self, theme_manager, **kwargs):
        super().__init__("Toggle Theme", **kwargs)
        self.theme_manager = theme_manager

    def on_click(self):
        self.theme_manager.toggle_theme()
        self.app.refresh()

class AMDTopApp(App):
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_theme", "Toggle Theme"),
        ("h", "show_help", "Help"),
        ("1", "switch_tab('system')", "System"),
        ("2", "switch_tab('disk')", "Disk"),
        ("3", "switch_tab('network')", "Network"),
        ("4", "switch_tab('temperature')", "Temperature"),
    ]

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or load_config()
        self.theme_manager = ThemeManager(self.config)
        self.gpu_info = GPUInfo()
        self.temp_monitor = TemperatureMonitor()
        self.net_monitor = NetworkProcessMonitor()
        self.current_tab = self.config.get("default_tab", "system")

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with Tabs():
                yield Tab("System", id="system")
                yield Tab("Disk", id="disk")
                yield Tab("Network", id="network")
                yield Tab("Temperature", id="temperature")
            with Container(id="main-content"):
                if self.current_tab == "system":
                    yield CPUGraph(color=self.theme_manager.theme_colors.get("cpu_graph", "green"))
                    yield MemoryGraph(color=self.theme_manager.theme_colors.get("memory_graph", "blue"))
                    yield TopProcesses()
                elif self.current_tab == "network":
                    yield MultiLineGraph(
                        "Network",
                        [lambda: 0, lambda: 0],  # Placeholder
                        ["Download", "Upload"],
                        [self.theme_manager.theme_colors.get("network_download", "green"),
                         self.theme_manager.theme_colors.get("network_upload", "orange")]
                    )
                elif self.current_tab == "temperature":
                    yield TemperatureGraph(self.temp_monitor, color="orange")
                    yield GPUGraph(self.gpu_info, color="red")
        yield ThemeToggleButton(self.theme_manager)
        yield Footer()

    def action_quit(self):
        self.exit()

    def action_toggle_theme(self):
        self.theme_manager.toggle_theme()
        self.refresh()

    def action_show_help(self):
        from help_screen import HelpScreen
        self.push_screen(HelpScreen())

    def action_switch_tab(self, tab):
        self.current_tab = tab
        self.refresh()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AMDTop - AMD CPU/GPU monitoring TUI")
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument("--create-config", action="store_true", help="Create default config file")
    args = parser.parse_args()

    if args.create_config:
        create_default_config()
        print("Default config created.")
        sys.exit(0)

    config = load_config(args.config) if args.config else load_config()
    app = AMDTopApp(config)
    app.run()

if __name__ == "__main__":
    main()
