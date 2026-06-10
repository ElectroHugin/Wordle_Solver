# -*- coding: utf-8 -*-
"""Core solving logic: feedback patterns, candidate filtering, entropy ranking.

The solver never tracks green/yellow/gray constraints separately. Instead it
simulates: a word stays a candidate if guessing `guess` against it would have
produced exactly the observed feedback pattern. This handles all duplicate
letter edge cases correctly by construction.
"""

import math
from collections import Counter
from functools import lru_cache

GREEN, YELLOW, GRAY = 2, 1, 0

# If more candidates than this remain, skip the O(n^2) entropy computation
# and fall back to a positional letter-frequency heuristic.
ENTROPY_LIMIT = 800

# Strong opening guesses per language (verified against the word lists).
# Computing the optimal opener via entropy over the full list is O(n^2)
# and too slow to do at startup, so these are precomputed/known-good.
OPENERS = {
    "english": ["tarse", "soare", "roate", "raise", "salet"],
    "german": ["rates", "tarne", "raten", "taler", "reist"],
}


@lru_cache(maxsize=1_000_000)
def compute_pattern(guess, solution):
    """Return the Wordle feedback for `guess` against `solution`.

    Result is a tuple of GREEN/YELLOW/GRAY per position, with correct
    duplicate handling (two-pass: greens first, then yellows limited by
    remaining letter counts). Cached because the same (guess, solution)
    pairs recur constantly during entropy ranking.
    """
    pattern = [GRAY] * len(guess)
    remaining = {}

    for i, g in enumerate(guess):
        s = solution[i]
        if g == s:
            pattern[i] = GREEN
        else:
            remaining[s] = remaining.get(s, 0) + 1

    for i, g in enumerate(guess):
        if pattern[i] == GRAY:
            count = remaining.get(g, 0)
            if count:
                pattern[i] = YELLOW
                remaining[g] = count - 1

    return tuple(pattern)


def filter_candidates(candidates, guess, pattern):
    """Keep only words that would have produced `pattern` for `guess`."""
    return [w for w in candidates if compute_pattern(guess, w) == pattern]


# When few candidates remain, also evaluate non-candidate "probe" words from
# the full list. A probe cannot win immediately, but it can discriminate
# between word families (e.g. _ATEN: raten/daten/laten/...) in one guess
# instead of trying them one by one.
PROBE_LIMIT = 30

# Score bonus (in bits) for guesses that are themselves possible solutions.
# A candidate guess can win immediately, a probe never can; without this,
# the greedy entropy choice slightly over-favors probes. Benchmarked best
# around 0.1 (German, 450 games: 3.62 -> 3.60 avg guesses).
CANDIDATE_BONUS = 0.1


def entropy_ranking(candidates, guess_pool=None, top_n=5, candidate_bonus=0.0):
    """Rank guesses by expected information gain (entropy) over `candidates`.

    `guess_pool` defaults to the candidates themselves; pass a larger pool to
    include probe words. For each guess, partition the candidate set by the
    feedback pattern it would produce; the entropy of that partition is the
    expected number of bits the guess yields. Higher is better.

    Returns a list of (word, entropy_bits, expected_remaining) tuples.
    Ties (within rounding) are broken in favor of actual candidates, since
    only those can win the game on the spot.
    """
    if guess_pool is None:
        guess_pool = candidates
    candidate_set = set(candidates)
    n = len(candidates)

    results = []
    for guess in guess_pool:
        buckets = Counter(compute_pattern(guess, sol) for sol in candidates)
        entropy = 0.0
        expected_remaining = 0.0
        for size in buckets.values():
            p = size / n
            entropy -= p * math.log2(p)
            expected_remaining += p * size
        if candidate_bonus and guess in candidate_set:
            # A candidate guess has a 1/n chance of winning immediately —
            # a probe never does. Reward that in the score.
            entropy += candidate_bonus
        results.append((guess, entropy, expected_remaining))

    results.sort(key=lambda t: (-round(t[1], 6),
                                t[0] not in candidate_set,
                                t[2]))
    return results[:top_n]


def probe_shortlist(candidates, guess_pool, k=200):
    """Select probe words that test the most *uncertain* letters.

    A letter present in fraction p of the candidates contributes p*(1-p)
    (its variance) — maximal for letters in ~half the candidates, zero for
    letters already known: confirmed letters have p≈1, eliminated letters
    p=0. So this naturally favors words built from untried letters without
    any explicit constraint tracking. Repeated letters count once.
    """
    n = len(candidates)
    presence = Counter()
    for word in candidates:
        for letter in set(word):
            presence[letter] += 1
    info = {letter: (c / n) * (1.0 - c / n) for letter, c in presence.items()}

    scored = sorted(guess_pool,
                    key=lambda w: -sum(info.get(l, 0.0) for l in set(w)))
    return scored[:k]


def frequency_ranking(candidates, top_n=5):

    """Fast heuristic ranking by positional letter frequency.

    Used when the candidate set is too large for entropy. Scores each word
    by how common its letters are at their positions across all candidates;
    repeated letters in a word only count once (they add less information).
    """
    length = len(candidates[0])
    pos_freq = [Counter() for _ in range(length)]
    for word in candidates:
        for i, letter in enumerate(word):
            pos_freq[i][letter] += 1

    n = len(candidates)
    results = []
    for word in candidates:
        seen = set()
        score = 0.0
        for i, letter in enumerate(word):
            value = pos_freq[i][letter] / n
            if letter in seen:
                value /= 5.0  # penalize duplicate letters
            score += value
            seen.add(letter)
        results.append((word, score, None))

    results.sort(key=lambda t: -t[1])
    return results[:top_n]


class WordleSolver:
    """Stateful solver: feed it (guess, pattern) pairs, ask for suggestions."""

    def __init__(self, word_list, lang, guess_pool=None):
        self.all_words = list(word_list)          # possible solutions
        self.guess_pool = list(guess_pool) if guess_pool else self.all_words
        self.lang = lang
        self.candidates = list(word_list)
        self.history = []  # list of (guess, pattern, candidates_before)

    def suggest(self, top_n=5):
        """Return ranked suggestions as (word, score, expected_remaining)."""
        n = len(self.candidates)
        if n == 0:
            return []
        if n <= 2:
            return [(w, None, None) for w in self.candidates]
        if not self.history:
            pool = set(self.guess_pool)
            openers = [w for w in OPENERS.get(self.lang, []) if w in pool]
            if openers:
                return [(w, None, None) for w in openers[:top_n]]
        if n > ENTROPY_LIMIT:
            return frequency_ranking(self.candidates, top_n)
        if n <= PROBE_LIMIT:
            # Small candidate set: evaluate the entire guess pool as probes —
            # they may split word families much better than any candidate.
            return entropy_ranking(self.candidates, self.guess_pool, top_n,
                                   candidate_bonus=CANDIDATE_BONUS)
        # Mid-range (typically the 2nd/3rd guess): candidates plus a
        # shortlist of probe words covering the most uncertain letters.
        probes = probe_shortlist(self.candidates, self.guess_pool)
        return entropy_ranking(self.candidates, self.candidates + probes,
                               top_n, candidate_bonus=CANDIDATE_BONUS)

    def apply_feedback(self, guess, pattern):
        """Apply a guess and its observed pattern; shrinks the candidate set."""
        self.history.append((guess, pattern, self.candidates))
        self.candidates = filter_candidates(self.candidates, guess, pattern)

    def undo(self):
        """Revert the last apply_feedback call. Returns True on success."""
        if not self.history:
            return False
        _, _, previous = self.history.pop()
        self.candidates = previous
        return True

    @property
    def solved(self):
        return self.history and all(p == GREEN for p in self.history[-1][1])
