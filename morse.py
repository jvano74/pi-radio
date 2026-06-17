import time
import os
import numpy as np
import pygame

# --- CONFIGURATION ---
TEXT_FILE = "message.txt"  # Path to your text file
INTRO_FILE = "intro.wav"  # Pre-recorded intro voice file
OUTRO_FILE = "outro.wav"  # Pre-recorded outro voice file

SAMPLE_RATE = 44100  # Audio sample rate (44.1kHz standard)
FREQUENCY = 800  # Pitch of the Morse tone in Hz
DOT_DURATION = 0.2  # Speed: Duration of a dot in seconds

# Calculate relative Morse timings
DASH_DURATION = DOT_DURATION * 3
SYMBOL_SPACE = DOT_DURATION
LETTER_SPACE = DOT_DURATION * 3
WORD_SPACE = DOT_DURATION * 7

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
    " ": " ",
}

# Initialize Pygame Mixer
pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)


def generate_beep_sound(duration):
    """Generates a raw sine wave array and converts it into a Pygame Sound."""
    num_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    wave = np.sin(2 * np.pi * FREQUENCY * t) * 32767
    wave = wave.astype(np.int16)
    return pygame.sndarray.make_sound(wave)


# Pre-generate Dot and Dash audio clips
dot_sound = generate_beep_sound(DOT_DURATION)
dash_sound = generate_beep_sound(DASH_DURATION)


def play_voice_file(file_path):
    """Loads and plays an external voice recording, waiting until it finishes."""
    if os.path.exists(file_path):
        print(f"Playing voice announcement: {file_path}")
        voice_sound = pygame.mixer.Sound(file_path)
        voice_sound.play()

        # Keep the script paused until the voice track finishes playing
        while pygame.mixer.get_busy():
            time.sleep(0.1)
    else:
        print(f"Warning: Voice file '{file_path}' not found. Skipping.")


def play_morse(text):
    """Processes text and plays it through the audio jack/HDMI."""
    cleaned_text = text.upper().strip()

    for word in cleaned_text.split("\n").split(" "):
        for letter in word:
            if letter not in MORSE_DICT:
                print(" [Unknown Character] ")
                time.sleep(WORD_SPACE)
            code = MORSE_DICT[letter]
            print(f"{letter}: {code}")

            for symbol in code:
                if symbol == ".":
                    dot_sound.play()
                    time.sleep(DOT_DURATION)
                elif symbol == "-":
                    dash_sound.play()
                    time.sleep(DASH_DURATION)
                time.sleep(SYMBOL_SPACE)

            time.sleep(LETTER_SPACE - SYMBOL_SPACE)

        print(" [Word Space] ")
        time.sleep(WORD_SPACE)


def main():
    if not os.path.exists(TEXT_FILE):
        with open(TEXT_FILE, "w") as f:
            f.write("Hello World")
        print(f"Created a sample text file at '{TEXT_FILE}'.")

    with open(TEXT_FILE, "r") as f:
        file_content = f.read()

    print("Starting broadcast audio sequence... Press Ctrl+C to stop.")
    try:
        # 1. Play "Message follows" voice clip
        play_voice_file(INTRO_FILE)
        time.sleep(1.5)  # Brief pause after voice before Morse starts

        # 2. Play the Morse code
        print("Playing Morse Code...")
        play_morse(file_content)
        time.sleep(1.5)  # Brief pause after Morse finishes

        # 3. Play "Message will repeat..." voice clip
        play_voice_file(OUTRO_FILE)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pygame.mixer.quit()


if __name__ == "__main__":
    main()
