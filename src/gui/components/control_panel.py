import tkinter as tk
from tkinter import ttk
import logging

class ControlPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        
        # Server status
        self.server_running = False
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Create control panel widgets"""
        # Title
        self.title_label = ttk.Label(self, text="PC to Alexa Audio Control", font=("Helvetica", 14, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Start/Stop button
        self.toggle_button = ttk.Button(
            self, 
            text="Start Streaming",
            command=self.toggle_streaming
        )
        self.toggle_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Volume control
        self.volume_label = ttk.Label(self, text="Volume:")
        self.volume_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.volume_scale = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            value=80
        )
        self.volume_scale.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Settings button
        self.settings_button = ttk.Button(
            self,
            text="Settings",
            command=self.open_settings
        )
        self.settings_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Help button
        self.help_button = ttk.Button(
            self,
            text="Help",
            command=self.show_help
        )
        self.help_button.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
    def toggle_streaming(self):
        """Toggle audio streaming on/off"""
        if self.server_running:
            self.server_running = False
            self.toggle_button.config(text="Start Streaming")
            self.logger.info("Streaming stopped by user")
            # TODO: Signal main app to stop streaming
        else:
            self.server_running = True
            self.toggle_button.config(text="Stop Streaming")
            self.logger.info("Streaming started by user")
            # TODO: Signal main app to start streaming
            
    def open_settings(self):
        """Open settings dialog"""
        # TODO: Implement settings dialog
        self.logger.info("Settings dialog requested")
        
    def show_help(self):
        """Show help information"""
        help_window = tk.Toplevel(self.parent)
        help_window.title("Help")
        help_window.geometry("400x300")
        
        help_text = """
        PC to Alexa Audio System
        
        This application allows you to use your Alexa device as a speaker for your PC.
        
        1. Make sure your Alexa device is on the same network as your PC
        2. Click "Start Streaming" to begin sending audio
        3. On your Alexa device, say "Alexa, connect to PC Audio"
        
        For more help, visit https://github.com/carloshenao/ServicesSoundAlexa
        """
        
        help_label = ttk.Label(help_window, text=help_text, wraplength=380, justify="left")
        help_label.pack(padx=10, pady=10, fill="both", expand=True)
        
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)