import os
import warnings
import langdetect
import shutil
import signal
import subprocess
import threading
from TTS.api import TTS

# ---------------- CONFIG ----------------

voices_dir = "Voices/"
DEFAULT_VOICE = "Guada_youtuber_voice.wav"

warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

cached_tts_model = None
keyboard_flash_active = False
KEYBOARD_LIGHT_ENABLED = False  # 👈 USER CONTROL LIGHT

# ---------------- LANGUAGES ----------------

SUPPORTED_LANGUAGES = {
    "ar",
    "zh",
    "cs",
    "da",
    "nl",
    "en",
    "fi",
    "fr",
    "de",
    "el",
    "hi",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "th",
    "tr",
    "uk",
    "vi",
}

# ---------------- SAFE EXIT ----------------


def handle_ctrl_c(sig, frame):
    print("\n\nExiting safely. Goodbye 👋")
    exit(0)


signal.signal(signal.SIGINT, handle_ctrl_c)

# ---------------- HELPERS ----------------


def tts_cli_exists():
    return shutil.which("tts") is not None


def get_available_voices():
    if not os.path.exists(voices_dir):
        return []
    return [f for f in os.listdir(voices_dir) if f.endswith(".wav")]


def detect_language(text):
    try:
        lang = langdetect.detect(text)
        return lang if lang in SUPPORTED_LANGUAGES else "en"
    except:
        return "en"


def check_audio_file(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def read_text_input():
    print("\nInput method:")
    print("1 - Enter text manually")
    print("2 - Load text from .txt file")
    print("3 - Cancel")

    choice = input("> ").strip()

    if choice == "1":
        return input("Enter text: ").strip()

    if choice == "2":
        path = input("Enter .txt file path: ").strip()
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            print("Error reading file.")
            return None

    return None


# ---------------- KEYBOARD FLASH ----------------


def flash_keyboard_while_playing():
    global keyboard_flash_active
    while keyboard_flash_active:
        subprocess.call(
            ["mac-brightnessctl", "-f", "2", "0.25", "0.2"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def play_audio(path):
    global keyboard_flash_active

    if not check_audio_file(path):
        return

    if KEYBOARD_LIGHT_ENABLED:
        keyboard_flash_active = True
        threading.Thread(target=flash_keyboard_while_playing, daemon=True).start()

    subprocess.call(["afplay", path])

    keyboard_flash_active = False


def post_play_menu(audio_file):
    while True:
        print("\nOptions:")
        print("1 - Play again")
        print("2 - Return to main menu")

        if input("> ").strip() != "1":
            break

        play_audio(audio_file)


# ---------------- XTTS CACHE ----------------


def get_cached_xtts():
    global cached_tts_model
    if cached_tts_model is None:
        print("\nLoading XTTS model (one time only)...")
        cached_tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    return cached_tts_model


# ---------------- KEYBOARD MENU ----------------


def keyboard_light_menu():
    global KEYBOARD_LIGHT_ENABLED

    os.system("clear")
    print("Keyboard lighting while audio:\n")
    print("1 - ON")
    print("2 - OFF")

    choice = input("> ").strip()
    KEYBOARD_LIGHT_ENABLED = choice == "1"


# ---------------- MAIN ----------------


def synthesize_speech():
    while True:
        os.system("clear")

        wav_files = get_available_voices()
        cli_available = tts_cli_exists()

        print("\nAvailable voices:")
        for i, file in enumerate(wav_files, 1):
            print(f"{i} - {file}")

        keyboard_option = len(wav_files) + 1
        print(f"{keyboard_option} - Keyboard lighting settings")

        system_option = None
        if cli_available:
            system_option = keyboard_option + 1
            print(f"{system_option} - Use system tts command")

        choice = input(
            f"\nChoose a voice (1-{len(wav_files)})"
            f"\nOther options: {keyboard_option}"
            + (f", {system_option}" if cli_available else "")
            + f"\nPress Enter for default ({DEFAULT_VOICE}): "
        ).strip()

        # -------- KEYBOARD MENU --------
        if choice.isdigit() and int(choice) == keyboard_option:
            keyboard_light_menu()
            continue

        # -------- SYSTEM TTS --------
        if cli_available and choice.isdigit() and int(choice) == system_option:
            os.system("clear")

            text = read_text_input()
            if not text:
                continue

            language = detect_language(text)
            output_file = (
                input("\nOutput file (default: test.wav): ").strip() or "test.wav"
            )

            subprocess.call(
                [
                    "tts",
                    "--text",
                    text,
                    "--out_path",
                    output_file,
                    "--language_idx",
                    language,
                ]
            )

            if check_audio_file(output_file):
                print(f"\nAudio saved as '{output_file}' (system tts)")
                play_audio(output_file)
                post_play_menu(output_file)
            else:
                print("\nError generating audio")

            continue

        # -------- XTTS --------
        if choice.isdigit() and 1 <= int(choice) <= len(wav_files):
            speaker_wav = os.path.join(voices_dir, wav_files[int(choice) - 1])
        else:
            speaker_wav = os.path.join(voices_dir, DEFAULT_VOICE)

        os.system("clear")

        text = read_text_input()
        if not text:
            continue

        language = detect_language(text)
        print(f"\nDetected language: {language.upper()}")

        tts = get_cached_xtts()
        output_file = "test.wav"

        tts.tts_to_file(
            text=text, speaker_wav=speaker_wav, language=language, file_path=output_file
        )

        if check_audio_file(output_file):
            print(
                f"\nAudio saved as '{output_file}' using voice: {os.path.basename(speaker_wav)}"
            )
            play_audio(output_file)
            post_play_menu(output_file)
        else:
            print("\nError generating audio")


# ---------------- START ----------------

synthesize_speech()
