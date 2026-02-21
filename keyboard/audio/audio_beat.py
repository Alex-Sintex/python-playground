import time
from subprocess import run

import numpy as np
import pyaudio
import scipy.signal

# =========================
# Config
# =========================
RATE = 44100
CHUNK = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

BASS_BAND = (20, 200)

ENV_ALPHA = 0.2
FLUX_ALPHA = 0.3

KICK_THRESHOLD = 1.5      # sensitivity
FLASH_COOLDOWN = 0.15

BRIGHTNESSCTL_PATH = "/usr/local/bin/mac-brightnessctl"

# =========================
# Helpers
# =========================
def ema(prev, x, alpha):
    return x if prev is None else (1 - alpha) * prev + alpha * x

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def rms(x):
    return np.sqrt(np.mean(x * x) + 1e-12)

def butter_bandpass(low, high, fs):
    return scipy.signal.butter(
        4, [low, high],
        btype="bandpass",
        fs=fs,
        output="sos"
    )

def flash_keyboard(intensity):
    percent = int(clamp(intensity, 0.05, 1.0) * 100)
    run([
        BRIGHTNESSCTL_PATH,
        "-f", "1",
        "0.08",
        f"{percent}"
    ])

# =========================
# Audio device
# =========================
def get_blackhole_device_index(p):
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "blackhole" in info["name"].lower():
            print(f"[+] BlackHole selected: {info['name']} (index {i})")
            return i
    return int(input("Select input device index: "))

# =========================
# Main loop
# =========================
def runloop(stream):
    bass_sos = butter_bandpass(*BASS_BAND, RATE)

    prev_spectrum = None
    flux_ema = None
    bass_env = None
    last_flash = 0.0

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, np.int16).astype(np.float32) / 32768.0

        # Band-pass bass
        bass = scipy.signal.sosfilt(bass_sos, samples)

        # Envelope (energy)
        bass_energy = rms(bass)
        bass_env = ema(bass_env, bass_energy, ENV_ALPHA)

        # Spectrum (FFT)
        spectrum = np.abs(np.fft.rfft(bass))

        if prev_spectrum is not None:
            # Spectral flux (positive changes only)
            flux = np.sum(np.maximum(spectrum - prev_spectrum, 0))
            flux_ema = ema(flux_ema, flux, FLUX_ALPHA)

            now = time.time()

            # Kick detection
            if (
                flux_ema
                and flux > flux_ema * KICK_THRESHOLD
                and now - last_flash > FLASH_COOLDOWN
            ):
                # Intensity from bass strength
                intensity = clamp(bass_energy * 8, 0.1, 1.0)
                flash_keyboard(intensity)
                last_flash = now

        prev_spectrum = spectrum

# =========================
# Entry
# =========================
def main():
    print("[+] Starting TRUE kick-reactive lighting...")

    p = pyaudio.PyAudio()
    idx = get_blackhole_device_index(p)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=idx,
        frames_per_buffer=CHUNK,
    )

    try:
        runloop(stream)
    except KeyboardInterrupt:
        print("\n[X] Stopped")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
