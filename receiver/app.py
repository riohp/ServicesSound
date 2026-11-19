"""ServicesSound Receiver — desktop client app."""

import json
import logging
import pathlib
import threading

import customtkinter as ctk

from .audio_player import AudioPlayer
from .client import ReceiverClient
from . import discovery

logger = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Color tokens ─────────────────────────────────────────────────────────────
_MUTED = ("gray50", "#8b9ab2")
_CARD = ("gray88", "#1e2433")
_BTN_SEC = ("gray75", "#2d3748")
_BTN_SEC_HOVER = ("gray65", "#374151")
_BTN_SEC_TEXT = ("gray10", "gray90")
_GREEN = ("#16a34a", "#4ade80")
_YELLOW = ("#ca8a04", "#facc15")
_RED = ("#dc2626", "#f87171")
_CLR_CONNECT = "#2563eb"
_CLR_CONNECT_HOVER = "#1d4ed8"
_CLR_DISCONNECT = "#dc2626"
_CLR_DISCONNECT_HOVER = "#b91c1c"

_LEVEL_GREEN = "#22c55e"
_LEVEL_YELLOW = "#eab308"
_LEVEL_RED = "#ef4444"

# ── Preferences persistence ───────────────────────────────────────────────────
_PREFS_FILE = pathlib.Path(__file__).parent / "receiver_prefs.json"


def _load_prefs() -> dict:
    try:
        return json.loads(_PREFS_FILE.read_text())
    except Exception:
        return {}


def _save_prefs(prefs: dict) -> None:
    try:
        _PREFS_FILE.write_text(json.dumps(prefs, indent=2))
    except Exception:
        pass


_DEFAULT_LABEL = "System Default"

# ── App ───────────────────────────────────────────────────────────────────────

class ReceiverApp(ctk.CTk):
    _POLL_MS = 180
    _W, _H = 440, 680

    def __init__(self) -> None:
        super().__init__()
        self.title("ServicesSound — Receiver")
        self.resizable(False, False)

        self._prefs = _load_prefs()
        self._player = AudioPlayer()
        self._client: ReceiverClient | None = None
        self._connected = False
        self._output_map: dict[str, int | None] = {_DEFAULT_LABEL: None}

        self._build()
        self._center()
        self._schedule_poll()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(300, self._auto_discover)

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self) -> None:
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=20)
        outer.grid_columnconfigure(0, weight=1)

        row = 0

        # Header
        ctk.CTkLabel(
            outer, text="ServicesSound",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=row, column=0, sticky="w")
        row += 1
        ctk.CTkLabel(
            outer, text="Audio receiver",
            font=ctk.CTkFont(size=12), text_color=_MUTED,
        ).grid(row=row, column=0, sticky="w")
        row += 1

        row = self._divider(outer, row)

        # ── Server ──────────────────────────────────────────────
        row = self._section_label(outer, "SERVER", row)

        ip_row = ctk.CTkFrame(outer, fg_color="transparent")
        ip_row.grid(row=row, column=0, sticky="ew")
        ip_row.grid_columnconfigure(0, weight=1)
        row += 1

        self._ip_entry = ctk.CTkEntry(
            ip_row,
            placeholder_text="Server IP  (e.g. 192.168.1.100)",
            height=38,
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        self._ip_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        last_ip = self._prefs.get("last_ip", "")
        if last_ip:
            self._ip_entry.insert(0, last_ip)

        ctk.CTkButton(
            ip_row, text="⟳", width=38, height=38,
            font=ctk.CTkFont(size=16),
            fg_color=_BTN_SEC, hover_color=_BTN_SEC_HOVER, text_color=_BTN_SEC_TEXT,
            command=self._auto_discover,
        ).grid(row=0, column=1)

        self._discover_label = ctk.CTkLabel(
            outer, text="", font=ctk.CTkFont(size=11), text_color=_MUTED,
        )
        self._discover_label.grid(row=row, column=0, sticky="w", pady=(4, 0))
        row += 1

        # ── Output device ────────────────────────────────────────
        row = self._section_label(outer, "OUTPUT DEVICE", row, top_pad=12)

        dev_row = ctk.CTkFrame(outer, fg_color="transparent")
        dev_row.grid(row=row, column=0, sticky="ew")
        dev_row.grid_columnconfigure(0, weight=1)
        row += 1

        self._output_menu = ctk.CTkOptionMenu(
            dev_row,
            values=[_DEFAULT_LABEL],
            command=self._on_output_device,
            dynamic_resizing=False,
            height=34,
        )
        self._output_menu.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(
            dev_row, text="⟳", width=34, height=34,
            font=ctk.CTkFont(size=14),
            fg_color=_BTN_SEC, hover_color=_BTN_SEC_HOVER, text_color=_BTN_SEC_TEXT,
            command=self._refresh_output_devices,
        ).grid(row=0, column=1)
        self._refresh_output_devices()

        # ── Auto-reconnect switch ────────────────────────────────
        switch_row = ctk.CTkFrame(outer, fg_color="transparent")
        switch_row.grid(row=row, column=0, sticky="ew", pady=(12, 0))
        switch_row.grid_columnconfigure(0, weight=1)
        row += 1

        ctk.CTkLabel(
            switch_row, text="Auto-reconnect",
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=0, sticky="w")

        self._reconnect_switch = ctk.CTkSwitch(
            switch_row, text="", width=44,
            onvalue=True, offvalue=False,
        )
        self._reconnect_switch.grid(row=0, column=1, sticky="e")
        if self._prefs.get("auto_reconnect", True):
            self._reconnect_switch.select()

        # ── Connect button ───────────────────────────────────────
        self._connect_btn = ctk.CTkButton(
            outer, text="▶  Connect",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50, corner_radius=8,
            fg_color=_CLR_CONNECT, hover_color=_CLR_CONNECT_HOVER,
            command=self._toggle_connection,
        )
        self._connect_btn.grid(row=row, column=0, sticky="ew", pady=(14, 0))
        row += 1

        row = self._divider(outer, row)

        # ── Status cards ─────────────────────────────────────────
        row = self._section_label(outer, "STATUS", row)

        cards = ctk.CTkFrame(outer, fg_color="transparent")
        cards.grid(row=row, column=0, sticky="ew")
        cards.grid_columnconfigure((0, 1, 2), weight=1)
        row += 1

        self._card_status = self._make_card(cards, "Connection", "Disconnected", col=0)
        self._card_packets = self._make_card(cards, "Received", "0", col=1)
        self._card_dropped = self._make_card(cards, "Dropped", "0", col=2)

        # ── Volume ───────────────────────────────────────────────
        vol = ctk.CTkFrame(outer, fg_color="transparent")
        vol.grid(row=row, column=0, sticky="ew", pady=(16, 0))
        vol.grid_columnconfigure(0, weight=1)
        row += 1

        vol_hdr = ctk.CTkFrame(vol, fg_color="transparent")
        vol_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        vol_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            vol_hdr, text="VOLUME",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w")

        self._vol_label = ctk.CTkLabel(
            vol_hdr, text="80%", font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._vol_label.grid(row=0, column=1, sticky="e")

        self._vol_slider = ctk.CTkSlider(
            vol, from_=0, to=100, number_of_steps=100, command=self._on_volume,
        )
        saved_vol = self._prefs.get("volume", 80)
        self._vol_slider.set(saved_vol)
        self._vol_label.configure(text=f"{saved_vol}%")
        self._player.set_volume(saved_vol / 100.0)
        self._vol_slider.grid(row=1, column=0, sticky="ew")

        # ── Audio level ───────────────────────────────────────────
        lvl = ctk.CTkFrame(outer, fg_color=_CARD, corner_radius=8)
        lvl.grid(row=row, column=0, sticky="ew", pady=(14, 0))
        lvl.grid_columnconfigure(0, weight=1)
        row += 1

        lvl_hdr = ctk.CTkFrame(lvl, fg_color="transparent")
        lvl_hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        lvl_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            lvl_hdr, text="AUDIO LEVEL",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=_MUTED,
        ).grid(row=0, column=0, sticky="w")

        self._level_pct = ctk.CTkLabel(
            lvl_hdr, text="0%", font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._level_pct.grid(row=0, column=1, sticky="e")

        self._level_bar = ctk.CTkProgressBar(
            lvl, height=12, corner_radius=4, progress_color=_LEVEL_GREEN,
        )
        self._level_bar.set(0)
        self._level_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))

        # Buffer fill sub-bar
        buf_row = ctk.CTkFrame(lvl, fg_color="transparent")
        buf_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        buf_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            buf_row, text="Buffer",
            font=ctk.CTkFont(size=9), text_color=_MUTED,
        ).grid(row=0, column=0, padx=(0, 8))

        self._buffer_bar = ctk.CTkProgressBar(
            buf_row, height=6, corner_radius=3,
            progress_color=("gray60", "#4b5563"),
        )
        self._buffer_bar.set(0)
        self._buffer_bar.grid(row=0, column=1, sticky="ew")

        self._buffer_label = ctk.CTkLabel(
            buf_row, text="0%",
            font=ctk.CTkFont(size=9), text_color=_MUTED, width=30,
        )
        self._buffer_label.grid(row=0, column=2, padx=(6, 0))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _divider(self, parent, row: int) -> int:
        ctk.CTkFrame(parent, height=1, fg_color=("gray80", "#2d3748")).grid(
            row=row, column=0, sticky="ew", pady=14,
        )
        return row + 1

    def _section_label(self, parent, text: str, row: int, top_pad: int = 0) -> int:
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=10, weight="bold"), text_color=_MUTED,
        ).grid(row=row, column=0, sticky="w", pady=(top_pad, 6))
        return row + 1

    def _make_card(
        self, parent: ctk.CTkFrame, title: str, value: str, col: int
    ) -> ctk.CTkLabel:
        padx = (0, 6) if col < 2 else 0
        card = ctk.CTkFrame(parent, fg_color=_CARD, corner_radius=8)
        card.grid(row=0, column=col, sticky="ew", padx=padx)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=9), text_color=_MUTED,
        ).grid(row=0, column=0, padx=10, pady=(8, 1), sticky="w")
        lbl = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=13, weight="bold"),
        )
        lbl.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")
        return lbl

    # ── Output devices ───────────────────────────────────────────────────────

    def _refresh_output_devices(self) -> None:
        try:
            devices = AudioPlayer.list_output_devices()
        except Exception as exc:
            logger.warning("Could not list output devices: %s", exc)
            devices = []

        self._output_map = {_DEFAULT_LABEL: None}
        for dev in devices:
            label = dev["name"][:32] + ("…" if len(dev["name"]) > 32 else "")
            self._output_map[label] = dev["index"]

        names = list(self._output_map.keys())
        self._output_menu.configure(values=names)
        self._output_menu.set(names[0])
        self._player.set_device(None)

    def _on_output_device(self, label: str) -> None:
        idx = self._output_map.get(label)
        self._player.set_device(idx)

    # ── Discovery ────────────────────────────────────────────────────────────

    def _auto_discover(self) -> None:
        self._discover_label.configure(text="Searching for server…", text_color=_MUTED)
        threading.Thread(target=self._discover_worker, daemon=True).start()

    def _discover_worker(self) -> None:
        ip = discovery.find_server(timeout=4.0)
        if ip:
            self.after(0, lambda: self._ip_entry.delete(0, "end"))
            self.after(0, lambda: self._ip_entry.insert(0, ip))
            self.after(0, lambda: self._discover_label.configure(
                text=f"Found: {ip}", text_color=_GREEN,
            ))
        else:
            self.after(0, lambda: self._discover_label.configure(
                text="Not found — enter IP manually", text_color=_MUTED,
            ))

    # ── Connection ───────────────────────────────────────────────────────────

    def _toggle_connection(self) -> None:
        if self._connected:
            self._disconnect()
        else:
            self._connect()

    def _connect(self) -> None:
        ip = self._ip_entry.get().strip()
        if not ip:
            return
        try:
            auto_rec = bool(self._reconnect_switch.get())
            self._client = ReceiverClient(server_ip=ip)
            self._client.set_auto_reconnect(auto_rec)
            self._client.set_chunk_callback(self._player.put_chunk)
            self._client.set_disconnect_callback(
                lambda: self.after(0, self._on_server_disconnect)
            )
            self._client.set_reconnecting_callback(
                lambda n: self.after(0, lambda: self._on_reconnecting(n))
            )
            self._player.start()
            self._client.connect()
            self._connected = True
            self._connect_btn.configure(
                text="■  Disconnect",
                fg_color=_CLR_DISCONNECT, hover_color=_CLR_DISCONNECT_HOVER,
            )
            self._ip_entry.configure(state="disabled")
            self._output_menu.configure(state="disabled")
            self._save_session_prefs(ip)
            logger.info("Connected to %s", ip)
        except Exception as exc:
            from tkinter import messagebox
            messagebox.showerror("Connection Error", f"Could not connect:\n{exc}")

    def _disconnect(self) -> None:
        if self._client:
            self._client.disconnect()
            self._client = None
        self._player.stop()
        self._connected = False
        self._connect_btn.configure(
            text="▶  Connect",
            fg_color=_CLR_CONNECT, hover_color=_CLR_CONNECT_HOVER,
        )
        self._ip_entry.configure(state="normal")
        self._output_menu.configure(state="normal")

    def _on_server_disconnect(self) -> None:
        self._disconnect()
        self._card_status.configure(text="Lost connection", text_color=_RED)

    def _on_reconnecting(self, attempt: int) -> None:
        self._card_status.configure(
            text=f"Reconnecting… ({attempt})", text_color=_YELLOW,
        )

    # ── Polling ──────────────────────────────────────────────────────────────

    def _schedule_poll(self) -> None:
        self._poll()
        self.after(self._POLL_MS, self._schedule_poll)

    def _poll(self) -> None:
        if self._connected and self._client:
            self._card_status.configure(text="● Connected", text_color=_GREEN)
            self._card_packets.configure(text=str(self._client.packets_received))
            self._card_dropped.configure(text=str(self._player.packets_dropped))
        elif not self._connected:
            self._card_packets.configure(text="0")
            self._card_dropped.configure(text="0")

        # Audio level with color
        level = self._player.level
        self._level_bar.set(level)
        self._level_pct.configure(text=f"{int(level * 100)}%")
        if level < 0.6:
            color = _LEVEL_GREEN
        elif level < 0.82:
            color = _LEVEL_YELLOW
        else:
            color = _LEVEL_RED
        self._level_bar.configure(progress_color=color)

        # Buffer fill
        fill = self._player.buffer_fill
        self._buffer_bar.set(fill)
        self._buffer_label.configure(text=f"{int(fill * 100)}%")

    # ── Volume ───────────────────────────────────────────────────────────────

    def _on_volume(self, value: float) -> None:
        pct = int(value)
        self._vol_label.configure(text=f"{pct}%")
        self._player.set_volume(value / 100.0)

    # ── Prefs ─────────────────────────────────────────────────────────────────

    def _save_session_prefs(self, ip: str) -> None:
        self._prefs["last_ip"] = ip
        self._prefs["volume"] = int(self._vol_slider.get())
        self._prefs["auto_reconnect"] = bool(self._reconnect_switch.get())
        _save_prefs(self._prefs)

    # ── Window ────────────────────────────────────────────────────────────────

    def _center(self) -> None:
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self._W}x{self._H}+{(sw - self._W) // 2}+{(sh - self._H) // 2}")

    def _on_closing(self) -> None:
        self._prefs["volume"] = int(self._vol_slider.get())
        self._prefs["auto_reconnect"] = bool(self._reconnect_switch.get())
        _save_prefs(self._prefs)
        self._disconnect()
        self.destroy()
