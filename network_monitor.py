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
    """Monitors network usage per process"""
    def __init__(self):
        """Initialize network monitor"""
        self.process_stats: Dict[int, Dict] = {}
        self.previous_stats: Dict[int, Tuple[float, float, float]] = {}
        self.update_interval = 1.0  # seconds
        self.last_update = 0.0

    def update(self) -> None:
        """Update network statistics for all processes"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return

        # Clear old process stats
        self.process_stats.clear()
        
        # Get all network connections
        try:
            connections = psutil.net_connections(kind='inet')
        except psutil.AccessDenied:
            print("Warning: Need root privileges for full network monitoring")
            return

        # Group connections by PID
        for conn in connections:
            if not conn.pid:
                continue

            if conn.pid not in self.process_stats:
                try:
                    proc = psutil.Process(conn.pid)
                    self.process_stats[conn.pid] = {
                        'name': proc.name(),
                        'connections': [],
                        'bytes_sent': 0,
                        'bytes_recv': 0,
                        'connection_count': 0
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Add connection details
            self.process_stats[conn.pid]['connections'].append({
                'local_addr': conn.laddr,
                'remote_addr': conn.raddr if conn.raddr else None,
                'status': conn.status,
                'type': conn.type
            })
            self.process_stats[conn.pid]['connection_count'] += 1

        # Update IO statistics
        for pid in list(self.process_stats.keys()):
            try:
                proc = psutil.Process(pid)
                io_counters = proc.io_counters()
                bytes_sent = io_counters.write_bytes
                bytes_recv = io_counters.read_bytes
                
                # Calculate rates if we have previous data
                if pid in self.previous_stats:
                    prev_sent, prev_recv, prev_time = self.previous_stats[pid]
                    time_diff = current_time - prev_time
                    
                    if time_diff > 0:
                        send_rate = (bytes_sent - prev_sent) / time_diff
                        recv_rate = (bytes_recv - prev_recv) / time_diff
                        
                        self.process_stats[pid].update({
                            'bytes_sent_per_sec': send_rate,
                            'bytes_recv_per_sec': recv_rate
                        })

                # Store current values for next update
                self.previous_stats[pid] = (bytes_sent, bytes_recv, current_time)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.process_stats.pop(pid, None)
                self.previous_stats.pop(pid, None)

        self.last_update = current_time

    def get_top_processes(self, count: int = 10) -> List[Tuple[int, str, float, float]]:
        """Get top processes by network usage"""
        results = []
        for pid, stats in self.process_stats.items():
            if 'bytes_sent_per_sec' in stats:
                results.append((
                    pid,
                    stats['name'],
                    stats.get('bytes_sent_per_sec', 0),
                    stats.get('bytes_recv_per_sec', 0)
                ))
        
        # Sort by total bandwidth (send + receive)
        results.sort(key=lambda x: x[2] + x[3], reverse=True)
        return results[:count]

    def get_process_connection_count(self, pid: int) -> int:
        """Get number of connections for a process"""
        return self.process_stats.get(pid, {}).get('connection_count', 0)

    def get_process_connection_details(self, pid: int) -> List[Dict]:
        """Get detailed connection information for a process"""
        return self.process_stats.get(pid, {}).get('connections', [])

    def format_bytes(self, bytes: float) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"

    def print_network_usage(self) -> None:
        """Print current network usage (for debugging)"""
        print("\nNetwork Usage by Process:")
        print("-" * 80)
        print(f"{'PID':>7} {'Process':20} {'Send Rate':>15} {'Receive Rate':>15} {'Connections':>10}")
        print("-" * 80)
        
        for pid, name, sent, recv in self.get_top_processes():
            print(f"{pid:7d} {name:20} {self.format_bytes(sent):>15} "
                  f"{self.format_bytes(recv):>15} {self.get_process_connection_count(pid):>10d}")

# Test the module if run directly
if __name__ == "__main__":
    monitor = NetworkProcessMonitor()
    
    print("Testing network monitor...")
    print("(Note: Some features require root privileges)")
    
    # Monitor for a few seconds
    for _ in range(3):
        monitor.update()
        monitor.print_network_usage()
        time.sleep(1)
