#!/usr/bin/env python3
"""
Temperature monitoring module for AMDTop
Uses lm-sensors to get system temperatures
"""
import os
import time
import subprocess
import re
from typing import Dict, List, Tuple, Optional

class TemperatureMonitor:
    """
    Monitors system temperatures using lm-sensors
    """
    def __init__(self):
        # Check if sensors command is available
        self.sensors_available = self._check_sensors_available()
        
        # Initialize data structures
        self.sensors_data = {}  # sensor_name -> {temp_name -> (temp_value, critical_value)}
        self.sensor_history = {}  # sensor_name -> {temp_name -> [values]}
        self.max_history_points = 60  # Keep 60 data points for history
        
        # Update immediately on initialization
        if self.sensors_available:
            self.update()
    
    def _check_sensors_available(self) -> bool:
        """
        Check if the sensors command is available
        
        Returns:
            bool: True if sensors command is available, False otherwise
        """
        try:
            # Try to run the sensors command
            subprocess.run(["sensors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: 'sensors' command not found. Install lm-sensors package for temperature monitoring.")
            return False
    
    def update(self) -> None:
        """
        Update temperature data from sensors
        """
        if not self.sensors_available:
            return
        
        try:
            # Run sensors command and get output
            result = subprocess.run(["sensors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = result.stdout
            
            # Parse the output
            self._parse_sensors_output(output)
            
            # Update history
            self._update_history()
        except subprocess.SubprocessError as e:
            print(f"Error running sensors command: {e}")
    
    def _parse_sensors_output(self, output: str) -> None:
        """
        Parse the output of the sensors command
        
        Args:
            output: Output string from sensors command
        """
        current_sensor = None
        self.sensors_data = {}
        
        # Split output into lines
        lines = output.strip().split('\n')
        
        for line in lines:
            # Check if this is a sensor name line (no indentation)
            if line and not line.startswith(' '):
                current_sensor = line.strip()
                self.sensors_data[current_sensor] = {}
            
            # Check if this is a temperature line
            elif current_sensor and 'temp' in line.lower() and ':' in line:
                # Extract temperature name and value
                parts = line.split(':')
                temp_name = parts[0].strip()
                
                # Extract temperature value and critical value if available
                value_part = parts[1].strip()
                
                # Extract the temperature value
                temp_value_match = re.search(r'([+-]?\d+\.\d+)°C', value_part)
                if temp_value_match:
                    temp_value = float(temp_value_match.group(1))
                else:
                    continue  # Skip if no temperature value found
                
                # Extract critical temperature if available
                crit_value = None
                crit_match = re.search(r'crit\s*=\s*([+-]?\d+\.\d+)°C', value_part)
                if crit_match:
                    crit_value = float(crit_match.group(1))
                
                # Store the temperature data
                self.sensors_data[current_sensor][temp_name] = (temp_value, crit_value)
    
    def _update_history(self) -> None:
        """
        Update temperature history
        """
        # Initialize history for new sensors
        for sensor_name, temps in self.sensors_data.items():
            if sensor_name not in self.sensor_history:
                self.sensor_history[sensor_name] = {}
            
            for temp_name, (temp_value, _) in temps.items():
                if temp_name not in self.sensor_history[sensor_name]:
                    self.sensor_history[sensor_name][temp_name] = []
                
                # Add current value to history
                self.sensor_history[sensor_name][temp_name].append(temp_value)
                
                # Limit history length
                if len(self.sensor_history[sensor_name][temp_name]) > self.max_history_points:
                    self.sensor_history[sensor_name][temp_name] = self.sensor_history[sensor_name][temp_name][-self.max_history_points:]
    
    def get_all_temperatures(self) -> Dict[str, Dict[str, Tuple[float, Optional[float]]]]:
        """
        Get all temperature data
        
        Returns:
            Dict mapping sensor names to dicts of temperature names to (value, critical) tuples
        """
        return self.sensors_data
    
    def get_temperature_history(self, sensor_name: str, temp_name: str) -> List[float]:
        """
        Get temperature history for a specific sensor and temperature
        
        Args:
            sensor_name: Name of the sensor
            temp_name: Name of the temperature
            
        Returns:
            List of temperature values
        """
        if sensor_name in self.sensor_history and temp_name in self.sensor_history[sensor_name]:
            return self.sensor_history[sensor_name][temp_name]
        return []
    
    def get_cpu_temperature(self) -> Optional[float]:
        """
        Get the CPU temperature (tries to find the most relevant CPU temperature)
        
        Returns:
            CPU temperature or None if not available
        """
        # Look for CPU temperature in different possible sensor names
        cpu_sensors = [s for s in self.sensors_data.keys() if 'cpu' in s.lower() or 'k10temp' in s.lower() or 'coretemp' in s.lower()]
        
        for sensor in cpu_sensors:
            # Look for the most relevant temperature (Tdie, Tctl, or Package)
            for temp_name in ['Tdie', 'Tctl', 'Package id 0', 'Core 0']:
                if temp_name in self.sensors_data[sensor]:
                    return self.sensors_data[sensor][temp_name][0]
            
            # If specific names not found, look for any temperature
            for temp_name, (temp_value, _) in self.sensors_data[sensor].items():
                if 'temp' in temp_name.lower():
                    return temp_value
        
        return None
    
    def get_motherboard_temperature(self) -> Optional[float]:
        """
        Get the motherboard temperature
        
        Returns:
            Motherboard temperature or None if not available
        """
        # Look for motherboard temperature in different possible sensor names
        mb_sensors = [s for s in self.sensors_data.keys() if 'motherboard' in s.lower() or 'asus' in s.lower() or 'gigabyte' in s.lower() or 'msi' in s.lower()]
        
        for sensor in mb_sensors:
            # Look for the most relevant temperature
            for temp_name, (temp_value, _) in self.sensors_data[sensor].items():
                if 'temp' in temp_name.lower() or 'mb' in temp_name.lower():
                    return temp_value
        
        return None
    
    def get_important_temperatures(self) -> Dict[str, float]:
        """
        Get the most important temperatures (CPU, GPU, motherboard)
        
        Returns:
            Dict mapping temperature names to values
        """
        important_temps = {}
        
        # Get CPU temperature
        cpu_temp = self.get_cpu_temperature()
        if cpu_temp is not None:
            important_temps['CPU'] = cpu_temp
        
        # Get motherboard temperature
        mb_temp = self.get_motherboard_temperature()
        if mb_temp is not None:
            important_temps['Motherboard'] = mb_temp
        
        # Add other important temperatures
        for sensor_name, temps in self.sensors_data.items():
            # Add GPU temperature if found
            if 'gpu' in sensor_name.lower() or 'nvidia' in sensor_name.lower() or 'amdgpu' in sensor_name.lower():
                for temp_name, (temp_value, _) in temps.items():
                    if 'temp' in temp_name.lower():
                        important_temps[f'GPU ({sensor_name})'] = temp_value
                        break
            
            # Add NVMe or SSD temperatures if found
            if 'nvme' in sensor_name.lower() or 'ssd' in sensor_name.lower():
                for temp_name, (temp_value, _) in temps.items():
                    if 'temp' in temp_name.lower():
                        important_temps[f'Storage ({sensor_name})'] = temp_value
                        break
        
        return important_temps

# Test the module if run directly
if __name__ == "__main__":
    monitor = TemperatureMonitor()
    
    if not monitor.sensors_available:
        print("lm-sensors not available. Please install it to use temperature monitoring.")
        exit(1)
    
    # Update a few times to get meaningful data
    for _ in range(3):
        monitor.update()
        time.sleep(1)
    
    # Print important temperatures
    print("Important temperatures:")
    for name, temp in monitor.get_important_temperatures().items():
        print(f"{name}: {temp}°C")
    
    # Print all temperatures
    print("\nAll temperatures:")
    for sensor_name, temps in monitor.get_all_temperatures().items():
        print(f"{sensor_name}:")
        for temp_name, (temp_value, crit_value) in temps.items():
            crit_str = f" (Critical: {crit_value}°C)" if crit_value else ""
            print(f"  {temp_name}: {temp_value}°C{crit_str}")
