#!/usr/bin/env python3
"""
Configuration loader for AMDTop
"""
import os
import yaml
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    "intervals": {
        "graphs": 1.0,
        "processes": 2.0,
    },
    "colors": {
        "cpu_graph": "green",
        "gpu_graph": "red",
        "memory_graph": "blue",
        "disk_read": "blue",
        "disk_write": "red",
        "network_download": "green",
        "network_upload": "orange",
    },
    "display": {
        "graph_history": 60,
        "process_count": 10,
        "partition_count": 3,
        "interface_count": 3,
    },
    "default_tab": "system",  # Options: system, disk, network, temperature
    "theme": "dark",  # Options: dark, light
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file. If None, looks in standard locations.
        
    Returns:
        Dict containing the configuration.
    """
    # Configuration file search paths
    search_paths = [
        # Current directory
        "./config.yaml",
        # User's home directory
        os.path.expanduser("~/.config/amdtop/config.yaml"),
        # System-wide configuration
        "/etc/amdtop/config.yaml",
    ]
    
    # If a specific path is provided, check it first
    if config_path:
        search_paths.insert(0, config_path)
    
    # Try to load from each path
    config = DEFAULT_CONFIG.copy()
    for path in search_paths:
        try:
            with open(path, 'r') as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    # Merge with default config (deep update)
                    deep_update(config, loaded_config)
                    print(f"Loaded configuration from {path}")
                    break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error loading configuration from {path}: {e}")
    
    return config

def deep_update(original: Dict, update: Dict) -> Dict:
    """
    Recursively update a dictionary.
    
    Args:
        original: Original dictionary to update
        update: Dictionary with updates
        
    Returns:
        Updated dictionary
    """
    for key, value in update.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            deep_update(original[key], value)
        else:
            original[key] = value
    return original

def get_config_path(config_path: str = None) -> str:
    """
    Get the path to the configuration file.
    
    Args:
        config_path: Path to the configuration file. If None, looks in standard locations.
        
    Returns:
        Path to the configuration file.
    """
    # Configuration file search paths
    search_paths = [
        # Current directory
        "./config.yaml",
        # User's home directory
        os.path.expanduser("~/.config/amdtop/config.yaml"),
        # System-wide configuration
        "/etc/amdtop/config.yaml",
    ]
    
    # If a specific path is provided, check it first
    if config_path:
        search_paths.insert(0, config_path)
    
    # Try to find an existing config file
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    # If no config file exists, use the user's home directory
    return os.path.expanduser("~/.config/amdtop/config.yaml")

def save_config(config: Dict[str, Any], path: str = None) -> None:
    """
    Save configuration to a YAML file.
    
    Args:
        config: Configuration dictionary
        path: Path where to save the configuration file. If None, uses the default path.
    """
    if path is None:
        path = get_config_path()
        
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write configuration
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"Saved configuration to {path}")
    except Exception as e:
        print(f"Error saving configuration to {path}: {e}")

def create_default_config(path: str = "./config.yaml") -> None:
    """
    Create a default configuration file.
    
    Args:
        path: Path where to create the configuration file
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write default configuration
        with open(path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        print(f"Created default configuration at {path}")
    except Exception as e:
        print(f"Error creating default configuration at {path}: {e}")

if __name__ == "__main__":
    # If run directly, create a default configuration file
    create_default_config()
