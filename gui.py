#!/usr/bin/env python3
"""Tkinter interface for the password generator."""

import os
import secrets
import string
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

try:
    import pyperclip
except ImportError:
    pyperclip = None


def copy_password() -> None:
    """Copy generated password to clipboard if available."""
    password = result_var.get()
    if not password:
        return
    if pyperclip:
        pyperclip.copy(password)
        messagebox.showinfo("已复制", "密码已复制到剪贴板")
    else:
        messagebox.showwarning("Unavailable", "pyperclip not installed.")

def generate_password() -> None:
    try:
        length = int(length_var.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a positive integer.")
        return

    # 构建字符集
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
    if capital_var.get() and password:
        password = password[0].upper() + password[1:]

    note = note_var.get()
    os.makedirs("data_file", exist_ok=True)
    with open("data_file/Token.txt", "a", encoding="utf-8") as f:
        f.write(f"{note}: {password}\n")

    result_var.set(password)

    if copy_var.get():
        copy_password()

root = tk.Tk()
root.title("Password Generator")
root.resizable(False, False)
try:
    root.iconphoto(False, tk.PhotoImage(file=os.path.join("resources", "logo.png")))
except Exception:
    pass

style = ttk.Style()
try:
    style.theme_use("vista")
except tk.TclError:
    pass
style.configure("TFrame", background="#F2F2F2")
style.configure("TLabel", background="#F2F2F2", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#F2F2F2")
style.configure("Result.TEntry", foreground="#e67e22", font=("Consolas", 12))

length_var = tk.StringVar(value="8")
letters_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
special_var = tk.BooleanVar(value=False)
capital_var = tk.BooleanVar(value=False)
copy_var = tk.BooleanVar(value=False)
note_var = tk.StringVar()
result_var = tk.StringVar()

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

header = ttk.Frame(main_frame)
header.pack(fill="x", pady=(0, 10))
logo_img = None
try:
    logo_img = tk.PhotoImage(file=os.path.join("resources", "logo.png"))
    logo_label = ttk.Label(header, image=logo_img)
    logo_label.image = logo_img
    logo_label.pack(side="left")
except Exception:
    logo_label = ttk.Label(header, text="")
    logo_label.pack(side="left")

title_label = ttk.Label(header, text="Password Generator", style="Header.TLabel")
title_label.pack(side="left", padx=(10, 0))

frame = ttk.LabelFrame(main_frame, text="设置", padding=10)
frame.pack(fill="x")

length_label = ttk.Label(frame, text="长度:")
length_label.grid(row=0, column=0, sticky="e")
length_entry = ttk.Entry(frame, textvariable=length_var, width=7)
length_entry.grid(row=0, column=1, sticky="w")
ttk.Label(frame, text="密码长度").grid(row=0, column=2, sticky="w", padx=(5,0))

letters_cb = ttk.Checkbutton(frame, text="字母", variable=letters_var)
letters_cb.grid(row=1, column=0, sticky="w")
digits_cb = ttk.Checkbutton(frame, text="数字", variable=digits_var)
digits_cb.grid(row=1, column=1, sticky="w")
special_cb = ttk.Checkbutton(frame, text="特殊字符", variable=special_var)
special_cb.grid(row=2, column=0, sticky="w")
capital_cb = ttk.Checkbutton(frame, text="首字母大写", variable=capital_var)
capital_cb.grid(row=2, column=1, sticky="w")
copy_cb = ttk.Checkbutton(frame, text="生成后自动复制", variable=copy_var)
copy_cb.grid(row=3, column=0, columnspan=2, sticky="w")

note_label = ttk.Label(frame, text="备注:")
note_label.grid(row=4, column=0, sticky="e")
note_entry = ttk.Entry(frame, textvariable=note_var, width=30)
note_entry.grid(row=4, column=1, sticky="w")
ttk.Label(frame, text="会记录在日志中").grid(row=4, column=2, sticky="w", padx=(5,0))

generate_button = ttk.Button(frame, text="生成密码", command=generate_password)
generate_button.grid(row=5, column=0, columnspan=3, pady=(5, 0))

result_frame = ttk.Frame(main_frame, padding=(0,10,0,0))
result_frame.pack(fill="x")
result_entry = ttk.Entry(result_frame, textvariable=result_var, state="readonly", style="Result.TEntry")
result_entry.pack(side="left", fill="x", expand=True)
copy_btn = ttk.Button(result_frame, text="复制", command=copy_password)
copy_btn.pack(side="left", padx=(5,0))

root.mainloop()
