import platform
import soundcard as sc
import numpy as np
import soundfile as sf
import tempfile
import os
import threading
from config import logger

class CrossPlatformAudioRecorder:
    def __init__(self, samplerate=48000):
        self.fs = samplerate
        self.temp_file_path = None
        self.recording = False
        self.threads = []
        self.mic_buffer = []
        self.loopback_buffer = []

    def _get_devices(self):
        system = platform.system()
        mic = None
        loopback = None

        if system == "Windows":
            try:
                mic = sc.default_microphone()
                speaker = sc.default_speaker()
                loopback = sc.get_microphone(speaker.id, include_loopback=True)
                logger.info(f"Using default Windows devices.")
            except Exception as e:
                logger.error(f"Error getting default Windows devices: {e}")
        elif system == "Darwin":
            try:
                # On macOS, user should have an aggregate device or blackhole
                mics = sc.all_microphones()
                for m in mics:
                    if "aggregate" in m.name.lower() or "blackhole" in m.name.lower():
                        loopback = m
                        break
                mic = sc.default_microphone()
                logger.info(f"Using macOS devices.")
            except Exception as e:
                logger.error(f"Error getting macOS devices: {e}")
        else:
            mic = sc.default_microphone()
            logger.info("Using default fallback devices.")
            
        return mic, loopback

    def _record_stream(self, device, buffer_list, name="Unknown"):
        logger.info(f"Opening stream on device: {name} at {self.fs}Hz")
        try:
            with device.recorder(samplerate=self.fs) as rec:
                while self.recording:
                    # Record in small chunks (e.g., 4800 frames = 0.1s)
                    data = rec.record(numframes=4800)
                    buffer_list.append(data.copy())
        except Exception as e:
            logger.error(f"Failed to record from device {name}: {e}")

    def start_recording(self):
        mic, loopback = self._get_devices()
        self.recording = True
        self.mic_buffer = []
        self.loopback_buffer = []

        logger.info(f"Starting recording... (Mic: {mic.name if mic else 'None'}, Loopback: {loopback.name if loopback else 'None'})")
        
        self.threads = []
        if mic is not None:
            self.threads.append(threading.Thread(target=self._record_stream, args=(mic, self.mic_buffer, f"Mic-{mic.name}")))
        if loopback is not None:
            # Check if mic and loopback are the exact same device object (e.g. Aggregate Device on Mac)
            if mic.id != loopback.id:
                self.threads.append(threading.Thread(target=self._record_stream, args=(loopback, self.loopback_buffer, f"Loopback-{loopback.name}")))
            else:
                logger.info("Mic and loopback are the same device, capturing as one stream.")

        for t in self.threads:
            t.start()

    def stop_recording(self) -> str:
        self.recording = False
        for t in self.threads:
            t.join()

        logger.info("Recording stopped. Mixing streams...")
        
        m_audio = np.concatenate(self.mic_buffer) if self.mic_buffer else np.array([])
        l_audio = np.concatenate(self.loopback_buffer) if self.loopback_buffer else np.array([])
        
        max_len = max(len(m_audio), len(l_audio))
        if max_len == 0:
            return None

        # soundcard captures in (frames, channels) format, often stereo
        m_channels = m_audio.shape[1] if len(m_audio.shape) > 1 else 1
        l_channels = l_audio.shape[1] if len(l_audio.shape) > 1 else 1
        target_channels = max(2, m_channels, l_channels)

        mixed_audio = np.zeros((max_len, target_channels))
        
        if len(m_audio) > 0:
            # If mono, broadcast to all channels, if stereo, keep stereo
            if m_channels == 1:
                mixed_audio[:len(m_audio), :] += np.reshape(m_audio, (-1, 1))
            else:
                mixed_audio[:len(m_audio), :m_channels] += m_audio
                
        if len(l_audio) > 0:
            if l_channels == 1:
                mixed_audio[:len(l_audio), :] += np.reshape(l_audio, (-1, 1))
            else:
                mixed_audio[:len(l_audio), :l_channels] += l_audio
            
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed_audio))
        if max_val > 1.0:
            mixed_audio /= max_val

        temp_fd, self.temp_file_path = tempfile.mkstemp(suffix=".wav")
        os.close(temp_fd)
        
        sf.write(self.temp_file_path, mixed_audio, self.fs)
        logger.info(f"Saved temporary audio to {self.temp_file_path}")
        return self.temp_file_path

    def cleanup(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
            logger.info("Cleaned up temporary audio file.")
