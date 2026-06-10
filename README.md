# Wordle Solver

An interactive, entropy-based Wordle solver for **German** and **English**.

## Usage

```bash
python main.py              # interactive language selection
python main.py -l german    # start directly in German
python main.py -l english -n 8   # show 8 suggestions per round
```

No dependencies — pure Python 3 standard library.

## How to play

1. The solver suggests words ranked by expected information gain (bits).
2. Play one of them in Wordle (or type the word you actually played).
3. Enter the feedback as 5 characters:
   - `g` or `+` — green (correct position)
   - `y` or `=` — yellow (in the word, wrong position)
   - `x` or `-` — gray (not in the word)

Example: `gxyxg`

Other commands: `list` (show remaining candidates), `undo` (revert last
feedback), `1`–`5` (pick a suggestion by number), `win`, `help`, `quit`.

## How it works

- **Pattern simulation instead of constraint tracking.** A word stays a
  candidate if guessing the played word against it would have produced
  exactly the observed feedback. This handles duplicate letters correctly
  by construction (the classic Wordle edge case).
- **Entropy ranking.** Each potential guess partitions the candidate set by
  the feedback it would produce; the guess with the highest partition
  entropy reduces the candidate set the most in expectation.
- **Probe words.** When few candidates remain (word families like
  `_ATEN`: raten / daten / gatte...), the solver also evaluates
  non-candidate words from the full guess pool that test several family
  letters at once — one probe instead of guessing candidates one by one.
  In the mid-game, a shortlist of probes built from the most *uncertain*
  letters (presence variance p·(1−p) across candidates) is added to the
  entropy ranking, so the solver can suggest a word made of fresh letters
  when that genuinely yields more information. Guesses that are possible
  solutions get a small score bonus (`CANDIDATE_BONUS`), since only they
  can win on the spot.
- **Separate solution and guess lists.** For English, candidates come from
  the official ~2,300 Wordle answers (`english.txt`) while probes may use
  the full ~20,000-word guess pool (`english_guesses.txt`).
- **Frequency fallback.** With very large candidate sets the O(n²) entropy
  step is skipped in favor of a positional letter-frequency heuristic.
- Opening guesses are precomputed (entropy-verified against the lists).

## Benchmark (self-play, random solutions)

| Language | Games | Avg. guesses | Failed (>6) |
|----------|-------|--------------|-------------|
| German   | 150   | 3.55         | 0           |
| English (official answers) | 150 | 3.44 | 0    |

Mid-game probing changes the average only marginally (within noise,
roughly ±0.03); the decisive improvements are the endgame family probes
(which eliminated all >6 failures) and entropy ranking itself.

Run it yourself: `python test_solver.py`

## Project structure

```
main.py            CLI (colors, undo, manual guesses)
solver.py          pattern logic, filtering, entropy/probe ranking
wordlist.py        word list loading & normalization
test_solver.py     unit tests + self-play benchmark
import_words.py    import raw dictionary dumps into cleaned lists
word_collections/  cleaned word lists; *_guesses.txt = extended guess pools
```

## Importing new word lists

```bash
python import_words.py raw_dump.txt word_collections/german.txt
```