#!/usr/bin/env python3
"""
Help screen for AMDTop
Provides user documentation and keyboard shortcuts
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Button, Label

class HelpSection(Static):
    """A section in the help screen"""
    def __init__(self, title: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Label(f"[b]{self.title}[/b]", classes="help-title")
        yield Static(self.content, classes="help-content")

class HelpScreen(Screen):
    """Help screen showing keyboard shortcuts and usage information"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("q", "app.pop_screen", "Close"),
    ]
    
    CSS = """
    HelpScreen {
        align: center middle;
    }
    
    .help-container {
        width: 80%;
        height: 90%;
        border: solid green;
        background: $surface;
        padding: 1 2;
    }
    
    .help-title {
        color: $accent;
        margin: 1 0;
    }
    
    .help-content {
        margin: 0 0 1 2;
    }
    
    .help-footer {
        margin-top: 1;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        with Container(classes="help-container"):
            with Vertical():
                yield HelpSection(
                    "Keyboard Shortcuts",
                    """
                    • q or Esc: Quit/Close
                    • t: Toggle Theme (Dark/Light)
                    • h: Show this Help Screen
                    • 1-4: Switch Tabs
                    • r: Reset Graphs
                    • p: Pause/Resume Updates
                    """
                )
                
                yield HelpSection(
                    "Tabs",
                    """
                    1. System: CPU, Memory, and Process usage
                    2. Disk: Disk I/O and storage information
                    3. Network: Network usage by process
                    4. Temperature: System temperature sensors
                    """
                )
                
                yield HelpSection(
                    "System Requirements",
                    """
                    • Linux operating system
                    • Python 3.7+
                    • lm-sensors package (for temperature monitoring)
                    • AMD GPU drivers (for GPU monitoring)
                    """
                )
                
                yield HelpSection(
                    "Configuration",
                    """
                    Config file location: ~/.config/amdtop/config.yaml
                    • Customize update intervals
                    • Change color scheme
                    • Adjust graph history length
                    • Set default tab
                    """
                )
                
                with Container(classes="help-footer"):
                    yield Button("Close", variant="primary", id="close_help")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        if event.button.id == "close_help":
            self.app.pop_screen()

    def on_key(self, event) -> None:
        """Handle key press events"""
        if event.key in {"escape", "q"}:
            self.app.pop_screen()

# Test the help screen if run directly
if __name__ == "__main__":
    from textual.app import App
    
    class HelpApp(App):
        def compose(self) -> ComposeResult:
            yield Button("Show Help", id="show_help")
            
        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "show_help":
                self.push_screen(HelpScreen())
    
    app = HelpApp()
    app.run()
