#!/usr/bin/env python3
"""
Help screen for AMDTop
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static, Button

class HelpScreen(Screen):
    """Help screen showing keyboard shortcuts and usage information."""
    
    BINDINGS = [("escape", "app.pop_screen", "Close")]
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Container():
            with Vertical(classes="help-text"):
                yield Static("[bold]AMDTop Help[/bold]\n\n")
                
                yield Static("[bold]Keyboard Shortcuts:[/bold]\n")
                yield Static("1: Switch to System tab")
                yield Static("2: Switch to Disk I/O tab")
                yield Static("3: Switch to Network tab")
                yield Static("4: Switch to Temperature tab")
                yield Static("t: Toggle between dark and light themes")
                yield Static("h: Show/hide this help screen")
                yield Static("q: Quit the application")
                yield Static("Escape: Close this help screen\n")
                
                yield Static("[bold]Usage Tips:[/bold]\n")
                yield Static("• The theme toggle button is in the top-right corner")
                yield Static("• Graphs update according to the interval in the config file")
                yield Static("• Temperature monitoring requires lm-sensors to be installed")
                yield Static("• GPU monitoring works best with AMD GPUs and pyamdgpu installed")
                yield Static("• Configuration is saved in ~/.config/amdtop/config.yaml\n")
                
                yield Button("Close", id="close_help")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "close_help":
            self.app.pop_screen()
