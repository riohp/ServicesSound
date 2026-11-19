import logging

import customtkinter as ctk

try:
    from src.utils.helpers import get_local_ip
except Exception:
    def get_local_ip() -> str:
        return "Unknown"

logger = logging.getLogger(__name__)

_MUTED = ("gray50", "#8b9ab2")
_CARD_BG = ("gray88", "#1e2433")
_GREEN_LIGHT = "#16a34a"
_GREEN_DARK = "#4ade80"
_GREEN = (_GREEN_LIGHT, _GREEN_DARK)
_BTN_SEC = ("gray75", "#2d3748")
_BTN_SEC_HOVER = ("gray65", "#374151")
_BTN_SEC_TEXT = ("gray10", "gray90")


class StatusPanel(ctk.CTkFrame):
    """Right-side status panel: server state, audio level, connected devices."""

    _POLL_MS = 250

    def __init__(self, parent, audio_server=None, tunnel_manager=None) -> None:
        super().__init__(parent, corner_radius=12)
        self.audio_server = audio_server
        self.tunnel_manager = tunnel_manager
        self._build()
        self._schedule_poll()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # ── Section title ────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="SYSTEM STATUS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ── Metric cards ─────────────────────────────────────────
        cards_row = ctk.CTkFrame(self, fg_color="transparent")
        cards_row.grid(row=1, column=0, sticky="ew", padx=20)
        cards_row.grid_columnconfigure((0, 1, 2), weight=1)

        self._card_server = self._make_card(cards_row, "Server", "○ Stopped", col=0)
        self._card_ip = self._make_card(cards_row, "IP Address", get_local_ip(), col=1)
        self._card_clients = self._make_card(cards_row, "Devices", "0", col=2)

        # ── Audio level ──────────────────────────────────────────
        lvl_frame = ctk.CTkFrame(self, fg_color=_CARD_BG, corner_radius=8)
        lvl_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(14, 0))
        lvl_frame.grid_columnconfigure(0, weight=1)

        lvl_header = ctk.CTkFrame(lvl_frame, fg_color="transparent")
        lvl_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        lvl_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            lvl_header,
            text="AUDIO LEVEL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w")

        self._level_pct = ctk.CTkLabel(
            lvl_header,
            text="0%",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._level_pct.grid(row=0, column=1, sticky="e")

        self._level_bar = ctk.CTkProgressBar(lvl_frame, height=12, corner_radius=4)
        self._level_bar.set(0)
        self._level_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # ── Connected devices ────────────────────────────────────
        dev_frame = ctk.CTkFrame(self, fg_color=_CARD_BG, corner_radius=8)
        dev_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(12, 20))
        dev_frame.grid_columnconfigure(0, weight=1)
        dev_frame.grid_columnconfigure(1, weight=0)
        dev_frame.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            dev_frame,
            text="STREAM URL & CLIENTES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        self._copy_btn = ctk.CTkButton(
            dev_frame,
            text="📋 Copiar URL",
            width=110,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=_BTN_SEC,
            hover_color=_BTN_SEC_HOVER,
            text_color=_BTN_SEC_TEXT,
            command=self._copy_stream_url,
        )
        self._copy_btn.grid(row=0, column=1, sticky="e", padx=16, pady=(10, 4))

        self._devices_box = ctk.CTkTextbox(
            dev_frame,
            height=90,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent",
            state="disabled",
        )
        self._devices_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0, 8))

    def _copy_stream_url(self) -> None:
        url = None
        if self.tunnel_manager and self.tunnel_manager.is_active:
            url = self.tunnel_manager.stream_url
        if not url:
            port = getattr(self.audio_server, "port", 8000)
            url = f"http://{get_local_ip()}:{port}/stream.mp3"
        self.clipboard_clear()
        self.clipboard_append(url)
        self._copy_btn.configure(text="¡Copiado!")
        self.after(2000, lambda: self._copy_btn.configure(text="📋 Copiar URL"))

    def _make_card(
        self, parent: ctk.CTkFrame, title: str, value: str, col: int
    ) -> ctk.CTkLabel:
        padx = (0, 10) if col < 2 else 0
        card = ctk.CTkFrame(parent, fg_color=_CARD_BG, corner_radius=8)
        card.grid(row=0, column=col, sticky="ew", padx=padx)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=10),
            text_color=_MUTED,
        ).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")

        val_lbl = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        val_lbl.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
        return val_lbl

    def _schedule_poll(self) -> None:
        self._poll()
        self.after(self._POLL_MS, self._schedule_poll)

    def _poll(self) -> None:
        if self.audio_server is None:
            return

        running = self.audio_server.is_running
        self._card_server.configure(
            text="● Running" if running else "○ Stopped",
            text_color=_GREEN if running else _MUTED,
        )

        level = self.audio_server.audio_level
        self._level_bar.set(level)
        self._level_pct.configure(text=f"{int(level * 100)}%")

        count = self.audio_server.client_count
        label = "connected" if count == 1 else "devices"
        self._card_clients.configure(text=f"{count} {label}")

        clients = self.audio_server.get_clients() if count > 0 else []
        self._devices_box.configure(state="normal")
        self._devices_box.delete("1.0", "end")

        port = getattr(self.audio_server, "port", 8000)
        local_url = f"http://{get_local_ip()}:{port}/stream.mp3"
        self._devices_box.insert("end", f"Red Local: {local_url}\n")

        if self.tunnel_manager and self.tunnel_manager.is_active:
            self._devices_box.insert("end", f"Alexa HTTPS: {self.tunnel_manager.stream_url}\n\n")
        else:
            self._devices_box.insert("end", "Alexa HTTPS: Inactivo (pulsa Start Streaming)\n\n")

        if clients:
            self._devices_box.insert("end", "Clientes conectados:\n")
            for ip in clients:
                self._devices_box.insert("end", f"  ●  {ip}\n")
        else:
            self._devices_box.insert("end", "Esperando conexión de Alexa...\n")
        self._devices_box.configure(state="disabled")
