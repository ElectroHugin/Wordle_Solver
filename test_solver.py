# -*- coding: utf-8 -*-
"""Tests and self-play benchmark for the solver.

Run:  python test_solver.py
"""

import random

from solver import (WordleSolver, compute_pattern, filter_candidates,
                    GREEN, YELLOW, GRAY)
from wordlist import load_word_list, load_guess_pool


def test_patterns():
    """Duplicate-letter edge cases from real Wordle rules."""
    cases = [
        # guess, solution, expected
        ("crane", "crane", (GREEN,) * 5),
        ("aaaaa", "abbba", (GREEN, GRAY, GRAY, GRAY, GREEN)),
        # solution has one 'l'; first 'l' in guess is yellow, second gray
        ("llama", "could", (YELLOW, GRAY, GRAY, GRAY, GRAY)),
        # green consumes one 'e', the leading 'e' is yellow, trailing gray
        ("eerie", "tenet", (YELLOW, GREEN, GRAY, GRAY, GRAY)),
        # abide has only ONE 'e': first 'e' yellow, second gray; 'd' yellow
        ("speed", "abide", (GRAY, GRAY, YELLOW, GRAY, YELLOW)),
        ("speed", "erase", (YELLOW, GRAY, YELLOW, YELLOW, GRAY)),
        ("speed", "steal", (GREEN, GRAY, GREEN, GRAY, GRAY)),
        ("speed", "crepe", (GRAY, YELLOW, GREEN, YELLOW, GRAY)),
    ]
    for guess, solution, expected in cases:
        got = compute_pattern(guess, solution)
        assert got == expected, f"{guess} vs {solution}: {got} != {expected}"
    print("pattern tests: OK")


def test_filtering():
    words = ["crane", "crate", "crave", "brace", "trace"]
    pattern = compute_pattern("crane", "trace")
    remaining = filter_candidates(words, "crane", pattern)
    assert "trace" in remaining
    assert "crane" not in remaining
    # every survivor must reproduce the observed pattern
    for w in remaining:
        assert compute_pattern("crane", w) == pattern
    print("filtering tests: OK")


def self_play(lang, games=150, seed=42):
    """Simulate full games against random solutions; report guess counts."""
    words = load_word_list(lang)
    pool = load_guess_pool(lang)
    rng = random.Random(seed)
    solutions = rng.sample(words, games)

    total, fails, dist = 0, 0, {}
    for solution in solutions:
        solver = WordleSolver(words, lang, pool)
        for attempt in range(1, 11):
            guess = solver.suggest(top_n=1)[0][0]
            pattern = compute_pattern(guess, solution)
            if all(p == GREEN for p in pattern):
                total += attempt
                dist[attempt] = dist.get(attempt, 0) + 1
                if attempt > 6:
                    fails += 1
                break
            solver.apply_feedback(guess, pattern)
        else:
            raise AssertionError(f"did not solve {solution}")

    avg = total / games
    print(f"{lang}: avg {avg:.3f} guesses over {games} games, "
          f"failed (>6): {fails}, distribution: {dict(sorted(dist.items()))}")
    return avg


if __name__ == "__main__":
    test_patterns()
    test_filtering()
    self_play("german")
    self_play("english")
