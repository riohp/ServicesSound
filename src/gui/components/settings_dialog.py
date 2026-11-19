import logging

import customtkinter as ctk
from tkinter import messagebox

logger = logging.getLogger(__name__)

_MUTED = ("gray50", "#8b9ab2")
_CARD_BG = ("gray88", "#1e2433")
_BTN_SEC = ("gray75", "#2d3748")
_BTN_SEC_HOVER = ("gray65", "#374151")
_BTN_SEC_TEXT = ("gray10", "gray90")


class SettingsDialog(ctk.CTkToplevel):
    """Modal dialog for editing application settings."""

    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Settings")
        self.geometry("440x440")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self) -> None:
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=24, pady=24)
        outer.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(
            outer,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        row = 1

        # ── Network ────────────────────────────────────────────
        row = self._section(outer, "NETWORK", row)

        row = self._field_label(outer, "UDP Port", row)
        self._port_entry = ctk.CTkEntry(outer, placeholder_text="8000", width=130)
        self._port_entry.grid(row=row - 1, column=1, sticky="w", padx=(12, 0))
        port_val = self.settings.get("network", "port") or 8000
        self._port_entry.insert(0, str(port_val))

        row = self._field_label(outer, "Service Name", row)
        self._name_entry = ctk.CTkEntry(outer, placeholder_text="ServicesSound", width=200)
        self._name_entry.grid(row=row - 1, column=1, sticky="w", padx=(12, 0))
        name_val = self.settings.get("network", "service_name") or "ServicesSound"
        self._name_entry.insert(0, str(name_val))

        # ── Audio ──────────────────────────────────────────────
        row = self._section(outer, "AUDIO", row)

        row = self._field_label(outer, "Sample Rate (Hz)", row)
        self._rate_menu = ctk.CTkOptionMenu(
            outer, values=["22050", "44100", "48000"], width=130
        )
        self._rate_menu.grid(row=row - 1, column=1, sticky="w", padx=(12, 0))
        self._rate_menu.set(str(self.settings.get("audio", "sample_rate") or 44100))

        row = self._field_label(outer, "Channels", row)
        self._ch_menu = ctk.CTkOptionMenu(outer, values=["1", "2"], width=130)
        self._ch_menu.grid(row=row - 1, column=1, sticky="w", padx=(12, 0))
        self._ch_menu.set(str(self.settings.get("audio", "channels") or 2))

        # ── Appearance ─────────────────────────────────────────
        row = self._section(outer, "APPEARANCE", row)

        row = self._field_label(outer, "Theme", row)
        self._theme_menu = ctk.CTkOptionMenu(
            outer,
            values=["dark", "light", "system"],
            command=lambda v: ctk.set_appearance_mode(v),
            width=130,
        )
        self._theme_menu.grid(row=row - 1, column=1, sticky="w", padx=(12, 0))
        stored = self.settings.get("gui", "theme") or "dark"
        self._theme_menu.set(stored if stored in ("dark", "light", "system") else "dark")

        # ── Buttons ────────────────────────────────────────────
        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.grid(row=row, column=0, columnspan=2, sticky="e", pady=(20, 0))

        ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=90,
            height=36,
            fg_color=_BTN_SEC,
            hover_color=_BTN_SEC_HOVER,
            text_color=_BTN_SEC_TEXT,
            command=self.destroy,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Save",
            width=90,
            height=36,
            command=self._save,
        ).pack(side="left")

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _section(self, parent, title: str, row: int) -> int:
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 4))
        return row + 1

    def _field_label(self, parent, text: str, row: int) -> int:
        ctk.CTkLabel(parent, text=text).grid(
            row=row, column=0, sticky="w", pady=5
        )
        return row + 1

    def _save(self) -> None:
        try:
            port = int(self._port_entry.get())
            if not (1024 <= port <= 65535):
                raise ValueError("Port must be 1024–65535")
        except ValueError as exc:
            messagebox.showerror("Invalid Port", str(exc), parent=self)
            return

        self.settings.set("network", "port", port)
        self.settings.set(
            "network",
            "service_name",
            self._name_entry.get().strip() or "ServicesSound",
        )
        self.settings.set("audio", "sample_rate", int(self._rate_menu.get()))
        self.settings.set("audio", "channels", int(self._ch_menu.get()))
        self.settings.set("gui", "theme", self._theme_menu.get())

        logger.info("Settings saved")
        self.destroy()
