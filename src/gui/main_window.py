import tkinter as tk
from tkinter import ttk
import logging


try:
    from src.gui.components.control_panel import ControlPanel
    from src.gui.components.status_panel import StatusPanel
    from src.gui.styles.theme import apply_theme
except ImportError:
    # Fallback para imports relativos si es necesario
    from .components.control_panel import ControlPanel
    from .components.status_panel import StatusPanel
    from .styles.theme import apply_theme