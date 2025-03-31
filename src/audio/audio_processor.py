import numpy as np

class AudioProcessor:
    @staticmethod
    def normalize_audio(audio_data, threshold=1.5):
        return np.clip(audio_data * threshold, -1, 1)
    
    @staticmethod
    def convert_to_bytes(audio_data):
        return audio_data.tobytes()