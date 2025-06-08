#!/usr/bin/env python3
"""Tkinter interface for the password generator."""

import os
import secrets
import string
import tkinter as tk
from tkinter import messagebox

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pyperclip = None


def generate_password() -> None:
    """Generate the password from the GUI selections."""
    try:
        length = int(length_var.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a positive integer.")
        return

    alphabet = ""
    if letters_var.get():
        alphabet += string.ascii_lowercase
    if digits_var.get():
        alphabet += string.digits
    if special_var.get():
        alphabet += string.punctuation
    if not alphabet:
        alphabet = string.digits

    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    if capital_var.get():
        password = secrets.choice(string.ascii_uppercase) + password[1:]

    os.makedirs("data_file", exist_ok=True)
    note = note_var.get()
    with open("data_file/Token.txt", "a", encoding="utf-8") as f:
        f.write(f"{note}: {password}\n")

    if copy_var.get():
        if pyperclip:
            pyperclip.copy(password)
        else:
            messagebox.showwarning("Unavailable", "pyperclip not installed.")

    result_var.set(password)


root = tk.Tk()
root.title("Password Generator")

length_var = tk.StringVar(value="8")
letters_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
special_var = tk.BooleanVar(value=False)
capital_var = tk.BooleanVar(value=False)
copy_var = tk.BooleanVar(value=False)
note_var = tk.StringVar()
result_var = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# length entry
length_label = tk.Label(frame, text="Length:")
length_label.grid(row=0, column=0, sticky="e")
length_entry = tk.Entry(frame, textvariable=length_var, width=5)
length_entry.grid(row=0, column=1, sticky="w")

# options
letters_cb = tk.Checkbutton(frame, text="Letters", variable=letters_var)
letters_cb.grid(row=1, column=0, sticky="w")
digits_cb = tk.Checkbutton(frame, text="Digits", variable=digits_var)
digits_cb.grid(row=1, column=1, sticky="w")
special_cb = tk.Checkbutton(frame, text="Special", variable=special_var)
special_cb.grid(row=2, column=0, sticky="w")
capital_cb = tk.Checkbutton(frame, text="Capitalize first", variable=capital_var)
capital_cb.grid(row=2, column=1, sticky="w")
copy_cb = tk.Checkbutton(frame, text="Copy to clipboard", variable=copy_var)
copy_cb.grid(row=3, column=0, columnspan=2, sticky="w")

note_label = tk.Label(frame, text="Note:")
note_label.grid(row=4, column=0, sticky="e")
note_entry = tk.Entry(frame, textvariable=note_var, width=30)
note_entry.grid(row=4, column=1, sticky="w")

generate_button = tk.Button(frame, text="Generate", command=generate_password)
generate_button.grid(row=5, column=0, columnspan=2, pady=(5, 0))

result_label = tk.Label(frame, textvariable=result_var, wraplength=400)
result_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))

root.mainloop()
