import tkinter as tk
from tkinter import ttk
import logging
import threading
import time

class StatusPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # State variables
        self.server_status = "Stopped"
        self.connected_devices = []
        self.audio_level = 0
        
        # Create widgets
        self.create_widgets()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_audio_level, daemon=True)
        self.update_thread.start()
        
    def create_widgets(self):
        """Create status panel widgets"""
        # Status frame
        status_frame = ttk.LabelFrame(self, text="System Status")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Server status
        self.server_status_label = ttk.Label(status_frame, text="Server Status:")
        self.server_status_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.server_status_value = ttk.Label(status_frame, text=self.server_status)
        self.server_status_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Connected devices
        self.connected_label = ttk.Label(status_frame, text="Connected Devices:")
        self.connected_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.connected_value = ttk.Label(status_frame, text="None")
        self.connected_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Audio level
        self.audio_level_label = ttk.Label(status_frame, text="Audio Level:")
        self.audio_level_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        self.audio_level_bar = ttk.Progressbar(
            status_frame,
            orient="horizontal",
            length=200,
            mode="determinate"
        )
        self.audio_level_bar.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # IP address
        self.ip_label = ttk.Label(status_frame, text="Server IP:")
        self.ip_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        
        self.ip_value = ttk.Label(status_frame, text="Detecting...")
        self.ip_value.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
    def update_server_status(self, status):
        """Update the server status display"""
        self.server_status = status
        self.server_status_value.config(text=status)
        
        # Change color based on status
        if status == "Running":
            self.server_status_value.config(foreground="green")
        else:
            self.server_status_value.config(foreground="red")
            
    def update_connected_devices(self, devices):
        """Update the connected devices display"""
        if not devices:
            self.connected_value.config(text="None")
        else:
            self.connected_value.config(text=", ".join(devices))
            
    def update_ip_address(self, ip):
        """Update the IP address display"""
        self.ip_value.config(text=ip)
        
    def update_audio_level(self):
        """Update the audio level display in a separate thread"""
        while True:
            # This would normally get the actual audio level
            # For demonstration, we'll use a simulated value
            self.audio_level = (self.audio_level + 10) % 100
            
            # Update UI in thread-safe manner
            self.after(10, lambda: self.audio_level_bar.config(value=self.audio_level))
            
            # Sleep to prevent CPU overuse
            time.sleep(0.1)