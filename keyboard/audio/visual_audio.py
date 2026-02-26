import time
import subprocess
import tempfile
from subprocess import run

import numpy as np
import pyaudio
import scipy.signal

# Settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # or 48000
BRIGHTNESSCTL_PATH = "/usr/local/bin/mac-brightnessctl"
BASS_THRESHOLD = 1000  # Adjust for sensitivity
COOLDOWN = 0.3  # seconds between flashes
# Visualizer settings (CAVA handles visualization)
CAVA_CMD = ["cava"]

# Bandpass filter (bass range: ~20-250 Hz)
def bass_filter(data):
    sos = scipy.signal.butter(4, [20, 250], btype="bandpass", fs=RATE, output="sos")
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
    index = int(choice)
    name = p.get_device_info_by_index(index)["name"]
    return index, name


def start_cava(device_name):
    # Let cava own the terminal for visualization using a dedicated config.
    config = f"""
[general]
framerate = 60
autosens = 1

[input]
method = portaudio
source = "{device_name}"
sample_rate = {RATE}
channels = {CHANNELS}

[output]
method = noncurses
channels = mono
"""
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="cava_", suffix=".conf")
    tmp.write(config)
    tmp.flush()
    tmp.close()
    return subprocess.Popen(CAVA_CMD + ["-p", tmp.name])


def runloop(stream, cava_proc):
    last_flash = 0

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            continue

        # Bass energy
        bass_data = bass_filter(samples)
        bass_rms = np.sqrt(np.mean(bass_data ** 2))

        # Flash on bass hit
        if bass_rms > BASS_THRESHOLD and (time.time() - last_flash) > COOLDOWN:
            flash_keyboard()
            last_flash = time.time()


if __name__ == "__main__":
    print("[+] Starting bass beat visualizer (CAVA)...")
    p = pyaudio.PyAudio()
    index, device_name = get_input_device_index(p)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=index,
        frames_per_buffer=CHUNK,
    )

    cava_proc = start_cava(device_name)

    try:
        runloop(stream, cava_proc)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
        if cava_proc.poll() is None:
            cava_proc.terminate()
        print("[X] Stopped.")
