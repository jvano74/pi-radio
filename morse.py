import os
import time
import configparser
import argparse
import numpy as np
import pygame
import scipy.io.wavfile as wav

# --- GENERAL CONFIGURATION ---
SAMPLE_RATE = 44100
CONFIG_FILE = "config.txt"

# Morse Code Dictionary
MORSE_DICT = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ",": "--.. --",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
}

SPECIAL_CHARACTERS = {
    ".": "period",
    ",": "comma",
    "?": "question",
    "/": "slash",
    "-": "dash",
    "(": "open_paren",
    ")": "close_paren",
}


def get_code(letter, to_number=False, shift=0):
    if to_number:
        digit = ord(letter) - 64
        digit = (digit + shift - 1) % 26 + 1
        letter = f"{digit}"
    return SPECIAL_CHARACTERS.get(letter, letter)


# -------------------------------------------------------------------------
# GENERATION ENGINE (The "Init" Functionality)
# -------------------------------------------------------------------------


def generate_profile(profile_name, frequency=800, dot_duration=0.2):
    """
    Generates a full directory of .wav files for each Morse code character
    based on explicit filename map rules.
    """
    profile_dir = os.path.join("profiles", profile_name)
    if os.path.isdir(profile_dir):
        print(f"\nProfile '{profile_name}' already exists.")
        return

    print(f"\nInitializing and generating profile: '{profile_name}'...")

    os.makedirs(profile_dir, exist_ok=True)
    print(f"\nInitializing and generating profile: '{profile_name}'...")
    print(f"Settings: Pitch={frequency}Hz, Speed={dot_duration}s per dot")

    dash_duration = dot_duration * 3
    symbol_space_duration = dot_duration
    letter_space_duration = dot_duration * 3

    def make_tone_array(duration):
        """Helper to create a raw numpy sine wave array."""
        num_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        wave = np.sin(2 * np.pi * frequency * t) * 32767
        return wave.astype(np.int16)

    # Pre-build primitive building blocks
    dot_wave = make_tone_array(dot_duration)
    dash_wave = make_tone_array(dash_duration)
    symbol_space_wave = np.zeros(
        int(SAMPLE_RATE * symbol_space_duration), dtype=np.int16
    )
    letter_space_wave = np.zeros(
        int(SAMPLE_RATE * (letter_space_duration - symbol_space_duration)),
        dtype=np.int16,
    )

    # Generate explicit .wav files for each character using the file map dict
    for char, code in MORSE_DICT.items():
        char_wave_components = []

        for symbol in code:
            if symbol == ".":
                char_wave_components.append(dot_wave)
            elif symbol == "-":
                char_wave_components.append(dash_wave)
            char_wave_components.append(symbol_space_wave)

        char_wave_components.append(letter_space_wave)
        final_char_wave = np.concatenate(char_wave_components)

        code = get_code(char)
        file_path = os.path.join(profile_dir, f"{code}.wav")
        wav.write(file_path, SAMPLE_RATE, final_char_wave)

    # Build and save word space interval tracking audio file
    word_space_duration = dot_duration * 7
    word_space_wave = np.zeros(
        int(SAMPLE_RATE * (word_space_duration - letter_space_duration)), dtype=np.int16
    )
    wav.write(os.path.join(profile_dir, "word_space.wav"), SAMPLE_RATE, word_space_wave)

    print(f"Profile '{profile_name}' successfully compiled to disk.")


# -------------------------------------------------------------------------
# PLAYBACK ENGINE
# -------------------------------------------------------------------------


def play_voice_file(file_path):
    """Loads and plays an external voice recording, stalling until finished."""
    if os.path.exists(file_path):
        print(f"Playing voice announcement: {file_path}")
        voice_sound = pygame.mixer.Sound(file_path)
        voice_sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)
    else:
        print(f"Warning: Voice file '{file_path}' not found. Skipping.")


def play_text_from_profile(text, profile_name, to_number=False, shift=0):
    """Reads text string and matches characters directly via ."""
    profile_dir = os.path.join("profiles", profile_name)

    if not os.path.isdir(profile_dir):
        print(
            f"Error: The profile '{profile_name}' does not exist! Run generator first."
        )
        return

    cleaned_text = text.upper().strip()
    words = cleaned_text.split()

    word_space_path = os.path.join(profile_dir, "word_space.wav")
    word_space_sound = (
        pygame.mixer.Sound(word_space_path) if os.path.exists(word_space_path) else None
    )

    for word in words:
        if len(word) == 0:
            continue
        for letter in word:
            code = get_code(letter, to_number, shift)
            file_path = os.path.join(profile_dir, f"{code}.wav")
            if not os.path.exists(file_path):
                print(f"Warning: {profile_dir=} missing wav file for {code=}")
                continue

            print(f"{letter}: {code if to_number else MORSE_DICT.get(letter)}")
            char_sound = pygame.mixer.Sound(file_path)
            char_sound.play()

            while pygame.mixer.get_busy():
                time.sleep(0.01)

        print(" [Word Space] ")
        word_space_sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.01)


# -------------------------------------------------------------------------
# CONFIG ARCHITECTURE & MAIN EXECUTION
# -------------------------------------------------------------------------


def load_config_file():
    """Reads runtime variables dynamically from configuration file."""
    if not os.path.exists(CONFIG_FILE):
        config = configparser.ConfigParser()
        config["SETTINGS"] = {
            "ACTIVE_PROFILE": "fast_high_pitch",
            "INTRO_FILE": "intro.wav",
            "OUTRO_FILE": "outro.wav",
            "TEXT_FILE": "message.txt",
            "NUMBER_STATION": "False",
            "SHIFT": "0",
        }
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
        print(f"Created a default runtime layout tracking file at '{CONFIG_FILE}'.")

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config["SETTINGS"]


def parse_arguments():
    """Defines and parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Broadcast Morse and custom shifted ciphers."
    )

    parser.add_argument("-p", "--profile", type=str, help="Override ACTIVE_PROFILE")
    parser.add_argument("-i", "--intro", type=str, help="Override INTRO_FILE")
    parser.add_argument("-o", "--outro", type=str, help="Override OUTRO_FILE")
    parser.add_argument("-t", "--text", type=str, help="Override TEXT_FILE")

    # action="store_true" makes it a boolean flag. If present, it becomes True.
    parser.add_argument(
        "-n",
        "--number-station",
        action="store_true",
        help="Override NUMBER_STATION to True",
    )
    parser.add_argument("-s", "--shift", type=int, help="Override cipher SHIFT value")

    return parser.parse_args()


def main():
    # --- PROFILES SETUP ---
    generate_profile(profile_name="standard_12wpm", frequency=800, dot_duration=0.2)
    generate_profile(profile_name="fast_high_pitch", frequency=1000, dot_duration=0.08)
    generate_profile(profile_name="slow_heavy_tone", frequency=500, dot_duration=0.35)

    settings = load_config_file()
    args = parse_arguments()
    active_profile = (
        args.profile
        if args.profile
        else settings.get("ACTIVE_PROFILE", "fast_high_pitch")
    )
    intro_file = args.intro if args.intro else settings.get("INTRO_FILE", "intro.wav")
    outro_file = args.outro if args.outro else settings.get("OUTRO_FILE", "outro.wav")
    text_file = args.text if args.text else settings.get("TEXT_FILE", "message.txt")
    to_number = (
        args.number_station
        if args.number_station
        else settings.get("NUMBER_STATION", "False").lower() in ("true", "1", "yes")
    )
    shift = args.shift if args.shift is not None else int(settings.get("SHIFT", 0))

    # Verify input text file source
    if not os.path.exists(text_file):
        with open(text_file, "w") as f:
            f.write("Hello World")
        print(f"\nCreated sample payload message file at '{text_file}'.")

    with open(text_file, "r") as f:
        file_content = " ".join(f.read().split("\n"))

    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

    print(f"\nRuntime Settings Summary:")
    print(f" -> Profile: {active_profile}")
    print(f" -> Cipher Shift: {shift} (Convert to Number: {to_number})")
    print(f" -> Payload File: {text_file}")

    print(f"\nStarting broadcast sequence...")
    try:
        play_voice_file(intro_file)
        time.sleep(1.0)

        print(f"Streaming transmission from folder: 'profiles/{active_profile}/'...")
        play_text_from_profile(file_content, active_profile, to_number, shift)
        time.sleep(1.0)

        play_voice_file(outro_file)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pygame.mixer.quit()


if __name__ == "__main__":
    main()
