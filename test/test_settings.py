import json
import os

import pytest

from config.settings import Settings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def settings(tmp_path):
    """Return a Settings instance whose config_file points to a temp directory.

    The constructor calls load_settings() against its computed path first, so
    we create the instance normally and then redirect config_file + reset
    self.settings to a clean copy of DEFAULT_SETTINGS.
    """
    s = Settings()
    s.config_file = str(tmp_path / "settings.json")
    s.settings = s.DEFAULT_SETTINGS.copy()
    return s


# ---------------------------------------------------------------------------
# Default settings structure
# ---------------------------------------------------------------------------

def test_default_settings_have_required_keys(settings):
    """DEFAULT_SETTINGS must contain 'audio', 'network', and 'gui' sections."""
    keys = settings.settings.keys()
    assert "audio" in keys
    assert "network" in keys
    assert "gui" in keys


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

def test_get_audio_chunk_size(settings):
    """get('audio', 'chunk_size') must return the default value 1024."""
    assert settings.get("audio", "chunk_size") == 1024


def test_get_section_returns_dict(settings):
    """get('audio') with no key must return a dict."""
    result = settings.get("audio")
    assert isinstance(result, dict)


def test_get_missing_key_returns_none(settings):
    """get() for a key that does not exist must return None."""
    result = settings.get("audio", "nonexistent_key")
    assert result is None


# ---------------------------------------------------------------------------
# set()
# ---------------------------------------------------------------------------

def test_set_and_get_value(settings):
    """set() must update the in-memory value retrievable via get()."""
    settings.set("audio", "chunk_size", 2048)
    assert settings.get("audio", "chunk_size") == 2048


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_path):
    """Values written by save_settings() must survive a fresh load_settings()."""
    config_path = str(tmp_path / "settings.json")

    # Create first instance, modify, and save
    s1 = Settings()
    s1.config_file = config_path
    s1.settings = s1.DEFAULT_SETTINGS.copy()
    s1.set("audio", "chunk_size", 4096)
    s1.save_settings()

    # Create second instance pointing at the same file
    s2 = Settings()
    s2.config_file = config_path
    s2.settings = s2.load_settings()

    assert s2.get("audio", "chunk_size") == 4096


# ---------------------------------------------------------------------------
# Missing file fallback
# ---------------------------------------------------------------------------

def test_load_default_when_file_missing(settings):
    """load_settings() must return DEFAULT_SETTINGS when config_file does not exist."""
    # Ensure the file does not exist
    if os.path.exists(settings.config_file):
        os.remove(settings.config_file)

    loaded = settings.load_settings()

    assert loaded == Settings.DEFAULT_SETTINGS
