import logging

import customtkinter as ctk
from tkinter import messagebox

from src.audio.audio_processor import AudioCapture
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

_CLR_START = "#2563eb"
_CLR_START_HOVER = "#1d4ed8"
_CLR_STOP = "#dc2626"
_CLR_STOP_HOVER = "#b91c1c"
_MUTED = ("gray50", "#8b9ab2")
_BTN_SEC = ("gray75", "#2d3748")
_BTN_SEC_HOVER = ("gray65", "#374151")
_BTN_SEC_TEXT = ("gray10", "gray90")

_DEFAULT_LABEL = "System Default"


class ControlPanel(ctk.CTkFrame):
    """Left-side control panel: device selector, streaming toggle, volume, settings, help."""

    def __init__(self, parent, audio_server=None, settings=None, tunnel_manager=None) -> None:
        super().__init__(parent, width=268, corner_radius=12)
        self.audio_server = audio_server
        self.settings = settings
        self.tunnel_manager = tunnel_manager
        self._is_streaming = False
        self._device_map: dict[str, int | None] = {_DEFAULT_LABEL: None}
        self.grid_propagate(False)
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # ── App header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(22, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="ServicesSound",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="PC audio → Alexa",
            font=ctk.CTkFont(size=11),
            text_color=_MUTED,
        ).grid(row=1, column=0, sticky="w")

        # ── Divider ─────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=("gray80", "#2d3748")).grid(
            row=1, column=0, sticky="ew", padx=20, pady=4
        )

        # ── Audio device section ────────────────────────────────
        dev_section = ctk.CTkFrame(self, fg_color="transparent")
        dev_section.grid(row=2, column=0, sticky="ew", padx=20, pady=(14, 4))
        dev_section.grid_columnconfigure(0, weight=1)

        dev_header = ctk.CTkFrame(dev_section, fg_color="transparent")
        dev_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        dev_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dev_header,
            text="AUDIO INPUT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            dev_header,
            text="⟳",
            width=26,
            height=20,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=("gray80", "#374151"),
            text_color=_MUTED,
            command=self._refresh_devices,
        ).grid(row=0, column=1, sticky="e")

        self._device_menu = ctk.CTkOptionMenu(
            dev_section,
            values=[_DEFAULT_LABEL],
            command=self._on_device_change,
            dynamic_resizing=False,
            height=32,
        )
        self._device_menu.grid(row=1, column=0, sticky="ew")
        self._refresh_devices()

        # ── Streaming section ───────────────────────────────────
        stream = ctk.CTkFrame(self, fg_color="transparent")
        stream.grid(row=3, column=0, sticky="ew", padx=20, pady=(14, 8))
        stream.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            stream,
            text="STREAMING",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._toggle_btn = ctk.CTkButton(
            stream,
            text="▶  Start Streaming",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            corner_radius=8,
            fg_color=_CLR_START,
            hover_color=_CLR_START_HOVER,
            command=self._toggle_streaming,
        )
        self._toggle_btn.grid(row=1, column=0, sticky="ew")

        # ── Volume section ──────────────────────────────────────
        vol = ctk.CTkFrame(self, fg_color="transparent")
        vol.grid(row=4, column=0, sticky="ew", padx=20, pady=(18, 8))
        vol.grid_columnconfigure(0, weight=1)

        vol_header = ctk.CTkFrame(vol, fg_color="transparent")
        vol_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        vol_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            vol_header,
            text="VOLUME",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w")

        self._vol_label = ctk.CTkLabel(
            vol_header,
            text="80%",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._vol_label.grid(row=0, column=1, sticky="e")

        initial = 80
        if self.settings:
            v = self.settings.get("gui", "default_volume")
            if v is not None:
                initial = int(v)

        self._volume_slider = ctk.CTkSlider(
            vol,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_volume_change,
        )
        self._volume_slider.set(initial)
        self._volume_slider.grid(row=1, column=0, sticky="ew")

        # ── Spacer ──────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").grid(row=5, column=0, sticky="nsew")
        self.grid_rowconfigure(5, weight=1)

        # ── Divider + footer ────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=("gray80", "#2d3748")).grid(
            row=6, column=0, sticky="ew", padx=20, pady=4
        )

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=7, column=0, sticky="ew", padx=20, pady=(8, 20))
        footer.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            footer,
            text="⚙  Settings",
            height=36,
            corner_radius=6,
            fg_color=_BTN_SEC,
            hover_color=_BTN_SEC_HOVER,
            text_color=_BTN_SEC_TEXT,
            command=self._open_settings,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            footer,
            text="?  Help",
            height=36,
            corner_radius=6,
            fg_color=_BTN_SEC,
            hover_color=_BTN_SEC_HOVER,
            text_color=_BTN_SEC_TEXT,
            command=self._show_help,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    # ── Device management ────────────────────────────────────────────────────

    def _refresh_devices(self) -> None:
        """Reload available input devices and update the dropdown."""
        try:
            devices = AudioCapture.list_input_devices()
        except Exception as exc:
            logger.warning("Could not enumerate audio devices: %s", exc)
            devices = []

        self._device_map = {_DEFAULT_LABEL: None}
        for dev in devices:
            label = self._truncate(dev["name"], 28)
            self._device_map[label] = dev["index"]

        names = list(self._device_map.keys())
        self._device_menu.configure(values=names)
        self._device_menu.set(names[0])

        if self.audio_server and hasattr(self.audio_server, "set_device"):
            self.audio_server.set_device(None)

        logger.debug("Audio devices refreshed: %d found", len(devices))

    def _on_device_change(self, label: str) -> None:
        device_index = self._device_map.get(label)
        if self.audio_server and hasattr(self.audio_server, "set_device"):
            self.audio_server.set_device(device_index)
        logger.debug("Audio device selected: %s (index=%s)", label, device_index)

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        return text if len(text) <= max_len else text[: max_len - 1] + "…"

    # ── Streaming ────────────────────────────────────────────────────────────

    def _toggle_streaming(self) -> None:
        if self.audio_server is None:
            return
        if self._is_streaming:
            self.audio_server.stop()
            if self.tunnel_manager and self.tunnel_manager.is_active:
                self.tunnel_manager.stop_tunnel()
            self._set_stopped()
        else:
            try:
                self.audio_server.start_async()
                if self.tunnel_manager:
                    self.tunnel_manager.start_tunnel()
                self._set_running()
            except Exception as exc:
                logger.error("Failed to start streaming: %s", exc)
                messagebox.showerror(
                    "Streaming Error",
                    f"Could not start audio streaming:\n{exc}\n\n"
                    "Check that your audio device is available.",
                )

    def _set_running(self) -> None:
        self._is_streaming = True
        self._device_menu.configure(state="disabled")
        self._toggle_btn.configure(
            text="■  Stop Streaming",
            fg_color=_CLR_STOP,
            hover_color=_CLR_STOP_HOVER,
        )

    def _set_stopped(self) -> None:
        self._is_streaming = False
        self._device_menu.configure(state="normal")
        self._toggle_btn.configure(
            text="▶  Start Streaming",
            fg_color=_CLR_START,
            hover_color=_CLR_START_HOVER,
        )

    # ── Volume ───────────────────────────────────────────────────────────────

    def _on_volume_change(self, value: float) -> None:
        pct = int(value)
        self._vol_label.configure(text=f"{pct}%")
        if self.audio_server and hasattr(self.audio_server, "set_volume"):
            self.audio_server.set_volume(value / 100.0)
        if self.settings:
            self.settings.set("gui", "default_volume", pct)

    # ── Dialogs ──────────────────────────────────────────────────────────────

    def _open_settings(self) -> None:
        if self.settings:
            SettingsDialog(self, self.settings)

    def _show_help(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Help")
        dialog.geometry("430x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(
            frame,
            text="How to use ServicesSound",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", pady=(0, 14))

        steps = [
            "1.  Select your audio input device from the dropdown.",
            "2.  Make sure your Alexa is on the same Wi-Fi network.",
            "3.  Click  ▶  Start Streaming  to begin capturing.",
            '4.  On your Alexa, say  "Alexa, connect to PC Audio".',
            "5.  Adjust the volume slider to control broadcast level.",
        ]
        for step in steps:
            ctk.CTkLabel(
                frame,
                text=step,
                font=ctk.CTkFont(size=12),
                justify="left",
                wraplength=380,
            ).pack(anchor="w", pady=2)

        ctk.CTkButton(
            frame,
            text="Got it",
            width=90,
            height=34,
            command=dialog.destroy,
        ).pack(anchor="e", pady=(16, 0))
