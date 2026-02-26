import numpy as np
import pyaudio
import scipy.signal
from subprocess import run
import time

# Settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # or 48000
BRIGHTNESSCTL_PATH = "/usr/local/bin/mac-brightnessctl"
BASS_THRESHOLD = 1000  # Adjust for sensitivity
COOLDOWN = 0.3  # seconds between flashes

# Bandpass filter (bass range: ~20-250 Hz)
def bass_filter(data):
    sos = scipy.signal.butter(4, [20, 250], btype='bandpass', fs=RATE, output='sos')
    return scipy.signal.sosfilt(sos, data)

def flash_keyboard():
    # Quick flash
    run([BRIGHTNESSCTL_PATH, "-f", "1", "0.05", "100"])

def get_input_device_index(p):
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"  {i}: {info['name']}")
    choice = input("Select input device index: ")
    return int(choice)

def runloop(stream):
    last_flash = 0
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            continue

        bass_data = bass_filter(samples)
        rms = np.sqrt(np.mean(bass_data ** 2))

        print(f"Bass RMS: {rms:.1f}")

        if rms > BASS_THRESHOLD and (time.time() - last_flash) > COOLDOWN:
            flash_keyboard()
            last_flash = time.time()

if __name__ == "__main__":
    print("[+] Starting bass beat sync...")
    p = pyaudio.PyAudio()
    index = get_input_device_index(p)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=index,
                    frames_per_buffer=CHUNK)

    try:
        runloop(stream)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[X] Stopped.")