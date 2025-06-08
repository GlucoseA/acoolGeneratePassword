#!/usr/bin/env python3
"""Simple GUI for generating a password."""

import secrets
import os
import tkinter as tk
from tkinter import messagebox


def generate_password():
    """Generate password from user input and display it."""
    try:
        length = int(length_var.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a positive integer.")
        return

    os.makedirs("data_file", exist_ok=True)
    password = secrets.token_bytes(length).hex()
    with open("data_file/Token.txt", "w", encoding="utf-8") as f:
        f.write(password)
    result_var.set(password)


root = tk.Tk()
root.title("Password Generator")

# Input for number of bytes
length_var = tk.StringVar()
result_var = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

length_label = tk.Label(frame, text="Number of bytes:")
length_label.grid(row=0, column=0, sticky="e")

length_entry = tk.Entry(frame, textvariable=length_var)
length_entry.grid(row=0, column=1)

generate_button = tk.Button(frame, text="Generate", command=generate_password)
generate_button.grid(row=1, column=0, columnspan=2, pady=(5, 0))

result_label = tk.Label(frame, textvariable=result_var, wraplength=400)
result_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))

root.mainloop()
