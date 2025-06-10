#!/usr/bin/env python3
"""Flexible password generator with optional clipboard support."""

import os
import secrets
import string
import json
import math

try:
    import pyperclip
except ImportError:  # pragma: no cover - optional dependency
    pyperclip = None

SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".acoolpwd")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


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
        os.makedirs(SETTINGS_DIR, exist_ok=True)
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


def build_alphabet(include_lower: bool, include_upper: bool, include_digits: bool, include_special: bool) -> str:
    """Build a character set for the password."""
    alphabet = ""
    if include_lower:
        alphabet += string.ascii_lowercase
    if include_upper:
        alphabet += string.ascii_uppercase
    if include_digits:
        alphabet += string.digits
    if include_special:
        alphabet += string.punctuation
    return alphabet


def estimate_bruteforce_years(length: int, alphabet_size: int, guesses_per_second: float = 1e9) -> float:
    """Return estimated brute-force cracking time in years."""
    if length <= 0 or alphabet_size <= 1:
        return 0.0
    # entropy bits = length * log2(alphabet_size)
    entropy_bits = length * math.log2(alphabet_size)
    # time in seconds = 2**entropy_bits / guesses_per_second
    log2_seconds = entropy_bits - math.log2(guesses_per_second)
    seconds = 2 ** log2_seconds
    years = seconds / 31_557_600  # average seconds in a year
    return years


def generate_password(length: int,
                      include_lower: bool,
                      include_upper: bool,
                      include_digits: bool,
                      include_special: bool,
                      capitalize_first: bool) -> str:
    """Generate a random password ensuring each selected category appears."""
    if length <= 0:
        raise ValueError("length must be positive")

    alphabet = build_alphabet(include_lower, include_upper, include_digits, include_special)
    if not alphabet and not capitalize_first:
        raise ValueError("No character types selected")

    categories: list[str] = []
    if include_lower:
        categories.append(string.ascii_lowercase)
    if include_upper:
        categories.append(string.ascii_uppercase)
    if include_digits:
        categories.append(string.digits)
    if include_special:
        categories.append(string.punctuation)

    extra_upper = capitalize_first and not include_upper
    required_len = len(categories) + (1 if extra_upper else 0)
    if length < required_len:
        raise ValueError("length too short for selected categories")

    chars = [secrets.choice(cat) for cat in categories]
    if extra_upper:
        chars.append(secrets.choice(string.ascii_uppercase))

    chars += [secrets.choice(alphabet or string.ascii_lowercase) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)

    if capitalize_first:
        chars[0] = secrets.choice(string.ascii_uppercase)
        if not include_upper:
            for i in range(1, len(chars)):
                if chars[i] in string.ascii_uppercase:
                    chars[i] = secrets.choice(alphabet or string.ascii_lowercase)
                    break

    return "".join(chars)


def main() -> None:
    settings = load_settings()

    length = ask_positive_int(
        "Password length:", int(settings.get("length", 8))
    )
    include_letters = ask_yes_no(
        "Include lowercase letters", settings.get("letters", True)
    )
    include_upper = ask_yes_no(
        "Include uppercase letters", settings.get("upper", True)
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

    alphabet = build_alphabet(include_letters, include_upper, include_digits, include_special)
    if not alphabet:
        print("No character types selected. Please enable at least one type.")
        return
    password = generate_password(length,
                                 include_letters,
                                 include_upper,
                                 include_digits,
                                 include_special,
                                 capitalize_first)

    alphabet_set = set()
    if include_letters:
        alphabet_set.update(string.ascii_lowercase)
    if include_upper or capitalize_first:
        alphabet_set.update(string.ascii_uppercase)
    if include_digits:
        alphabet_set.update(string.digits)
    if include_special:
        alphabet_set.update(string.punctuation)
    strength_years = estimate_bruteforce_years(length, len(alphabet_set))

    if save_file:
        import hashlib
        os.makedirs(log_dir, exist_ok=True)
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        with open(os.path.join(log_dir, "Token.txt"), "a", encoding="utf-8") as f:
            f.write(f"{note}: {digest}\n")

    if copy_clipboard:
        if pyperclip:
            pyperclip.copy(password)
            print("Password copied to clipboard.")
        else:
            print("pyperclip not installed; cannot copy to clipboard.")

    print("Generated password:", password)
    print(f"Estimated brute-force time: ~{strength_years:.2e} years")

    settings.update(
        {
            "length": length,
            "letters": include_letters,
            "upper": include_upper,
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
