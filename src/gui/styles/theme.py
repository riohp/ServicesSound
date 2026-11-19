"""CustomTkinter appearance configuration for ServicesSound."""

import logging
import customtkinter as ctk

logger = logging.getLogger(__name__)

APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"


def apply_theme(appearance: str = APPEARANCE_MODE) -> None:
    """Configure CTk appearance mode and color theme."""
    ctk.set_appearance_mode(appearance)
    ctk.set_default_color_theme(COLOR_THEME)
    logger.debug("Theme applied: mode=%s, theme=%s", appearance, COLOR_THEME)
