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
    print(theme_manager.generate_css())
