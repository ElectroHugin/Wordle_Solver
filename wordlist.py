# -*- coding: utf-8 -*-
"""Loading and validating word lists."""

import os

WORD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "word_collections")
LANGUAGES = ("english", "german")
WORD_LENGTH = 5


def load_word_list(lang, word_dir=WORD_DIR):
    """Load, normalize and deduplicate the word list for a language.

    Tolerates CRLF line endings, mixed case and stray whitespace, so raw
    dictionary dumps work as well as cleaned lists.
    """
    path = os.path.join(word_dir, lang + ".txt")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Word list not found: {path}")

    seen = set()
    words = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if len(word) == WORD_LENGTH and word.isascii() and word.isalpha():
                if word not in seen:
                    seen.add(word)
                    words.append(word)

    if not words:
        raise ValueError(f"No valid {WORD_LENGTH}-letter words in {path}")
    return words


def load_guess_pool(lang, word_dir=WORD_DIR):
    """Load the extended guess pool for a language, if available.

    A file `<lang>_guesses.txt` may contain valid guess words that are not
    possible solutions (e.g. the full Wordle guess list vs. the curated
    answer list). The solver uses these as probe words. Falls back to the
    solution list itself if no guess file exists. The result is guaranteed
    to be a superset of the solution list.
    """
    candidates = load_word_list(lang, word_dir)
    guess_path = os.path.join(word_dir, lang + "_guesses.txt")
    if not os.path.isfile(guess_path):
        return candidates

    seen = set(candidates)
    pool = list(candidates)
    with open(guess_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if len(word) == WORD_LENGTH and word.isascii() and word.isalpha():
                if word not in seen:
                    seen.add(word)
                    pool.append(word)
    return pool
