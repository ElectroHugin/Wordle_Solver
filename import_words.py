# -*- coding: utf-8 -*-
"""Import a raw dictionary dump into a cleaned word list.

Usage:
    python import_words.py raw_dictionary.txt word_collections/german.txt

Normalizes to lowercase, strips CR/LF and whitespace, keeps only ASCII
alphabetic words of the target length, and removes duplicates.
"""

import argparse


def import_words(source, target, length=5):
    seen = set()
    words = []
    with open(source, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if len(word) == length and word.isascii() and word.isalpha():
                if word not in seen:
                    seen.add(word)
                    words.append(word)

    words.sort()
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(words) + "\n")
    return len(words)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="raw dictionary file (one word per line)")
    parser.add_argument("target", help="output word list file")
    parser.add_argument("--length", type=int, default=5, help="word length (default: 5)")
    args = parser.parse_args()

    count = import_words(args.source, args.target, args.length)
    print(f"Wrote {count} unique {args.length}-letter words to {args.target}")


if __name__ == "__main__":
    main()
