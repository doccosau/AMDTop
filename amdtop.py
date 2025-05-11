#!/usr/bin/env python3
import time
import psutil
import numpy as np
from datetime import datetime
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Label, Tabs, Tab, Button
from textual.widget import Widget
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better performance
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from PIL import Image
import os
import argparse
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
        if not PYAMDGPU_AVAILABLE:
            self.available = False
            return
            
        try:
            # Get the first AMD GPU device
            self.gpu = pyamdgpu.get_device(0)
            self.available = True
        except Exception as e:
            print(f"Error initializing AMD GPU monitoring: {e}")
            self.available = False
    
    def get_temperature(self):
        """Get the current GPU temperature in Celsius."""
        if not self.available:
            # Return mock data if GPU not available
            return 50 + np.random.randint(0, 20)
        
        try:
            # Get temperature from the GPU sensor
            sensors = self.gpu.get_sensors()
            # Temperature is typically in millidegrees Celsius, convert to degrees
            return sensors.get('temperature', 0) / 1000.0
        except Exception as e:
            print(f"Error getting GPU temperature: {e}")
            return 0
    
    def get_usage(self):
        """Get the current GPU usage percentage."""
        if not self.available:
            # Return mock data if GPU not available
            return np.random.randint(0, 100)
        
        try:
            # Get GPU utilization
            usage = self.gpu.get_utilization()
            return usage.get('gpu', 0)
        except Exception as e:
            print(f"Error getting GPU usage: {e}")
            return 0
    
    def get_memory_usage(self):
        """Get the GPU memory usage in MB."""
        if not self.available:
            # Return mock data if GPU not available
            total = 8192  # 8GB
            used = np.random.randint(0, total)
            return used, total
        
        try:
            # Get memory info
            memory = self.gpu.get_memory_info()
            used = memory.get('used', 0) / (1024 * 1024)  # Convert to MB
            total = memory.get('total', 0) / (1024 * 1024)  # Convert to MB
            return used, total
        except Exception as e:
            print(f"Error getting GPU memory usage: {e}")
            return 0, 0

class Graph(Static):
    """A widget to display a matplotlib graph."""
    
    def __init__(self, title, data_func, color="blue", max_points=60, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data_func = data_func
        self.color = color
        self.data = []
        self.times = []
        self.max_points = max_points
    
    def update_data(self):
        """Update the graph data."""
        current_time = datetime.now()
        self.times.append(current_time)
        self.data.append(self.data_func())
        
        # Keep only the last max_points
        if len(self.data) > self.max_points:
            self.data = self.data[-self.max_points:]
            self.times = self.times[-self.max_points:]
        
        self.update_graph()
    
    def update_graph(self):
        """Generate and update the graph."""
        try:
            plt.figure(figsize=(8, 3))
            plt.plot(range(len(self.data)), self.data, color=self.color)
            plt.title(self.title)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Convert plot to image
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close('all')  # Close all figures to prevent memory leaks
            buf.seek(0)
            
            # Convert to base64 for display
            img = Image.open(buf)
            img = img.resize((img.width, img.height), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG")
            img_str = base64.b64encode(buf.getvalue()).decode()
            
            # Update the widget with the new graph
            self.update(f"[bold]{self.title}[/bold]\n\n![Graph](data:image/png;base64,{img_str})")
        except Exception as e:
            self.update(f"[bold]{self.title}[/bold]\n\nError generating graph: {e}")

class MultiLineGraph(Static):
    """A widget to display a matplotlib graph with multiple lines."""
    
    def __init__(self, title, data_funcs, labels, colors, max_points=60, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.data_funcs = data_funcs
        self.labels = labels
        self.colors = colors
        self.data_sets = [[] for _ in range(len(data_funcs))]
        self.times = []
        self.max_points = max_points
    
    def update_data(self):
        """Update the graph data."""
        current_time = datetime.now()
        self.times.append(current_time)
        
        # Get data from each function
        for i, func in enumerate(self.data_funcs):
            self.data_sets[i].append(func())
        
        # Keep only the last max_points
        if len(self.times) > self.max_points:
            self.times = self.times[-self.max_points:]
            for i in range(len(self.data_sets)):
                self.data_sets[i] = self.data_sets[i][-self.max_points:]
        
        self.update_graph()
    
    def update_graph(self):
        """Generate and update the graph."""
        try:
            plt.figure(figsize=(8, 3))
            
            # Plot each data set
            for i, data in enumerate(self.data_sets):
                plt.plot(range(len(data)), data, color=self.colors[i], label=self.labels[i])
            
            plt.title(self.title)
            plt.grid(True, alpha=0.3)
            plt.legend(loc="upper right")
            plt.tight_layout()
            
            # Convert plot to image
            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close('all')  # Close all figures to prevent memory leaks
            buf.seek(0)
            
            # Convert to base64 for display
            img = Image.open(buf)
            img = img.resize((img.width, img.height), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG")
            img_str = base64.b64encode(buf.getvalue()).decode()
            
            # Update the widget with the new graph
            self.update(f"[bold]{self.title}[/bold]\n\n![Graph](data:image/png;base64,{img_str})")
        except Exception as e:
            self.update(f"[bold]{self.title}[/bold]\n\nError generating graph: {e}")

class CPUGraph(Graph):
    """Widget to display CPU usage graph."""
    
    def __init__(self, color="green", max_points=60, **kwargs):
        super().__init__(
            title="CPU Usage (%)",
            data_func=lambda: psutil.cpu_percent(interval=0),
            color=color,
            max_points=max_points,
            **kwargs
        )

class GPUGraph(Graph):
    """Widget to display GPU temperature graph."""
    
    def __init__(self, gpu_info, color="red", max_points=60, **kwargs):
        super().__init__(
            title="GPU Temperature (°C)",
            data_func=lambda: gpu_info.get_temperature(),
            color=color,
            max_points=max_points,
            **kwargs
        )

class MemoryGraph(Graph):
    """Widget to display memory usage graph."""
    
    def __init__(self, color="blue", max_points=60, **kwargs):
        super().__init__(
            title="Memory Usage (%)",
            data_func=lambda: psutil.virtual_memory().percent,
            color=color,
            max_points=max_points,
            **kwargs
        )

class TemperatureGraph(Graph):
    """Widget to display CPU temperature graph."""
    
    def __init__(self, temp_monitor, temp_name="CPU", color="orange", max_points=60, **kwargs):
        self.temp_monitor = temp_monitor
        self.temp_name = temp_name
        
        super().__init__(
            title=f"{temp_name} Temperature (°C)",
            data_func=self._get_temperature,
            color=color,
            max_points=max_points,
            **kwargs
        )
    
    def _get_temperature(self):
        """Get the temperature for the specified component."""
        important_temps = self.temp_monitor.get_important_temperatures()
        if self.temp_name in important_temps:
            return important_temps[self.temp_name]
        return 0

class MultiTempGraph(MultiLineGraph):
    """Widget to display multiple temperature graphs."""
    
    def __init__(self, temp_monitor, max_points=60, **kwargs):
        self.temp_monitor = temp_monitor
        self.temp_names = []
        self.temp_colors = []
        
        # Initialize with empty data
        super().__init__(
            title="System Temperatures (°C)",
            data_funcs=[],
            labels=[],
            colors=[],
            max_points=max_points,
            **kwargs
        )
        
        # Update temperature sources
        self.update_temp_sources()
    
    def update_temp_sources(self):
        """Update temperature sources based on available sensors."""
        important_temps = self.temp_monitor.get_important_temperatures()
        
        # Create new data functions, labels, and colors
        self.temp_names = list(important_temps.keys())
        self.data_funcs = [self._create_temp_func(name) for name in self.temp_names]
        self.labels = self.temp_names
        
        # Assign colors based on temperature type
        self.temp_colors = []
        for name in self.temp_names:
            if 'CPU' in name:
                self.temp_colors.append('red')
            elif 'GPU' in name:
                self.temp_colors.append('green')
            elif 'Motherboard' in name:
                self.temp_colors.append('blue')
            elif 'Storage' in name or 'SSD' in name or 'NVMe' in name:
                self.temp_colors.append('purple')
            else:
                self.temp_colors.append('orange')
        
        self.colors = self.temp_colors
        
        # Reset data sets
        self.data_sets = [[] for _ in range(len(self.data_funcs))]
        self.times = []
    
    def _create_temp_func(self, temp_name):
        """Create a function to get temperature for a specific component."""
        def get_temp():
            important_temps = self.temp_monitor.get_important_temperatures()
            if temp_name in important_temps:
                return important_temps[temp_name]
            return 0
        return get_temp
    
    def update_data(self):
        """Update the graph data."""
        # Check if temperature sources have changed
        current_temps = self.temp_monitor.get_important_temperatures()
        if set(current_temps.keys()) != set(self.temp_names):
            self.update_temp_sources()
        
        # Update data as usual
        super().update_data()

class DiskIOGraph(MultiLineGraph):
    """Widget to display disk I/O graph."""
    
    def __init__(self, read_color="blue", write_color="red", max_points=60, **kwargs):
        # Initialize counters for calculating rates
        self.last_read_bytes = 0
        self.last_write_bytes = 0
        self.last_time = time.time()
        
        # Initialize with zero values
        self.read_speed = 0
        self.write_speed = 0
        
        super().__init__(
            title="Disk I/O (MB/s)",
            data_funcs=[
                lambda: self.read_speed,
                lambda: self.write_speed
            ],
            labels=["Read", "Write"],
            colors=[read_color, write_color],
            max_points=max_points,
            **kwargs
        )
    
    def update_io_speeds(self):
        """Calculate current disk I/O speeds."""
        # Get current disk I/O counters
        io_counters = psutil.disk_io_counters()
        current_time = time.time()
        
        # Skip first calculation
        if self.last_read_bytes > 0:
            # Calculate time difference
            time_diff = current_time - self.last_time
            
            # Calculate read/write speeds in MB/s
            read_bytes_diff = io_counters.read_bytes - self.last_read_bytes
            write_bytes_diff = io_counters.write_bytes - self.last_write_bytes
            
            self.read_speed = read_bytes_diff / (1024 * 1024) / time_diff
            self.write_speed = write_bytes_diff / (1024 * 1024) / time_diff
        
        # Update last values
        self.last_read_bytes = io_counters.read_bytes
        self.last_write_bytes = io_counters.write_bytes
        self.last_time = current_time

class NetworkGraph(MultiLineGraph):
    """Widget to display network traffic graph."""
    
    def __init__(self, download_color="green", upload_color="orange", max_points=60, **kwargs):
        # Initialize counters for calculating rates
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        
        # Initialize with zero values
        self.upload_speed = 0
        self.download_speed = 0
        
        super().__init__(
            title="Network Traffic (MB/s)",
            data_funcs=[
                lambda: self.download_speed,
                lambda: self.upload_speed
            ],
            labels=["Download", "Upload"],
            colors=[download_color, upload_color],
            max_points=max_points,
            **kwargs
        )
    
    def update_network_speeds(self):
        """Calculate current network speeds."""
        # Get current network counters (sum of all interfaces)
        net_counters = psutil.net_io_counters()
        current_time = time.time()
        
        # Skip first calculation
        if self.last_bytes_sent > 0:
            # Calculate time difference
            time_diff = current_time - self.last_time
            
            # Calculate upload/download speeds in MB/s
            bytes_sent_diff = net_counters.bytes_sent - self.last_bytes_sent
            bytes_recv_diff = net_counters.bytes_recv - self.last_bytes_recv
            
            self.upload_speed = bytes_sent_diff / (1024 * 1024) / time_diff
            self.download_speed = bytes_recv_diff / (1024 * 1024) / time_diff
        
        # Update last values
        self.last_bytes_sent = net_counters.bytes_sent
        self.last_bytes_recv = net_counters.bytes_recv
        self.last_time = current_time

class TopProcesses(Static):
    """Widget to display top CPU-consuming processes."""
    
    def __init__(self, process_count=10, **kwargs):
        super().__init__(**kwargs)
        self.process_count = process_count
    
    def update_processes(self):
        """Update the list of top processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_info = proc.info
                processes.append((
                    proc_info['pid'],
                    proc_info['name'],
                    proc_info['cpu_percent']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage and get top N
        processes.sort(key=lambda x: x[2], reverse=True)
        top_processes = processes[:self.process_count]
        
        # Create a table
        table = Table(title=f"Top {self.process_count} CPU Processes")
        table.add_column("PID", justify="right")
        table.add_column("Name")
        table.add_column("CPU %", justify="right")
        
        for pid, name, cpu_percent in top_processes:
            table.add_row(
                str(pid),
                name,
                f"{cpu_percent:.1f}%"
            )
        
        self.update(table)

class NetworkProcesses(Static):
    """Widget to display top network-consuming processes."""
    
    def __init__(self, network_monitor, process_count=10, **kwargs):
        super().__init__(**kwargs)
        self.network_monitor = network_monitor
        self.process_count = process_count
        self.selected_pid = None
    
    def update_processes(self):
        """Update the list of top network processes."""
        # Update network monitor
        self.network_monitor.update()
        
        # Get top processes
        top_processes = self.network_monitor.get_top_processes(self.process_count)
        
        # Create a table
        table = Table(title=f"Top {self.process_count} Network Processes")
        table.add_column("PID", justify="right")
        table.add_column("Name")
        table.add_column("Download", justify="right")
        table.add_column("Upload", justify="right")
        table.add_column("Connections", justify="right")
        
        # Format bytes to human-readable format
        def format_bytes_per_sec(bytes_per_sec):
            if bytes_per_sec < 1024:
                return f"{bytes_per_sec:.1f} B/s"
            elif bytes_per_sec < 1024 * 1024:
                return f"{bytes_per_sec / 1024:.1f} KB/s"
            else:
                return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
        
        for pid, name, download, upload in top_processes:
            # Get connection count
            conn_count = self.network_monitor.get_process_connection_count(pid)
            
            # Add row to table
            table.add_row(
                str(pid),
                name,
                format_bytes_per_sec(download),
                format_bytes_per_sec(upload),
                str(conn_count)
            )
        
        # If a process is selected, show its connection details
        if self.selected_pid is not None and self.selected_pid in [pid for pid, _, _, _ in top_processes]:
            table.add_section()
            table.add_row("", f"[bold]Connections for PID {self.selected_pid}:[/bold]", "", "", "")
            
            # Get connection details
            connections = self.network_monitor.get_process_connection_details(self.selected_pid)
            
            for i, (local_ip, local_port, remote_ip, remote_port, status) in enumerate(connections[:5]):
                table.add_row(
                    "",
                    f"{local_ip}:{local_port}",
                    "→",
                    f"{remote_ip}:{remote_port}",
                    status
                )
            
            # If there are more connections, indicate this
            if len(connections) > 5:
                table.add_row("", f"...and {len(connections) - 5} more connections", "", "", "")
        
        self.update(table)
    
    def select_process(self, pid):
        """Select a process to show its connection details."""
        self.selected_pid = pid
        self.update_processes()

class GPUMetrics(Static):
    """Widget to display GPU metrics."""
    
    def __init__(self, gpu_info, **kwargs):
        super().__init__(**kwargs)
        self.gpu_info = gpu_info
    
    def update_metrics(self):
        """Update GPU metrics."""
        temperature = self.gpu_info.get_temperature()
        usage = self.gpu_info.get_usage()
        memory_used, memory_total = self.gpu_info.get_memory_usage()
        
        # Check if GPU is available
        if not self.gpu_info.available and not PYAMDGPU_AVAILABLE:
            self.update(Text.from_markup("[bold]GPU Metrics[/bold]\n\nUsing mock GPU data (pyamdgpu not installed)"))
            return
        elif not self.gpu_info.available:
            self.update(Text.from_markup("[bold]GPU Metrics[/bold]\n\nNo AMD GPU detected or pyamdgpu error"))
            return
        
        # Set colors based on values
        temp_color = "green"
        if temperature > 80:
            temp_color = "red"
        elif temperature > 70:
            temp_color = "yellow"
        
        usage_color = "green"
        if usage > 80:
            usage_color = "red"
        elif usage > 60:
            usage_color = "yellow"
        
        memory_color = "green"
        if memory_total > 0:
            memory_percent = (memory_used / memory_total) * 100
            if memory_percent > 80:
                memory_color = "red"
            elif memory_percent > 60:
                memory_color = "yellow"
        
        # Format memory values
        if memory_total > 0:
            memory_text = f"Memory: [{memory_color}]{memory_used:.0f}MB / {memory_total:.0f}MB ({(memory_used / memory_total) * 100:.1f}%)[/{memory_color}]"
        else:
            memory_text = "Memory: Not available"
        
        content = Text.from_markup(f"""[bold]GPU Metrics[/bold]

Temperature: [{temp_color}]{temperature:.1f}°C[/{temp_color}]
Usage: [{usage_color}]{usage:.1f}%[/{usage_color}]
{memory_text}
""")
        
        self.update(content)

class MemoryMetrics(Static):
    """Widget to display memory metrics."""
    
    def update_metrics(self):
        """Update memory metrics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Set colors based on memory usage
        mem_color = "green"
        if mem.percent > 80:
            mem_color = "red"
        elif mem.percent > 60:
            mem_color = "yellow"
        
        swap_color = "green"
        if swap.percent > 80:
            swap_color = "red"
        elif swap.percent > 60:
            swap_color = "yellow"
        
        # Format bytes to human-readable format
        def format_bytes(bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes < 1024 or unit == 'TB':
                    return f"{bytes:.2f} {unit}"
                bytes /= 1024
        
        content = Text.from_markup(f"""[bold]Memory Metrics[/bold]

RAM: [{mem_color}]{mem.percent}% used[/{mem_color}]
Total: {format_bytes(mem.total)}
Used: {format_bytes(mem.used)}
Available: {format_bytes(mem.available)}

Swap: [{swap_color}]{swap.percent}% used[/{swap_color}]
Total: {format_bytes(swap.total)}
Used: {format_bytes(swap.used)}
""")
        
        self.update(content)

class TemperatureMetrics(Static):
    """Widget to display temperature metrics."""
    
    def __init__(self, temp_monitor, **kwargs):
        super().__init__(**kwargs)
        self.temp_monitor = temp_monitor
    
    def update_metrics(self):
        """Update temperature metrics."""
        if not self.temp_monitor.sensors_available:
            self.update(Text.from_markup("[bold]Temperature Metrics[/bold]\n\nlm-sensors not available. Please install it to use temperature monitoring."))
            return
        
        # Get all temperature data
        all_temps = self.temp_monitor.get_all_temperatures()
        
        content = Text.from_markup("[bold]Temperature Metrics[/bold]\n\n")
        
        # Add important temperatures first
        important_temps = self.temp_monitor.get_important_temperatures()
        if important_temps:
            content.append(Text.from_markup("[bold]Important Temperatures:[/bold]\n"))
            
            for name, temp in important_temps.items():
                # Set color based on temperature
                color = "green"
                if temp > 80:
                    color = "red"
                elif temp > 70:
                    color = "yellow"
                
                content.append(Text.from_markup(f"{name}: [{color}]{temp:.1f}°C[/{color}]\n"))
            
            content.append(Text.from_markup("\n"))
        
        # Add all temperatures (limit to save space)
        content.append(Text.from_markup("[bold]All Sensors:[/bold]\n"))
        
        sensor_count = 0
        for sensor_name, temps in all_temps.items():
            # Limit to 3 sensors to save space
            if sensor_count >= 3:
                content.append(Text.from_markup(f"...and {len(all_temps) - 3} more sensors\n"))
                break
            
            content.append(Text.from_markup(f"[bold]{sensor_name}:[/bold]\n"))
            
            temp_count = 0
            for temp_name, (temp_value, crit_value) in temps.items():
                # Limit to 3 temperatures per sensor to save space
                if temp_count >= 3:
                    content.append(Text.from_markup(f"  ...and {len(temps) - 3} more temperatures\n"))
                    break
                
                # Set color based on temperature and critical value
                color = "green"
                if crit_value and temp_value > crit_value * 0.9:
                    color = "red"
                elif crit_value and temp_value > crit_value * 0.8:
                    color = "yellow"
                elif temp_value > 80:
                    color = "red"
                elif temp_value > 70:
                    color = "yellow"
                
                # Add critical value if available
                crit_str = f" (Critical: {crit_value}°C)" if crit_value else ""
                
                content.append(Text.from_markup(f"  {temp_name}: [{color}]{temp_value:.1f}°C[/{color}]{crit_str}\n"))
                temp_count += 1
            
            sensor_count += 1
        
        self.update(content)

class DiskMetrics(Static):
    """Widget to display disk metrics."""
    
    def __init__(self, partition_count=3, **kwargs):
        super().__init__(**kwargs)
        self.partition_count = partition_count
    
    def update_metrics(self):
        """Update disk metrics."""
        # Get disk partitions
        partitions = psutil.disk_partitions()
        
        # Get disk I/O counters
        io_counters = psutil.disk_io_counters()
        
        # Format bytes to human-readable format
        def format_bytes(bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes < 1024 or unit == 'TB':
                    return f"{bytes:.2f} {unit}"
                bytes /= 1024
        
        content = Text.from_markup("[bold]Disk Metrics[/bold]\n\n")
        
        # Add I/O statistics
        content.append(Text.from_markup(f"Total Read: {format_bytes(io_counters.read_bytes)}\n"))
        content.append(Text.from_markup(f"Total Write: {format_bytes(io_counters.write_bytes)}\n"))
        content.append(Text.from_markup(f"Read Count: {io_counters.read_count}\n"))
        content.append(Text.from_markup(f"Write Count: {io_counters.write_count}\n\n"))
        
        # Add partition information (limit to partition_count partitions)
        content.append(Text.from_markup("[bold]Partitions:[/bold]\n"))
        for i, partition in enumerate(partitions[:self.partition_count]):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                usage_percent = usage.percent
                
                # Set color based on usage
                color = "green"
                if usage_percent > 80:
                    color = "red"
                elif usage_percent > 60:
                    color = "yellow"
                
                content.append(Text.from_markup(
                    f"{partition.device} ({partition.mountpoint}): [{color}]{usage_percent}% used[/{color}]\n"
                    f"  {format_bytes(usage.used)} / {format_bytes(usage.total)}\n"
                ))
            except (PermissionError, FileNotFoundError):
                content.append(Text.from_markup(f"{partition.device}: Access denied\n"))
        
        # If there are more partitions, indicate this
        if len(partitions) > self.partition_count:
            content.append(Text.from_markup(f"\n...and {len(partitions) - self.partition_count} more partitions\n"))
        
        self.update(content)

class NetworkMetrics(Static):
    """Widget to display network metrics."""
    
    def __init__(self, interface_count=3, **kwargs):
        super().__init__(**kwargs)
        self.interface_count = interface_count
    
    def update_metrics(self):
        """Update network metrics."""
        # Get network I/O counters (overall)
        net_io = psutil.net_io_counters()
        
        # Get network I/O counters per interface
        net_io_per_nic = psutil.net_io_counters(pernic=True)
        
        # Format bytes to human-readable format
        def format_bytes(bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes < 1024 or unit == 'TB':
                    return f"{bytes:.2f} {unit}"
                bytes /= 1024
        
        content = Text.from_markup("[bold]Network Metrics[/bold]\n\n")
        
        # Add overall statistics
        content.append(Text.from_markup("[bold]Overall Traffic:[/bold]\n"))
        content.append(Text.from_markup(f"Total Sent: {format_bytes(net_io.bytes_sent)}\n"))
        content.append(Text.from_markup(f"Total Received: {format_bytes(net_io.bytes_recv)}\n"))
        content.append(Text.from_markup(f"Packets Sent: {net_io.packets_sent}\n"))
        content.append(Text.from_markup(f"Packets Received: {net_io.packets_recv}\n"))
        content.append(Text.from_markup(f"Errors In: {net_io.errin}\n"))
        content.append(Text.from_markup(f"Errors Out: {net_io.errout}\n"))
        content.append(Text.from_markup(f"Dropped In: {net_io.dropin}\n"))
        content.append(Text.from_markup(f"Dropped Out: {net_io.dropout}\n\n"))
        
        # Add per-interface statistics (limit to active interfaces)
        content.append(Text.from_markup("[bold]Network Interfaces:[/bold]\n"))
        
        # Get network addresses
        net_addrs = psutil.net_if_addrs()
        
        # Filter out loopback and inactive interfaces
        active_interfaces = []
        for nic, stats in net_io_per_nic.items():
            # Skip loopback interface
            if nic == 'lo' or nic.startswith('loop'):
                continue
            
            # Check if interface has sent or received any data
            if stats.bytes_sent > 0 or stats.bytes_recv > 0:
                active_interfaces.append((nic, stats))
        
        # Sort by total traffic (sent + received)
        active_interfaces.sort(key=lambda x: x[1].bytes_sent + x[1].bytes_recv, reverse=True)
        
        # Display active interfaces (limit to interface_count)
        for nic, stats in active_interfaces[:self.interface_count]:
            content.append(Text.from_markup(f"[bold]{nic}:[/bold]\n"))
            
            # Add IP addresses if available
            if nic in net_addrs:
                for addr in net_addrs[nic]:
                    if addr.family == 2:  # AF_INET (IPv4)
                        content.append(Text.from_markup(f"  IPv4: {addr.address}\n"))
                    elif addr.family == 23:  # AF_INET6 (IPv6)
                        content.append(Text.from_markup(f"  IPv6: {addr.address}\n"))
            
            # Add traffic stats
            content.append(Text.from_markup(f"  Sent: {format_bytes(stats.bytes_sent)}\n"))
            content.append(Text.from_markup(f"  Received: {format_bytes(stats.bytes_recv)}\n"))
        
        # If there are more interfaces, indicate this
        if len(active_interfaces) > self.interface_count:
            content.append(Text.from_markup(f"\n...and {len(active_interfaces) - self.interface_count} more interfaces\n"))
        
        self.update(content)

class ThemeToggleButton(Button):
    """Button to toggle between dark and light themes."""
    
    def __init__(self, theme_manager, **kwargs):
        super().__init__(classes="theme-toggle", **kwargs)
        self.theme_manager = theme_manager
        self._update_label()
    
    def _update_label(self):
        """Update the button label based on the current theme."""
        current_theme = self.theme_manager.get_current_theme()
        if current_theme == "dark":
            self.label = "🌞 Light"  # Switch to light theme
        else:
            self.label = "🌙 Dark"  # Switch to dark theme
    
    def on_button_pressed(self):
        """Handle button press event."""
        # Toggle theme
        self.theme_manager.toggle_theme()
        
        # Update button label
        self._update_label()
        
        # Update app CSS
        self.app.refresh_css()
        
        # Save configuration
        save_config(self.app.config, "./config.yaml")

class AMDTopApp(App):
    """Main application class."""
    
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or load_config()
        self.gpu_info = GPUInfo()
        self.disk_io_graph = None
        self.network_graph = None
        self.network_monitor = NetworkProcessMonitor()
        self.temp_monitor = TemperatureMonitor()
        self.theme_manager = ThemeManager(self.config)
        
        # Generate CSS from theme
        self.CSS = self.theme_manager.generate_css()
    
    def refresh_css(self):
        """Refresh the CSS based on the current theme."""
        self.CSS = self.theme_manager.generate_css()
        self.app.refresh()
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Get configuration values
        colors = self.config["colors"]
        display = self.config["display"]
        
        # Create header with theme toggle button
        header = Header(show_clock=True)
        yield header
        yield ThemeToggleButton(self.theme_manager)
        
        with Container(classes="container"):
            # Tabs for different graph sets
            yield Tabs(
                Tab("System", id="tab_system"),
                Tab("Disk I/O", id="tab_disk"),
                Tab("Network", id="tab_network"),
                Tab("Temperature", id="tab_temperature"),
                id="tabs"
            )
            
            # System monitoring tab content
            with Container(id="tab_content_system"):
                with Horizontal():
                    yield CPUGraph(
                        color=colors["cpu_graph"],
                        max_points=display["graph_history"],
                        classes="graph",
                        id="cpu_graph"
                    )
                    yield GPUGraph(
                        self.gpu_info,
                        color=colors["gpu_graph"],
                        max_points=display["graph_history"],
                        classes="graph",
                        id="gpu_graph"
                    )
                    yield MemoryGraph(
                        color=colors["memory_graph"],
                        max_points=display["graph_history"],
                        classes="graph",
                        id="memory_graph"
                    )
                
                with Horizontal():
                    yield TopProcesses(
                        process_count=display["process_count"],
                        classes="processes",
                        id="top_processes"
                    )
                    with Vertical():
                        yield GPUMetrics(self.gpu_info, classes="metrics", id="gpu_metrics")
                        yield MemoryMetrics(classes="metrics", id="memory_metrics")
            
            # Disk I/O tab content
            with Container(id="tab_content_disk", classes="container"):
                with Horizontal():
                    self.disk_io_graph = DiskIOGraph(
                        read_color=colors["disk_read"],
                        write_color=colors["disk_write"],
                        max_points=display["graph_history"],
                        classes="graph",
                        id="disk_io_graph"
                    )
                    yield self.disk_io_graph
                
                with Horizontal():
                    yield DiskMetrics(
                        partition_count=display["partition_count"],
                        classes="processes",
                        id="disk_metrics"
                    )
            
            # Network tab content
            with Container(id="tab_content_network", classes="container"):
                with Horizontal():
                    self.network_graph = NetworkGraph(
                        download_color=colors["network_download"],
                        upload_color=colors["network_upload"],
                        max_points=display["graph_history"],
                        classes="graph",
                        id="network_graph"
                    )
                    yield self.network_graph
                
                with Horizontal():
                    yield NetworkProcesses(
                        self.network_monitor,
                        process_count=display["process_count"],
                        classes="processes",
                        id="network_processes"
                    )
                    yield NetworkMetrics(
                        interface_count=display["interface_count"],
                        classes="metrics",
                        id="network_metrics"
                    )
            
            # Temperature tab content
            with Container(id="tab_content_temperature", classes="container"):
                with Horizontal():
                    yield MultiTempGraph(
                        self.temp_monitor,
                        max_points=display["graph_history"],
                        classes="graph",
                        id="temp_graph"
                    )
                
                with Horizontal():
                    yield TemperatureMetrics(
                        self.temp_monitor,
                        classes="processes",
                        id="temp_metrics"
                    )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when the app is mounted."""
        # Set default tab based on configuration
        default_tab = self.config["default_tab"]
        
        # Hide all tab contents initially
        self.query_one("#tab_content_system").display = False
        self.query_one("#tab_content_disk").display = False
        self.query_one("#tab_content_network").display = False
        self.query_one("#tab_content_temperature").display = False
        
        # Show the default tab content
        if default_tab == "system":
            self.query_one("#tab_content_system").display = True
            self.query_one("#tabs").active = "tab_system"
        elif default_tab == "disk":
            self.query_one("#tab_content_disk").display = True
            self.query_one("#tabs").active = "tab_disk"
        elif default_tab == "network":
            self.query_one("#tab_content_network").display = True
            self.query_one("#tabs").active = "tab_network"
        elif default_tab == "temperature":
            self.query_one("#tab_content_temperature").display = True
            self.query_one("#tabs").active = "tab_temperature"
        
        # Set up update timer based on configuration
        intervals = self.config["intervals"]
        self.update_timer = self.set_interval(intervals["graphs"], self.update_widgets)
    
    def update_widgets(self) -> None:
        """Update all widgets with new data."""
        # Update system tab widgets
        self.query_one("#cpu_graph", CPUGraph).update_data()
        self.query_one("#gpu_graph", GPUGraph).update_data()
        self.query_one("#memory_graph", MemoryGraph).update_data()
        
        # Update processes less frequently if configured differently
        if not hasattr(self, "process_update_counter"):
            self.process_update_counter = 0
        
        self.process_update_counter += 1
        process_update_interval = int(self.config["intervals"]["processes"] / self.config["intervals"]["graphs"])
        if process_update_interval < 1:
            process_update_interval = 1
        
        if self.process_update_counter >= process_update_interval:
            self.query_one("#top_processes", TopProcesses).update_processes()
            self.query_one("#gpu_metrics", GPUMetrics).update_metrics()
            self.query_one("#memory_metrics", MemoryMetrics).update_metrics()
            self.process_update_counter = 0
        
        # Update disk tab widgets
        self.disk_io_graph.update_io_speeds()
        self.disk_io_graph.update_data()
        self.query_one("#disk_metrics", DiskMetrics).update_metrics()
        
        # Update network tab widgets
        self.network_graph.update_network_speeds()
        self.network_graph.update_data()
        self.query_one("#network_processes", NetworkProcesses).update_processes()
        self.query_one("#network_metrics", NetworkMetrics).update_metrics()
        
        # Update temperature tab widgets
        self.temp_monitor.update()
        self.query_one("#temp_graph", MultiTempGraph).update_data()
        self.query_one("#temp_metrics", TemperatureMetrics).update_metrics()
    
    def on_key(self, event):
        """Handle key press events."""
        # Tab switching shortcuts
        if event.key == "1":
            self.query_one("#tabs").active = "tab_system"
            self.on_tabs_tab_activated(self.query_one("#tabs"))
        elif event.key == "2":
            self.query_one("#tabs").active = "tab_disk"
            self.on_tabs_tab_activated(self.query_one("#tabs"))
        elif event.key == "3":
            self.query_one("#tabs").active = "tab_network"
            self.on_tabs_tab_activated(self.query_one("#tabs"))
        elif event.key == "4":
            self.query_one("#tabs").active = "tab_temperature"
            self.on_tabs_tab_activated(self.query_one("#tabs"))
        # Theme toggle shortcut
        elif event.key == "t":
            self.query_one(ThemeToggleButton).on_button_pressed()
        # Quit shortcut
        elif event.key == "q":
            self.exit()
    
    def on_tabs_tab_activated(self, event):
        """Handle tab switching."""
        # Get the active tab ID
        if hasattr(event, "tab"):
            tab_id = event.tab.id
        else:
            tab_id = event.active
        
        # Hide all tab contents
        self.query_one("#tab_content_system").display = False
        self.query_one("#tab_content_disk").display = False
        self.query_one("#tab_content_network").display = False
        self.query_one("#tab_content_temperature").display = False
        
        # Show selected tab content
        if tab_id == "tab_system":
            self.query_one("#tab_content_system").display = True
        elif tab_id == "tab_disk":
            self.query_one("#tab_content_disk").display = True
        elif tab_id == "tab_network":
            self.query_one("#tab_content_network").display = True
        elif tab_id == "tab_temperature":
            self.query_one("#tab_content_temperature").display = True

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AMDTop - AMD CPU/GPU monitoring tool")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    args = parser.parse_args()
    
    # Create default configuration if requested
    if args.create_config:
        create_default_config()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Run the application
    app = AMDTopApp(config=config)
    app.run()

if __name__ == "__main__":
    main()
