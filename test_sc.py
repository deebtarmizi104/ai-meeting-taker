import soundcard as sc
import threading
import numpy as np

def test_recording():
    mic = sc.default_microphone()
    speaker = sc.default_speaker()
    
    # Get loopback microphone corresponding to the default speaker
    loopback_mic = sc.get_microphone(speaker.id, include_loopback=True)
    
    print(f"Mic: {mic.name}")
    print(f"Loopback: {loopback_mic.name}")
    
    mic_data = []
    loopback_data = []
    recording = True
    
    def record_mic():
        with mic.recorder(samplerate=48000) as rec:
            while recording:
                mic_data.append(rec.record(numframes=4800))
                
    def record_loopback():
        with loopback_mic.recorder(samplerate=48000) as rec:
            while recording:
                loopback_data.append(rec.record(numframes=4800))

    t1 = threading.Thread(target=record_mic)
    t2 = threading.Thread(target=record_loopback)
    t1.start()
    t2.start()
    
    import time
    time.sleep(3)
    recording = False
    
    t1.join()
    t2.join()
    
    m = np.concatenate(mic_data) if mic_data else np.array([])
    l = np.concatenate(loopback_data) if loopback_data else np.array([])
    
    print(f"Mic shape: {m.shape}")
    print(f"Loopback shape: {l.shape}")

if __name__ == '__main__':
    test_recording()
