import sounddevice as sd
import numpy as np
import threading
import wave
import time

class audioBackend:
    def __init__(self):
        self.fs = 44100  # Sample rate
        self.recording = False
        self.frames = []
        self.thread = None

    def start_recording(self):
        if self.recording:
            print("Already recording")
            return False

        self.recording = True
        self.frames = []

        def callback(indata, frames, time, status):
            if self.recording:
                self.frames.append(indata.copy())
            else:
                raise sd.CallbackStop

        self.thread = threading.Thread(target=self._record, args=(callback,))
        self.thread.start()
        print("Recording started")
        return True

    def _record(self, callback):
        with sd.InputStream(callback=callback, channels=1, samplerate=self.fs):
            while self.recording:
                sd.sleep(100)

    def stop_recording(self):
        if not self.recording:
            print("Not recording")
            return False

        self.recording = False
        self.thread.join()
        print("Recording stopped")
        self.save_recording()
        return True

    def save_recording(self):
        # Flatten the frames and convert to numpy array
        audio_data = np.concatenate(self.frames, axis=0)
        audio_data = np.squeeze(audio_data)

        # Save the recording to a WAV file
        timestamp = int(time.time())
        filename = f"recording.wav"
        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(1)  # Mono
        wave_file.setsampwidth(2)  # Sample width in bytes
        wave_file.setframerate(self.fs)
        wave_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        wave_file.close()
        print(f"Recording saved to {filename}")
