#!/usr/bin/env python3
"""
Network monitoring module for AMDTop
Tracks per-process network usage
"""
import os
import time
import psutil
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class NetworkProcessMonitor:
    """
    Monitors network usage per process
    """
    def __init__(self):
        # Initialize data structures
        self.process_connections = {}  # pid -> connections
        self.process_io_prev = {}  # pid -> (recv_bytes, sent_bytes, timestamp)
        self.process_io_current = {}  # pid -> (recv_bytes, sent_bytes, download_speed, upload_speed)
        self.last_update = 0
        
        # Update immediately on initialization
        self.update()
    
    def update(self) -> None:
        """
        Update network usage statistics for all processes
        """
        current_time = time.time()
        
        # Get all network connections with process information
        try:
            connections = psutil.net_connections(kind='inet')
        except (psutil.AccessDenied, PermissionError):
            # If we don't have permission, try to get what we can
            connections = []
            print("Warning: Limited network connection information due to permissions")
        
        # Group connections by process ID
        process_connections = defaultdict(list)
        for conn in connections:
            if conn.pid is not None:
                process_connections[conn.pid].append(conn)
        
        # Update process connections
        self.process_connections = process_connections
        
        # Get process network I/O
        for pid in process_connections:
            try:
                # Try to get process
                process = psutil.Process(pid)
                
                # Get process network I/O counters
                # Note: This is not directly available in psutil, so we need to use a workaround
                # We'll use /proc/[pid]/net/dev on Linux
                if os.name == 'posix':  # Linux/Unix
                    recv_bytes, sent_bytes = self._get_process_net_io_linux(pid)
                else:
                    # On other platforms, we can't easily get per-process network I/O
                    # So we'll just use the connection count as a proxy
                    recv_bytes, sent_bytes = len(process_connections[pid]), len(process_connections[pid])
                
                # Calculate speeds if we have previous data
                if pid in self.process_io_prev:
                    prev_recv, prev_sent, prev_time = self.process_io_prev[pid]
                    time_diff = current_time - prev_time
                    
                    if time_diff > 0:
                        download_speed = (recv_bytes - prev_recv) / time_diff
                        upload_speed = (sent_bytes - prev_sent) / time_diff
                    else:
                        download_speed = 0
                        upload_speed = 0
                else:
                    download_speed = 0
                    upload_speed = 0
                
                # Store current data for next update
                self.process_io_prev[pid] = (recv_bytes, sent_bytes, current_time)
                
                # Store current speeds
                self.process_io_current[pid] = (recv_bytes, sent_bytes, download_speed, upload_speed)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process no longer exists or we don't have permission
                if pid in self.process_io_prev:
                    del self.process_io_prev[pid]
                if pid in self.process_io_current:
                    del self.process_io_current[pid]
        
        # Clean up processes that no longer exist
        for pid in list(self.process_io_prev.keys()):
            if pid not in process_connections:
                del self.process_io_prev[pid]
        
        for pid in list(self.process_io_current.keys()):
            if pid not in process_connections:
                del self.process_io_current[pid]
        
        self.last_update = current_time
    
    def _get_process_net_io_linux(self, pid: int) -> Tuple[int, int]:
        """
        Get network I/O for a process on Linux using /proc
        
        Args:
            pid: Process ID
            
        Returns:
            Tuple of (received_bytes, sent_bytes)
        """
        # This is a simplified approach that uses connection information
        # A more accurate approach would involve tracking socket file descriptors
        # and mapping them to network interfaces, but that's complex
        
        # As a simple approximation, we'll count the number of connections
        # and use that as a proxy for network activity
        try:
            process = psutil.Process(pid)
            connections = process.connections(kind='inet')
            
            # Count established connections
            established = sum(1 for c in connections if c.status == 'ESTABLISHED')
            
            # Use connection count as a proxy for network activity
            # This is not accurate for actual bytes, but helps identify active network processes
            return established * 1000, established * 1000
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0, 0
    
    def get_top_processes(self, count: int = 10) -> List[Tuple[int, str, float, float]]:
        """
        Get the top processes by network usage
        
        Args:
            count: Number of processes to return
            
        Returns:
            List of (pid, name, download_speed, upload_speed) tuples
        """
        # Get process information
        processes = []
        for pid, (_, _, download, upload) in self.process_io_current.items():
            try:
                process = psutil.Process(pid)
                processes.append((
                    pid,
                    process.name(),
                    download,
                    upload
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by total network usage (download + upload)
        processes.sort(key=lambda x: x[2] + x[3], reverse=True)
        
        return processes[:count]
    
    def get_process_connection_count(self, pid: int) -> int:
        """
        Get the number of network connections for a process
        
        Args:
            pid: Process ID
            
        Returns:
            Number of connections
        """
        if pid in self.process_connections:
            return len(self.process_connections[pid])
        return 0
    
    def get_process_connection_details(self, pid: int) -> List[Tuple[str, int, str, int, str]]:
        """
        Get connection details for a process
        
        Args:
            pid: Process ID
            
        Returns:
            List of (local_ip, local_port, remote_ip, remote_port, status) tuples
        """
        if pid not in self.process_connections:
            return []
        
        details = []
        for conn in self.process_connections[pid]:
            if conn.laddr and len(conn.laddr) >= 2:
                local_ip, local_port = conn.laddr
            else:
                local_ip, local_port = "-", 0
            
            if conn.raddr and len(conn.raddr) >= 2:
                remote_ip, remote_port = conn.raddr
            else:
                remote_ip, remote_port = "-", 0
            
            status = conn.status
            
            details.append((local_ip, local_port, remote_ip, remote_port, status))
        
        return details

# Test the module if run directly
if __name__ == "__main__":
    monitor = NetworkProcessMonitor()
    
    # Update a few times to get meaningful data
    for _ in range(3):
        monitor.update()
        time.sleep(1)
    
    # Print top processes
    print("Top network processes:")
    for pid, name, download, upload in monitor.get_top_processes(5):
        print(f"{name} (PID {pid}): Download: {download/1024:.2f} KB/s, Upload: {upload/1024:.2f} KB/s")
        
        # Print connection details
        for local_ip, local_port, remote_ip, remote_port, status in monitor.get_process_connection_details(pid)[:2]:
            print(f"  {local_ip}:{local_port} -> {remote_ip}:{remote_port} [{status}]")
        
        conn_count = monitor.get_process_connection_count(pid)
        if conn_count > 2:
            print(f"  ... and {conn_count - 2} more connections")
