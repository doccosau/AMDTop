#!/usr/bin/env python3
"""
Temperature monitoring module for AMDTop
Uses lm-sensors to get system temperatures
"""
from typing import Dict, List, Tuple, Optional
import subprocess
import re
import shutil
from collections import deque

class TemperatureMonitor:
    """
    Monitors system temperatures using lm-sensors
    """
    def __init__(self):
        """Initialize temperature monitor"""
        self.sensors_available = self._check_sensors_available()
        if not self.sensors_available:
            print("Warning: lm-sensors not found. Temperature monitoring disabled.")
            
        # Temperature data storage
        self.temperatures: Dict[str, Dict[str, Tuple[float, Optional[float]]]] = {}
        
        # History storage (last 60 readings for each sensor)
        self.history: Dict[str, Dict[str, deque]] = {}
        
        # Maximum history length
        self.max_history = 60
        
        # Update temperatures on init
        self.update()

    def _check_sensors_available(self) -> bool:
        """Check if lm-sensors is available"""
        return shutil.which('sensors') is not None

    def update(self) -> None:
        """Update temperature readings"""
        if not self.sensors_available:
            return
            
        try:
            output = subprocess.check_output(['sensors'], 
                                          text=True, 
                                          stderr=subprocess.DEVNULL)
            self._parse_sensors_output(output)
            self._update_history()
        except subprocess.SubprocessError:
            print("Error running sensors command")

    def _parse_sensors_output(self, output: str) -> None:
        """Parse the output from sensors command"""
        current_adapter = None
        temperatures = {}
        
        for line in output.splitlines():
            # Check for adapter
            if "Adapter:" in line:
                current_adapter = line.split(":")[1].strip()
                temperatures[current_adapter] = {}
                continue
                
            # Parse temperature readings
            match = re.match(r'^([^:]+):\s+[+-]?([\d.]+)°C\s+\(high = [+-]?([\d.]+)°C\)?', line)
            if match and current_adapter:
                name, temp, high = match.groups()
                name = name.strip()
                temp = float(temp)
                high = float(high) if high else None
                temperatures[current_adapter][name] = (temp, high)
        
        self.temperatures = temperatures

    def _update_history(self) -> None:
        """Update temperature history"""
        for adapter, readings in self.temperatures.items():
            if adapter not in self.history:
                self.history[adapter] = {}
                
            for name, (temp, _) in readings.items():
                if name not in self.history[adapter]:
                    self.history[adapter][name] = deque(maxlen=self.max_history)
                self.history[adapter][name].append(temp)

    def get_all_temperatures(self) -> Dict[str, Dict[str, Tuple[float, Optional[float]]]]:
        """Get all temperature readings"""
        return self.temperatures

    def get_temperature_history(self, sensor_name: str, temp_name: str) -> List[float]:
        """Get temperature history for a specific sensor"""
        if sensor_name in self.history and temp_name in self.history[sensor_name]:
            return list(self.history[sensor_name][temp_name])
        return []

    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (tries different common sensor names)"""
        cpu_sensors = [
            ('k10temp-*', 'Tctl'),         # AMD Ryzen
            ('coretemp-*', 'Package id 0'), # Intel
            ('zenpower-*', 'Tctl'),        # AMD Zen
        ]
        
        for adapter in self.temperatures:
            for sensor_pattern, temp_name in cpu_sensors:
                if re.match(sensor_pattern, adapter):
                    readings = self.temperatures[adapter]
                    if temp_name in readings:
                        return readings[temp_name][0]
        return None

    def get_motherboard_temperature(self) -> Optional[float]:
        """Get motherboard temperature"""
        mb_sensors = ['it8620-*', 'nct6775-*']
        
        for adapter in self.temperatures:
            for sensor_pattern in mb_sensors:
                if re.match(sensor_pattern, adapter):
                    # Look for likely motherboard temp sensors
                    for name, (temp, _) in self.temperatures[adapter].items():
                        if 'SYSTIN' in name or 'Board' in name:
                            return temp
        return None

    def print_all_temperatures(self) -> None:
        """Print all temperature readings (for debugging)"""
        for adapter, readings in self.temperatures.items():
            print(f"\nAdapter: {adapter}")
            for name, (temp, high) in readings.items():
                high_str = f" (High = {high}°C)" if high else ""
                print(f"  {name}: {temp}°C{high_str}")

# Test the module if run directly
if __name__ == "__main__":
    monitor = TemperatureMonitor()
    
    print("Testing temperature monitor...")
    print("\nAll temperatures:")
    monitor.print_all_temperatures()
    
    print("\nCPU temperature:", monitor.get_cpu_temperature())
    print("Motherboard temperature:", monitor.get_motherboard_temperature())
    
    # Test history
    print("\nUpdating temperatures multiple times...")
    for _ in range(5):
        monitor.update()
    
    if monitor.temperatures:
        # Get first available sensor and temp name
        adapter = next(iter(monitor.temperatures))
        temp_name = next(iter(monitor.temperatures[adapter]))
        history = monitor.get_temperature_history(adapter, temp_name)
        print(f"\nTemperature history for {adapter} {temp_name}:")
        print(history)
