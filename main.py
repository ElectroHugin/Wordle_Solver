# -*- coding: utf-8 -*-
"""Wordle Solver — interactive CLI.

Usage:
    python main.py                # interactive language selection
    python main.py -l german     # start directly in German
    python main.py -l english -n 8   # show 8 suggestions per round
"""

import argparse
import sys

from solver import WordleSolver, GREEN, YELLOW, GRAY, ENTROPY_LIMIT
from wordlist import load_word_list, load_guess_pool, LANGUAGES, WORD_LENGTH

# --- ANSI rendering ---------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
TILE = {
    GREEN: "\033[1;97;42m",   # white on green
    YELLOW: "\033[1;30;43m",  # black on yellow
    GRAY: "\033[1;97;100m",   # white on gray
}

FEEDBACK_CHARS = {
    "g": GREEN, "+": GREEN,
    "y": YELLOW, "=": YELLOW,
    "x": GRAY, "-": GRAY, "b": GRAY,
}


def render_guess(guess, pattern):
    """Render a guess as colored tiles, e.g. a Wordle row."""
    return "".join(f"{TILE[p]} {c.upper()} {RESET}" for c, p in zip(guess, pattern))


def parse_feedback(text):
    """Parse a feedback string like 'gyxxg' or '+=--+' into a pattern tuple."""
    text = text.strip().lower()
    if len(text) != WORD_LENGTH:
        return None
    try:
        return tuple(FEEDBACK_CHARS[c] for c in text)
    except KeyError:
        return None


HELP_TEXT = f"""
{BOLD}Commands{RESET}
  <feedback>      5 characters describing the colors of the last guess:
                    g or +  green  (correct position)
                    y or =  yellow (wrong position)
                    x or -  gray   (not in the word)
                  Example: gxyxg
  ggggg / win     mark the puzzle as solved
  <word>          you played a different 5-letter word — tell the solver
  list            show all remaining candidate words
  next            show the next batch of suggestions
  undo            revert the last feedback
  help            show this help
  quit            exit
"""


def choose_language():
    print("Choose a language / Sprache wählen:")
    for i, lang in enumerate(LANGUAGES, 1):
        print(f"  {i}) {lang}")
    while True:
        choice = input("> ").strip().lower()
        if choice in LANGUAGES:
            return choice
        if choice.isdigit() and 1 <= int(choice) <= len(LANGUAGES):
            return LANGUAGES[int(choice) - 1]
        print("Invalid choice, try again.")


def print_suggestions(solver, top_n):
    n = len(solver.candidates)
    if not solver.history:
        mode = "opening book"
    elif n > ENTROPY_LIMIT:
        mode = "frequency ranking"
    else:
        mode = "entropy ranking"
    print(f"\n{BOLD}{n}{RESET} candidate{'s' if n != 1 else ''} remaining "
          f"{DIM}({mode}){RESET}")

    suggestions = solver.suggest(top_n)
    for rank, (word, score, remaining) in enumerate(suggestions, 1):
        line = f"  {rank}) {BOLD}{word.upper()}{RESET}"
        if score is not None:
            line += f"  {DIM}{score:.2f} bits"
            if remaining is not None:
                line += f", ~{remaining:.0f} words left after guess"
            line += RESET
        print(line)
    return suggestions


def main():
    parser = argparse.ArgumentParser(description="Interactive Wordle solver.")
    parser.add_argument("-l", "--lang", choices=LANGUAGES,
                        help="word list language (default: ask)")
    parser.add_argument("-n", "--top", type=int, default=5,
                        help="number of suggestions per round (default: 5)")
    args = parser.parse_args()

    lang = args.lang or choose_language()
    words = load_word_list(lang)
    guess_pool = load_guess_pool(lang)
    solver = WordleSolver(words, lang, guess_pool)
    word_set = set(guess_pool)

    print(f"\n{BOLD}Wordle Solver{RESET} — {lang}, "
          f"{len(words)} solutions / {len(guess_pool)} guessable words loaded.")
    print(HELP_TEXT)

    current_guess = None
    while True:
        suggestions = print_suggestions(solver, args.top)
        if not solver.candidates:
            print("No candidates left — some feedback was inconsistent. "
                  "Use 'undo' to step back.")
        elif len(solver.candidates) == 1:
            print(f"\nThe word must be {render_guess(solver.candidates[0], (GREEN,) * WORD_LENGTH)} 🎉")

        if suggestions:
            current_guess = suggestions[0][0]
            print(f"\nPlay {BOLD}{current_guess.upper()}{RESET} "
                  f"(or pick another / type your own), then enter the feedback.")

        command = input("> ").strip().lower()

        if command in ("quit", "exit", "q"):
            break

        elif command in ("help", "h", "?"):
            print(HELP_TEXT)

        elif command == "undo":
            if solver.undo():
                print("Reverted last feedback.")
            else:
                print("Nothing to undo.")

        elif command == "list":
            for word in sorted(solver.candidates):
                print(" ", word)

        elif command in ("next", "n", ""):
            continue  # loop reprints suggestions; 'next' could page in future

        elif command in ("win", "ggggg", "+++++"):
            print(f"\n{render_guess(current_guess or 'great', (GREEN,) * WORD_LENGTH)}")
            print("Solved! 🎉")
            break

        elif command.isdigit() and suggestions and 1 <= int(command) <= len(suggestions):
            current_guess = suggestions[int(command) - 1][0]
            print(f"Selected {BOLD}{current_guess.upper()}{RESET}. Now enter the feedback.")
            feedback_input(solver, current_guess)

        elif parse_feedback(command):
            if current_guess is None:
                print("No active guess — type the word you played first.")
                continue
            pattern = parse_feedback(command)
            solver.apply_feedback(current_guess, pattern)
            print(render_guess(current_guess, pattern))
            if all(p == GREEN for p in pattern):
                print("Solved! 🎉")
                break

        elif len(command) == WORD_LENGTH and command.isalpha():
            if command not in word_set:
                print(f"'{command}' is not in the {lang} word list — using it anyway.")
            current_guess = command
            print(f"Guess set to {BOLD}{command.upper()}{RESET}. Now enter the feedback.")
            feedback_input(solver, current_guess)

        else:
            print("Unrecognized input. Type 'help' for commands.")


def feedback_input(solver, guess):
    """Prompt until valid feedback for `guess` is entered (or skipped)."""
    while True:
        raw = input(f"feedback for {guess.upper()} > ").strip().lower()
        if raw in ("", "skip", "cancel"):
            print("Skipped.")
            return
        pattern = parse_feedback(raw)
        if pattern is None:
            print("Invalid feedback — use 5 characters from g/y/x (or +/=/-).")
            continue
        solver.apply_feedback(guess, pattern)
        print(render_guess(guess, pattern))
        if all(p == GREEN for p in pattern):
            print("Solved! 🎉")
            sys.exit(0)
        return


if __name__ == "__main__":
    main()
