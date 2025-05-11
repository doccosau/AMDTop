#!/usr/bin/env python3
"""
Theme manager for AMDTop
Handles dark and light themes
"""
from typing import Dict, Any

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
}

class ThemeManager:
    """
    Manages application themes
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_theme = config.get("theme", "dark")
        
        # Initialize theme colors
        self.theme_colors = self._get_theme_colors()
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """
        Get the colors for the current theme
        
        Returns:
            Dict of color names to color values
        """
        if self.current_theme == "light":
            return LIGHT_THEME.copy()
        else:
            return DARK_THEME.copy()
    
    def toggle_theme(self) -> None:
        """
        Toggle between dark and light themes
        """
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        
        # Update theme colors
        self.theme_colors = self._get_theme_colors()
        
        # Update config
        self.config["theme"] = self.current_theme
    
    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get the colors for the current theme
        
        Returns:
            Dict of color names to color values
        """
        return self.theme_colors
    
    def get_current_theme(self) -> str:
        """
        Get the current theme name
        
        Returns:
            Theme name ("dark" or "light")
        """
        return self.current_theme
    
    def generate_css(self) -> str:
        """
        Generate CSS for the current theme
        
        Returns:
            CSS string
        """
        colors = self.theme_colors
        
        return f"""
        Screen {{
            background: {colors["background"]};
            color: {colors["text"]};
        }}
        
        Header {{
            background: {colors["header_background"]};
            color: {colors["text"]};
        }}
        
        Footer {{
            background: {colors["header_background"]};
            color: {colors["text"]};
        }}
        
        .container {{
            height: 100%;
            padding: 1;
        }}
        
        .graph {{
            height: 40%;
            border: solid {colors["widget_border"]};
            background: {colors["widget_background"]};
            margin: 1;
        }}
        
        .metrics {{
            width: 30%;
            border: solid {colors["widget_border"]};
            background: {colors["widget_background"]};
            margin: 1;
        }}
        
        .processes {{
            height: 40%;
            border: solid {colors["widget_border"]};
            background: {colors["widget_background"]};
            margin: 1;
        }}
        
        .tabs {{
            background: {colors["widget_background"]};
            color: {colors["text"]};
        }}
        
        Tab {{
            padding: 1 2;
        }}
        
        Tab:hover {{
            background: {colors["tab_hover"]};
        }}
        
        Tab.-active {{
            background: {colors["tab_active"]};
            color: {colors["text"]};
        }}
        
        .theme-toggle {{
            dock: right;
            background: {colors["header_background"]};
            color: {colors["text"]};
            border: none;
            padding: 0 1;
            margin: 0 1;
        }}
        
        .theme-toggle:hover {{
            background: {colors["tab_hover"]};
        }}
        
        .help-text {{
            background: {colors["widget_background"]};
            color: {colors["text"]};
            border: solid {colors["widget_border"]};
            padding: 1;
            margin: 1;
        }}
        """

# Test the module if run directly
if __name__ == "__main__":
    config = {"theme": "dark"}
    theme_manager = ThemeManager(config)
    
    print(f"Current theme: {theme_manager.get_current_theme()}")
    print("Theme colors:")
    for name, color in theme_manager.get_theme_colors().items():
        print(f"  {name}: {color}")
    
    print("\nToggling theme...")
    theme_manager.toggle_theme()
    
    print(f"Current theme: {theme_manager.get_current_theme()}")
    print("Theme colors:")
    for name, color in theme_manager.get_theme_colors().items():
        print(f"  {name}: {color}")
