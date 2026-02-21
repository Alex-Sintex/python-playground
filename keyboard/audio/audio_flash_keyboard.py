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

# Frequency bands
KICK_BAND = (20, 180)
SNARE_BAND = (180, 2500)
HAT_BAND = (2500, 8000)

# Adaptive thresholds
ENV_ALPHA = 0.2
FLUX_ALPHA = 0.3

KICK_GAIN = 10.0
SNARE_GAIN = 6.0
HAT_GAIN = 4.0

FLASH_COOLDOWN = 0.05
LATENCY_COMP = 0.02  # seconds

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

def flash_keyboard(intensity, duration):
    percent = int(clamp(intensity, 0.05, 1.0) * 100)
    duration = clamp(duration, 0.03, 0.2)

    run([
        BRIGHTNESSCTL_PATH,
        "-f", "1",
        f"{duration:.3f}",
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
    kick_sos = butter_bandpass(*KICK_BAND, RATE)
    snare_sos = butter_bandpass(*SNARE_BAND, RATE)
    hat_sos = butter_bandpass(*HAT_BAND, RATE)

    prev_spec_k = prev_spec_s = prev_spec_h = None
    flux_k = flux_s = flux_h = None

    env_k = env_s = env_h = None
    last_flash = 0.0

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, np.int16).astype(np.float32) / 32768.0

        # Band signals
        kick = scipy.signal.sosfilt(kick_sos, samples)
        snare = scipy.signal.sosfilt(snare_sos, samples)
        hat = scipy.signal.sosfilt(hat_sos, samples)

        # Energy envelopes
        env_k = ema(env_k, rms(kick), ENV_ALPHA)
        env_s = ema(env_s, rms(snare), ENV_ALPHA)
        env_h = ema(env_h, rms(hat), ENV_ALPHA)

        # Spectra
        spec_k = np.abs(np.fft.rfft(kick))
        spec_s = np.abs(np.fft.rfft(snare))
        spec_h = np.abs(np.fft.rfft(hat))

        now = time.time()

        # Flux detection
        def detect(prev, curr, flux_avg, gain):
            if prev is None:
                return curr, flux_avg, False, 0.0
            flux = np.sum(np.maximum(curr - prev, 0))
            flux_avg = ema(flux_avg, flux, FLUX_ALPHA)
            trigger = flux_avg and flux > flux_avg * 1.6
            intensity = clamp((flux / (flux_avg + 1e-9)) / gain, 0.1, 1.0)
            return curr, flux_avg, trigger, intensity

        prev_spec_k, flux_k, kick_hit, kick_i = detect(prev_spec_k, spec_k, flux_k, KICK_GAIN)
        prev_spec_s, flux_s, snare_hit, snare_i = detect(prev_spec_s, spec_s, flux_s, SNARE_GAIN)
        prev_spec_h, flux_h, hat_hit, hat_i = detect(prev_spec_h, spec_h, flux_h, HAT_GAIN)

        if now - last_flash < FLASH_COOLDOWN:
            continue

        # Priority: Kick > Snare > Hat
        if kick_hit:
            flash_keyboard(kick_i, 0.12)
            last_flash = now + LATENCY_COMP
        elif snare_hit:
            flash_keyboard(snare_i, 0.08)
            last_flash = now + LATENCY_COMP
        elif hat_hit:
            flash_keyboard(hat_i, 0.04)
            last_flash = now + LATENCY_COMP

# =========================
# Entry
# =========================
def main():
    print("[+] Starting adaptive white-only keyboard lighting...")

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
