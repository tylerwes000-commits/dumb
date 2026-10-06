"""Check whether a 4-letter input is a valid Scrabble word (ENABLE word list)."""

import hashlib
import sys
from collections import deque
from pathlib import Path

WORD_LIST = Path(__file__).with_name("four_letter_words.txt")
NEIGHBOR_CACHE = Path(__file__).with_name("neighbors.txt")
PRIORITY_WORD = "poop"
PRIORITY_STEPS = Path(__file__).with_name(f"{PRIORITY_WORD}_steps.txt")


def load_words(path=WORD_LIST):
    with open(path) as f:
        return {line.strip().lower() for line in f if line.strip()}


def is_real_word(text, words):
    """Return True if text is exactly 4 letters and appears in the word list."""
    text = text.strip().lower()
    if len(text) != 4 or not text.isalpha():
        raise ValueError("Input must be exactly 4 letters (a-z).")
    return text in words


def one_letter_off(text, words):
    """Return every word in the list that differs from text by exactly one letter."""
    text = text.strip().lower()
    if len(text) != 4 or not text.isalpha():
        raise ValueError("Input must be exactly 4 letters (a-z).")
    neighbors = []
    for i in range(len(text)):
        for c in "abcdefghijklmnopqrstuvwxyz":
            if c != text[i]:
                candidate = text[:i] + c + text[i + 1:]
                if candidate in words:
                    neighbors.append(candidate)
    return sorted(neighbors)


def word_list_fingerprint(words):
    """Hash of the word list, stored in the cache header to detect a changed list."""
    return hashlib.sha256("\n".join(sorted(words)).encode()).hexdigest()


def build_neighbor_cache(words, path=NEIGHBOR_CACHE):
    """Precompute one_letter_off for every word that can reach the priority word and save it.

    Words with no chain of one-letter changes to the priority word are left out entirely.
    """
    full_map = {word: one_letter_off(word, words) for word in sorted(words)}
    reachable, _ = steps_from_priority(full_map)
    neighbor_map = {word: full_map[word] for word in sorted(reachable)}
    with open(path, "w") as f:
        f.write(f"#{word_list_fingerprint(words)}\n")
        for word, neighbors in neighbor_map.items():
            f.write(f"{word}:{','.join(neighbors)}\n")
    return neighbor_map


def load_neighbor_cache(words, path=NEIGHBOR_CACHE):
    """Load the saved neighbor map, rebuilding it if missing or out of date with the word list."""
    try:
        with open(path) as f:
            if f.readline().strip() == f"#{word_list_fingerprint(words)}":
                neighbor_map = {}
                for line in f:
                    word, _, neighbors = line.strip().partition(":")
                    neighbor_map[word] = neighbors.split(",") if neighbors else []
                return neighbor_map
    except OSError:
        pass
    return build_neighbor_cache(words, path)


def steps_from_priority(neighbor_map, priority=PRIORITY_WORD):
    """Breadth-first search out from the priority word.

    Returns (steps, parent): steps maps each reachable word to how many one-letter
    changes it is from the priority word; parent maps each word to the next word
    on a shortest path back toward it.
    """
    steps = {priority: 0}
    parent = {priority: None}
    queue = deque([priority])
    while queue:
        word = queue.popleft()
        for neighbor in neighbor_map.get(word, []):
            if neighbor not in steps:
                steps[neighbor] = steps[word] + 1
                parent[neighbor] = word
                queue.append(neighbor)
    return steps, parent


def save_priority_steps(steps, path=PRIORITY_STEPS):
    """Write the step count to the priority word for every word that can reach it."""
    with open(path, "w") as f:
        for word in sorted(steps):
            f.write(f"{word}:{steps[word]}\n")


def path_to_priority(text, neighbor_map, words, steps, parent):
    """Return the shortest list of words from text to the priority word, or None if unreachable."""
    text = text.strip().lower()
    if text in steps:
        start = text
        path = []
    else:
        # Not in the word list: step to its closest real neighbor first.
        reachable = [n for n in one_letter_off(text, words) if n in steps]
        if not reachable:
            return None
        start = min(reachable, key=lambda n: (steps[n], n))
        path = [text]
    while start is not None:
        path.append(start)
        start = parent[start]
    return path


def main():
    words = load_words()
    neighbor_map = load_neighbor_cache(words)
    text = sys.argv[1] if len(sys.argv) > 1 else input("Enter a 4-letter word: ")
    if text.strip().lower() == "--all":
        steps, _ = steps_from_priority(neighbor_map)
        save_priority_steps(steps)
        print(f"Saved step counts for {len(steps)} words to {PRIORITY_STEPS.name}")
        return
    try:
        is_real = is_real_word(text, words)
        steps, parent = steps_from_priority(neighbor_map)
        path = path_to_priority(text, neighbor_map, words, steps, parent)
        if path is None:
            print(f"'{text.strip()}' can't reach '{PRIORITY_WORD}'.")
        else:
            print(f"'{text.strip()}' is {len(path) - 1} step(s) from '{PRIORITY_WORD}': {' -> '.join(path)}")
        if is_real:
            print(f"'{text.strip()}' is a real word.")
        else:
            print(f"'{text.strip()}' is NOT a real word.")
        word = text.strip().lower()
        neighbors = neighbor_map[word] if word in neighbor_map else one_letter_off(word, words)
        print(f"Words one letter off: {', '.join(neighbors) if neighbors else '(none)'}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
