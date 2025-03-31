import pyaudio

class AudioConfig:
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 2
    RATE = 44100
    PORT = 8000
    
    @classmethod
    def get_config(cls):
        return {
            "chunk": cls.CHUNK,
            "format": cls.FORMAT,
            "channels": cls.CHANNELS,
            "rate": cls.RATE,
            "port": cls.PORT
        }
