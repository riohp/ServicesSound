import logging

import customtkinter as ctk

from .components.control_panel import ControlPanel
from .components.status_panel import StatusPanel
from .styles.theme import apply_theme

logger = logging.getLogger(__name__)

_WINDOW_W = 820
_WINDOW_H = 540


class MainWindow:
    """Root application window."""

    def __init__(self, audio_server=None, settings=None, tunnel_manager=None) -> None:
        self.audio_server = audio_server
        self.settings = settings
        self.tunnel_manager = tunnel_manager

        theme = "dark"
        if settings:
            stored = settings.get("gui", "theme")
            if stored in ("dark", "light", "system"):
                theme = stored

        apply_theme(theme)

        self.root = ctk.CTk()
        self._setup_window()
        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        logger.info("MainWindow initialized")

    def _setup_window(self) -> None:
        self.root.title("ServicesSound - Alexa Audio Streamer")
        self.root.minsize(750, 480)
        self._center_window()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _center_window(self) -> None:
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - _WINDOW_W) // 2
        y = (sh - _WINDOW_H) // 2
        self.root.geometry(f"{_WINDOW_W}x{_WINDOW_H}+{x}+{y}")

    def _build_layout(self) -> None:
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.control_panel = ControlPanel(
            container,
            audio_server=self.audio_server,
            settings=self.settings,
            tunnel_manager=self.tunnel_manager,
        )
        self.control_panel.grid(row=0, column=0, sticky="ns", padx=(0, 12))

        self.status_panel = StatusPanel(
            container,
            audio_server=self.audio_server,
            tunnel_manager=self.tunnel_manager,
        )
        self.status_panel.grid(row=0, column=1, sticky="nsew")

    def _on_closing(self) -> None:
        logger.info("Application closing")
        if self.audio_server and self.audio_server.is_running:
            self.audio_server.stop()
        if self.tunnel_manager and self.tunnel_manager.is_active:
            self.tunnel_manager.stop_tunnel()
        self.root.destroy()

    def run(self) -> None:
        logger.info("Starting GUI mainloop")
        self.root.mainloop()
        logger.info("GUI closed")
