import os
import json
import logging

class Settings:
    DEFAULT_SETTINGS = {
        "audio": {
            "chunk_size": 1024,
            "channels": 2,
            "sample_rate": 44100,
            "format": "paFloat32"
        },
        "network": {
            "port": 8000,
            "service_name": "ServicesSound"
        },
        "gui": {
            "theme": "default",
            "window_size": "800x600",
            "default_volume": 80
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "settings.json"
        )
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load settings from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                self.logger.info("Settings loaded from file")
                return settings
            else:
                self.save_settings(self.DEFAULT_SETTINGS)
                self.logger.info("Default settings created")
                return self.DEFAULT_SETTINGS
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return self.DEFAULT_SETTINGS
            
    def save_settings(self, settings=None):
        """Save settings to file"""
        if settings is None:
            settings = self.settings
            
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.logger.info("Settings saved to file")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
            
    def get(self, section, key=None):
        """Get a setting value"""
        try:
            if key is None:
                return self.settings.get(section, {})
            return self.settings.get(section, {}).get(key)
        except Exception as e:
            self.logger.error(f"Error getting setting {section}.{key}: {e}")
            # Get from default settings
            if key is None:
                return self.DEFAULT_SETTINGS.get(section, {})
            return self.DEFAULT_SETTINGS.get(section, {}).get(key)
            
    def set(self, section, key, value):
        """Set a setting value"""
        try:
            if section not in self.settings:
                self.settings[section] = {}
            self.settings[section][key] = value
            self.save_settings()
            return True
        except Exception as e:
            self.logger.error(f"Error setting {section}.{key}: {e}")
            return False