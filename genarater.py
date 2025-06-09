#!/usr/bin/env python3
"""Flexible password generator with optional clipboard support."""

import os
import secrets
import string
import json

try:
    import pyperclip
except ImportError:  # pragma: no cover - optional dependency
    pyperclip = None

SETTINGS_FILE = "settings.json"


def load_settings() -> dict:
    """Load configuration from SETTINGS_FILE if it exists."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict) -> None:
    """Write configuration to SETTINGS_FILE."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def ask_positive_int(prompt: str, default: int | None = None) -> int:
    """Repeatedly prompt until a positive integer is entered.
    If the user presses enter without input and a default is provided, the
    default value is returned."""
    while True:
        text = prompt
        if default is not None:
            text += f" (default {default}) "
        else:
            text += " "
        raw = input(text)
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a positive integer.")


def ask_yes_no(prompt: str, default: bool | None = None) -> bool:
    """Return True for 'y' and False for 'n'. Accept default on empty input."""
    while True:
        suffix = " (y/n) "
        if default is not None:
            suffix = f" (y/n, default {'y' if default else 'n'}) "
        answer = input(f"{prompt}{suffix}").strip().lower()
        if answer == "" and default is not None:
            return default
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
    return alphabet


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
    settings = load_settings()

    length = ask_positive_int(
        "Password length:", int(settings.get("length", 8))
    )
    include_letters = ask_yes_no(
        "Include letters", settings.get("letters", True)
    )
    include_digits = ask_yes_no(
        "Include digits", settings.get("digits", True)
    )
    include_special = ask_yes_no(
        "Include special characters", settings.get("special", False)
    )
    capitalize_first = ask_yes_no(
        "Capitalize first letter", settings.get("capital", False)
    )
    copy_clipboard = ask_yes_no(
        "Copy password to clipboard", settings.get("copy", False)
    )
    save_file = ask_yes_no(
        "Save password to log file", settings.get("save", True)
    )
    log_dir = settings.get("log_dir", "data_file")
    if save_file:
        custom = input(f"Log directory path (default {log_dir}): ").strip()
        if custom:
            log_dir = custom
    note = input("Note for this password: ")

    alphabet = build_alphabet(include_letters, include_digits, include_special)
    if not alphabet:
        print("No character types selected. Please enable at least one type.")
        return
    password = generate_password(length, alphabet, capitalize_first)

    if save_file:
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "Token.txt"), "a", encoding="utf-8") as f:
            f.write(f"{note}: {password}\n")

    if copy_clipboard:
        if pyperclip:
            pyperclip.copy(password)
            print("Password copied to clipboard.")
        else:
            print("pyperclip not installed; cannot copy to clipboard.")

    print("Generated password:", password)

    settings.update(
        {
            "length": length,
            "letters": include_letters,
            "digits": include_digits,
            "special": include_special,
            "capital": capitalize_first,
            "copy": copy_clipboard,
            "save": save_file,
            "log_dir": log_dir,
        }
    )
    save_settings(settings)


if __name__ == "__main__":
    main()
