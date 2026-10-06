"""Check whether a 4-letter input is a valid Scrabble word (ENABLE word list)."""

import sys
from pathlib import Path

WORD_LIST = Path(__file__).with_name("four_letter_words.txt")


def load_words(path=WORD_LIST):
    with open(path) as f:
        return {line.strip().lower() for line in f if line.strip()}


def is_real_word(text, words):
    """Return True if text is exactly 4 letters and appears in the word list."""
    text = text.strip().lower()
    if len(text) != 4 or not text.isalpha():
        raise ValueError("Input must be exactly 4 letters (a-z).")
    return text in words


def main():
    words = load_words()
    text = sys.argv[1] if len(sys.argv) > 1 else input("Enter a 4-letter word: ")
    try:
        if is_real_word(text, words):
            print(f"'{text.strip()}' is a real word.")
        else:
            print(f"'{text.strip()}' is NOT a real word.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
