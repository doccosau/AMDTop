#!/usr/bin/env python3
"""
Configuration loader for AMDTop
Handles loading, saving, and validating configuration
"""
import os
import sys
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConfigPaths:
    """Configuration file paths"""
    LOCAL: str = "./config.yaml"
    USER: str = "~/.config/amdtop/config.yaml"
    SYSTEM: str = "/etc/amdtop/config.yaml"

# Default configuration with type hints
DEFAULT_CONFIG: Dict[str, Any] = {
    "intervals": {
        "graphs": 1.0,        # Update interval for graphs (seconds)
        "processes": 2.0,     # Update interval for process list
        "temperature": 5.0,   # Update interval for temperature sensors
        "network": 1.0,       # Update interval for network stats
    },
    "colors": {
        "cpu_graph": "green",
        "gpu_graph": "red",
        "memory_graph": "blue",
        "disk_read": "blue",
        "disk_write": "red",
        "network_download": "green",
        "network_upload": "orange",
        "temperature": "orange",
        "warning": "yellow",
        "error": "red",
    },
    "display": {
        "graph_history": 60,    # Number of points in graphs
        "process_count": 10,    # Number of processes to show
        "partition_count": 3,   # Number of disk partitions to show
        "interface_count": 3,   # Number of network interfaces to show
        "show_gpu": True,       # Show GPU information if available
        "show_temperature": True,  # Show temperature information
        "compact_mode": False,  # Use compact display mode
    },
    "alerts": {
        "cpu_temp_warning": 70,   # CPU temperature warning threshold (°C)
        "cpu_temp_critical": 85,  # CPU temperature critical threshold
        "gpu_temp_warning": 75,   # GPU temperature warning threshold
        "gpu_temp_critical": 90,  # GPU temperature critical threshold
        "enable_notifications": True,  # Enable system notifications
    },
    "default_tab": "system",    # Options: system, disk, network, temperature
    "theme": "dark",           # Options: dark, light
    "log_level": "INFO",       # Options: DEBUG, INFO, WARNING, ERROR
}

def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration values and return any errors

    Args:
        config: Configuration dictionary to validate

    Returns:
        Dictionary of validation errors (empty if valid)
    """
    errors = {}

    # Validate intervals
    for key, value in config.get("intervals", {}).items():
        if not isinstance(value, (int, float)) or value <= 0:
            errors[f"intervals.{key}"] = f"Must be a positive number, got {value}"

    # Validate display counts
    for key, value in config.get("display", {}).items():
        if key.endswith("_count"):
            if not isinstance(value, int) or value <= 0:
                errors[f"display.{key}"] = f"Must be a positive integer, got {value}"

    # Validate temperature thresholds
    alerts = config.get("alerts", {})
    if alerts.get("cpu_temp_warning", 0) >= alerts.get("cpu_temp_critical", 100):
        errors["alerts.cpu_temp"] = "Warning temperature must be lower than critical"
    if alerts.get("gpu_temp_warning", 0) >= alerts.get("gpu_temp_critical", 100):
        errors["alerts.gpu_temp"] = "Warning temperature must be lower than critical"

    return errors

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file with validation

    Args:
        config_path: Optional path to configuration file

    Returns:
        Validated configuration dictionary
    """
    paths = ConfigPaths()
    search_paths = [
        config_path if config_path else None,
        paths.LOCAL,
        os.path.expanduser(paths.USER),
        paths.SYSTEM
    ]

    config = DEFAULT_CONFIG.copy()
    loaded = False

    for path in filter(None, search_paths):
        try:
            with open(path, 'r') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    deep_update(config, loaded_config)
                    print(f"Loaded configuration from {path}")
                    loaded = True
                    break
        except FileNotFoundError:
            continue
        except yaml.YAMLError as e:
            print(f"YAML error in config file {path}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Error reading config file {path}: {e}", file=sys.stderr)
            continue

    if not loaded:
        print("No configuration file found, using defaults")

    # Validate configuration
    errors = validate_config(config)
    if errors:
        print("Configuration validation errors:", file=sys.stderr)
        for key, error in errors.items():
            print(f"  {key}: {error}", file=sys.stderr)

    return config

def deep_update(original: Dict, update: Dict) -> Dict:
    """Recursively update a dictionary"""
    for key, value in update.items():
        if (
            key in original 
            and isinstance(original[key], dict) 
            and isinstance(value, dict)
        ):
            deep_update(original[key], value)
        else:
            original[key] = value
    return original

def save_config(config: Dict[str, Any], path: Optional[str] = None) -> bool:
    """
    Save configuration to a YAML file

    Args:
        config: Configuration dictionary to save
        path: Optional path to save to (default: user config path)

    Returns:
        True if save was successful, False otherwise
    """
    if path is None:
        path = os.path.expanduser(ConfigPaths.USER)

    try:
        # Validate before saving
        errors = validate_config(config)
        if errors:
            print("Invalid configuration, not saving:", file=sys.stderr)
            for key, error in errors.items():
                print(f"  {key}: {error}", file=sys.stderr)
            return False

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save configuration
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"Configuration saved to {path}")
        return True

    except Exception as e:
        print(f"Error saving configuration to {path}: {e}", file=sys.stderr)
        return False

def create_default_config(path: str = "./config.yaml") -> bool:
    """Create a default configuration file"""
    return save_config(DEFAULT_CONFIG, path)

# Test module if run directly
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMDTop Configuration Manager")
    parser.add_argument("--create", action="store_true", 
                       help="Create default configuration file")
    parser.add_argument("--validate", action="store_true",
                       help="Validate existing configuration")
    parser.add_argument("--path", help="Path to configuration file")
    
    args = parser.parse_args()

    if args.create:
        create_default_config(args.path if args.path else ConfigPaths.LOCAL)
    elif args.validate:
        config = load_config(args.path)
        errors = validate_config(config)
        if not errors:
            print("Configuration is valid")
    else:
        print("Current configuration:")
        config = load_config(args.path)
        yaml.dump(config, sys.stdout, default_flow_style=False)
