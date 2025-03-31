import tkinter as tk
from tkinter import ttk
from .components.control_panel import ControlPanel
from .components.status_panel import StatusPanel
from .styles.theme import apply_theme

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PC to Alexa Audio System")
        
        # tema
        apply_theme(self.root)
        
        # Componentes
        self.control_panel = ControlPanel(self.root)
        self.status_panel = StatusPanel(self.root)
        
        self.setup_layout()
        
    def setup_layout(self):
        self.control_panel.pack(pady=10)
        self.status_panel.pack(pady=10)
        
    def run(self):
        self.root.mainloop()
