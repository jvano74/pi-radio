import os
import time
import numpy as np
import pygame
import scipy.io.wavfile as wav

# --- GENERAL CONFIGURATION ---
TEXT_FILE = "message.txt"
INTRO_FILE = "intro.wav"
OUTRO_FILE = "outro.wav"
SAMPLE_RATE = 44100

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
    ",": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
}

# -------------------------------------------------------------------------
# 1. GENERATION ENGINE (The "Init" Functionality)
# -------------------------------------------------------------------------


def generate_profile(profile_name, frequency=800, dot_duration=0.2):
    """
    Generates a full directory of .wav files for each Morse code character
    based on the specified frequency (pitch) and dot duration (speed).
    """
    profile_dir = os.path.join("profiles", profile_name)
    os.makedirs(profile_dir, exist_ok=True)
    print(f"\nInitializing and generating profile: '{profile_name}'...")
    print(f"Settings: Pitch={frequency}Hz, Speed={dot_duration}s per dot")

    # Internal timing math
    dash_duration = dot_duration * 3
    symbol_space_duration = dot_duration
    letter_space_duration = dot_duration * 3

    def make_tone_array(duration):
        """Helper to create a raw numpy sine wave array."""
        num_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        wave = np.sin(2 * np.pi * frequency * t) * 32767
        return wave.astype(np.int16)

    # Pre-build our primitive building blocks
    dot_wave = make_tone_array(dot_duration)
    dash_wave = make_tone_array(dash_duration)
    symbol_space_wave = np.zeros(
        int(SAMPLE_RATE * symbol_space_duration), dtype=np.int16
    )

    # The trailing gap added to the end of a complete letter's sound file
    # We subtract one symbol space because the last symbol element already included it
    letter_space_wave = np.zeros(
        int(SAMPLE_RATE * (letter_space_duration - symbol_space_duration)),
        dtype=np.int16,
    )

    # Generate a separate .wav file for every character mapping
    for char, code in MORSE_DICT.items():
        char_wave_components = []

        for symbol in code:
            if symbol == ".":
                char_wave_components.append(dot_wave)
            elif symbol == "-":
                char_wave_components.append(dash_wave)

            # Intracharacter pause (space between dots/dashes)
            char_wave_components.append(symbol_space_wave)

        # Append the letter-boundary padding at the very end
        char_wave_components.append(letter_space_wave)

        # Merge arrays into one contiguous audio track for this single letter
        final_char_wave = np.concatenate(char_wave_components)

        # Save file (Handle special naming for filesystem-sensitive characters)
        filename = f"char_{ord(char)}.wav"
        file_path = os.path.join(profile_dir, filename)
        wav.write(file_path, SAMPLE_RATE, final_char_wave)

    # Also build and save a standard word space interval file for convenience
    word_space_duration = dot_duration * 7
    # Subtract letter space duration since the last letter already padded the timeline
    word_space_wave = np.zeros(
        int(SAMPLE_RATE * (word_space_duration - letter_space_duration)), dtype=np.int16
    )
    wav.write(os.path.join(profile_dir, "word_space.wav"), SAMPLE_RATE, word_space_wave)

    print(f"Profile '{profile_name}' successfully compiled to disk.")


# -------------------------------------------------------------------------
# 2. PLAYBACK ENGINE
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


def play_morse_from_profile(text, profile_name):
    """Reads a text string and matches characters to pre-baked profile .wav files."""
    profile_dir = os.path.join("profiles", profile_name)

    if not os.path.isdir(profile_dir):
        print(
            f"Error: The profile '{profile_name}' does not exist! Run generator first."
        )
        return

    cleaned_text = text.upper().strip()
    words = cleaned_text.split()

    # Pre-load the word space audio tracking file
    word_space_path = os.path.join(profile_dir, "word_space.wav")
    word_space_sound = (
        pygame.mixer.Sound(word_space_path) if os.path.exists(word_space_path) else None
    )

    for i, word in enumerate(words):
        for letter in word:
            if letter not in MORSE_DICT:
                print(f" [Unknown Character skipped: {letter}] ")
                continue

            filename = f"char_{ord(letter)}.wav"
            file_path = os.path.join(profile_dir, filename)

            if os.path.exists(file_path):
                print(f"{letter}: {MORSE_DICT[letter]}")
                char_sound = pygame.mixer.Sound(file_path)
                char_sound.play()

                # Block execution while this specific letter file plays out entirely
                while pygame.mixer.get_busy():
                    time.sleep(0.01)
            else:
                print(f"Warning: Missing .wav file for character: {letter}")

        # Inject word gap audio file between word loops
        if i < len(words) - 1 and word_space_sound:
            print(" [Word Space] ")
            word_space_sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.01)


# -------------------------------------------------------------------------
# MAIN EXECUTION ROUTINE
# -------------------------------------------------------------------------


def main():
    # --- SETUP / INITIALIZATION PHASES (Run this when settings change) ---
    # Create distinct profiles to demonstrate different speeds/pitches
    generate_profile(profile_name="standard_12wpm", frequency=800, dot_duration=0.2)
    generate_profile(profile_name="fast_high_pitch", frequency=1000, dot_duration=0.08)
    generate_profile(profile_name="slow_heavy_tone", frequency=500, dot_duration=0.35)

    # --- SELECT YOUR ACTIVE RUNTIME PROFILE HERE ---
    ACTIVE_PROFILE = "fast_high_pitch"

    # Check text payload
    if not os.path.exists(TEXT_FILE):
        with open(TEXT_FILE, "w") as f:
            f.write("Hello World")
        print(f"\nCreated a sample text file at '{TEXT_FILE}'.")

    with open(TEXT_FILE, "r") as f:
        file_content = f.read()

    # Initialize Pygame audio playback architecture
    pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

    print(f"\nStarting broadcast sequence using profile [{ACTIVE_PROFILE}]...")
    try:
        # 1. Play "Message follows"
        play_voice_file(INTRO_FILE)
        time.sleep(1.0)

        # 2. Play the pre-baked character file sequences
        print(f"Streaming Morse Code from directory: 'profiles/{ACTIVE_PROFILE}/'...")
        play_morse_from_profile(file_content, ACTIVE_PROFILE)
        time.sleep(1.0)

        # 3. Play "Message will repeat..."
        play_voice_file(OUTRO_FILE)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pygame.mixer.quit()


if __name__ == "__main__":
    main()
