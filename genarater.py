#!/usr/bin/env python3
"""Flexible password generator with optional clipboard support."""

import os
import secrets
import string

try:
    import pyperclip
except ImportError:  # pragma: no cover - optional dependency
    pyperclip = None


def ask_positive_int(prompt: str) -> int:
    """Repeatedly prompt until a positive integer is entered."""
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a positive integer.")


def ask_yes_no(prompt: str) -> bool:
    """Return True if user answers y/Y."""
    while True:
        answer = input(f"{prompt} (y/n) ").strip().lower()
        if answer in {"y", "n"}:
            return answer == "y"
        print("Please enter 'y' or 'n'.")


def build_alphabet(include_letters: bool, include_digits: bool, include_special: bool) -> str:
    """Build a character set for the password."""
    alphabet = ""
    if include_letters:
        alphabet += string.ascii_lowercase
    if include_digits:
        alphabet += string.digits
    if include_special:
        alphabet += string.punctuation
    return alphabet or string.digits


def generate_password(length: int, alphabet: str, capitalize_first: bool) -> str:
    """Generate a random password."""
    if length <= 0:
        raise ValueError("length must be positive")

    if capitalize_first:
        # 首位必须是大写字母
        chars = [secrets.choice(string.ascii_uppercase)]
        if length > 1:
            chars += [secrets.choice(alphabet) for _ in range(length - 1)]
    else:
        chars = [secrets.choice(alphabet) for _ in range(length)]
    return "".join(chars)


def main() -> None:
    length = ask_positive_int("Password length: ")
    include_letters = ask_yes_no("Include letters")
    include_digits = ask_yes_no("Include digits")
    include_special = ask_yes_no("Include special characters")
    capitalize_first = ask_yes_no("Capitalize first letter")
    copy_clipboard = ask_yes_no("Copy password to clipboard")
    note = input("Note for this password: ")

    alphabet = build_alphabet(include_letters, include_digits, include_special)
    password = generate_password(length, alphabet, capitalize_first)

    os.makedirs("data_file", exist_ok=True)
    with open("data_file/Token.txt", "a", encoding="utf-8") as f:
        f.write(f"{note}: {password}\n")

    if copy_clipboard:
        if pyperclip:
            pyperclip.copy(password)
            print("Password copied to clipboard.")
        else:
            print("pyperclip not installed; cannot copy to clipboard.")

    print("Generated password:", password)


if __name__ == "__main__":
    main()
