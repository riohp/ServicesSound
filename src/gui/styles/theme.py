import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    """Apply a modern theme to the application"""
    # Configure the style
    style = ttk.Style(root)
    
    # Try to use a more modern theme if available
    try:
        style.theme_use("clam")  # 'clam' is a built-in theme that looks better than default
    except tk.TclError:
        # Fall back to default if 'clam' is not available
        pass
    
    # Configure colors
    bg_color = "#f0f0f0"
    accent_color = "#3498db"
    text_color = "#333333"
    
    # Configure ttk styles
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground=text_color)
    style.configure("TButton", 
                   background=accent_color, 
                   foreground="white", 
                   padding=5, 
                   relief="flat")
    
    style.map("TButton",
              background=[("active", "#2980b9"), ("pressed", "#1f618d")],
              foreground=[("active", "white"), ("pressed", "white")])
    
    style.configure("TProgressbar", 
                   background=accent_color,
                   troughcolor=bg_color,
                   borderwidth=0)
    
    style.configure("TScale", 
                   background=bg_color, 
                   troughcolor="#d1d1d1", 
                   sliderlength=15)
    
    style.configure("TLabelframe", 
                   background=bg_color, 
                   foreground=text_color,
                   borderwidth=1, 
                   relief="solid")
    
    style.configure("TLabelframe.Label", 
                   background=bg_color, 
                   foreground=text_color)
    
    # Configure root window
    root.configure(background=bg_color)
    root.option_add("*Font", "Helvetica 10")
    
    # Set window icon (if available)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass  # No icon available