import keyboard
from subprocess import run
import time

BRIGHTNESSCTL_PATH = "/usr/local/bin/mac-brightnessctl"
COOLDOWN = 0.2
last_flash = 0

def flash_keyboard():
    print("[*] Flashing keyboard")
    run([BRIGHTNESSCTL_PATH, "-f", "1", "0.05", "100"])

def handle_keypress(e):
    global last_flash
    now = time.time()
    if now - last_flash > COOLDOWN:
        flash_keyboard()
        last_flash = now

keyboard.on_press(handle_keypress)

print("[+] Listening for key presses. Press Ctrl+C to stop.")
keyboard.wait()
