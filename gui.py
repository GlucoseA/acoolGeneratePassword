#!/usr/bin/env python3
"""Tkinter interface for the password generator."""

import os
import secrets
import string
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

try:
    import pyperclip
except ImportError:
    pyperclip = None

SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".acoolpwd")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


def load_settings() -> dict:
    """Load configuration from SETTINGS_FILE if available."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict) -> None:
    """Persist settings to SETTINGS_FILE."""
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def copy_password() -> None:
    """Copy generated password to clipboard if available."""
    password = result_var.get()
    if not password:
        return
    if pyperclip:
        pyperclip.copy(password)
        status_var.set("密码已复制到剪贴板")
        root.after(2000, lambda: status_var.set(""))
    else:
        messagebox.showwarning("Unavailable", "pyperclip not installed.")

def generate_password() -> None:
    try:
        length = int(length_var.get())
        if length <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid input", "请输入一个正整数作为密码长度。")
        return

    # 构建字符集并确保类别出现
    alphabet = ""
    categories = []
    if letters_var.get():
        alphabet += string.ascii_lowercase
        categories.append(string.ascii_lowercase)
    if upper_var.get() or capital_var.get():
        alphabet += string.ascii_uppercase
        if upper_var.get():
            categories.append(string.ascii_uppercase)
    if digits_var.get():
        alphabet += string.digits
        categories.append(string.digits)
    if special_var.get():
        alphabet += string.punctuation
        categories.append(string.punctuation)
    if not alphabet:
        messagebox.showerror("Invalid selection", "请至少选择一种字符类型。")
        return
    if length < len(categories):
        messagebox.showerror("Invalid input", "长度不足以包含所有选中的类别。")
        return

    password_chars = [secrets.choice(c) for c in categories]
    password_chars += [secrets.choice(alphabet) for _ in range(length - len(password_chars))]
    secrets.SystemRandom().shuffle(password_chars)

    if capital_var.get():
        idx = secrets.randbelow(length)
        password_chars[idx] = secrets.choice(string.ascii_uppercase)

    password = ''.join(password_chars)

    note = note_var.get()
    if save_var.get():
        import hashlib
        os.makedirs(log_path_var.get(), exist_ok=True)
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        with open(os.path.join(log_path_var.get(), "Token.txt"), "a", encoding="utf-8") as f:
            f.write(f"{note}: {digest}\n")

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
    style.theme_use("vista")  # 在Windows上使用vista主题
except tk.TclError:
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

# 配置Checkbutton样式以显示√
style.configure("TCheckbutton", 
                font=("Segoe UI", 10))
style.configure("TFrame", background="#F2F2F2")
style.configure("TLabel", background="#F2F2F2", font=("Segoe UI", 10))
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#F2F2F2")
style.configure("Result.TEntry", foreground="#e67e22", font=("Consolas", 12))

settings = load_settings()

length_var = tk.StringVar(value=str(settings.get("length", 8)))
letters_var = tk.BooleanVar(value=settings.get("letters", True))
upper_var = tk.BooleanVar(value=settings.get("upper", True))
digits_var = tk.BooleanVar(value=settings.get("digits", True))
special_var = tk.BooleanVar(value=settings.get("special", False))
capital_var = tk.BooleanVar(value=settings.get("capital", False))
copy_var = tk.BooleanVar(value=settings.get("copy", False))
save_var = tk.BooleanVar(value=settings.get("save", True))
log_path_var = tk.StringVar(value=settings.get("log_dir", "data_file"))

note_var = tk.StringVar()
result_var = tk.StringVar()
status_var = tk.StringVar()

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

header = ttk.Frame(main_frame)
header.pack(fill="x", pady=(0, 10))
logo_img = None
try:
    logo_img = tk.PhotoImage(file=os.path.join("resources", "logo.png"))
    # 缩放为32x32像素
    w, h = logo_img.width(), logo_img.height()
    scale = max(1, max(w // 32, h // 32))
    if scale > 1:
        logo_img = logo_img.subsample(scale, scale)
    logo_label = ttk.Label(header, image=logo_img)
    # 用全局变量保存图片引用，防止被回收
    global _logo_img_ref
    _logo_img_ref = logo_img
    logo_label.pack(side="left")
except Exception:
    logo_label = ttk.Label(header, text="")
    logo_label.pack(side="left")

title_label = ttk.Label(header, text="Password Generator", style="Header.TLabel")
title_label.pack(side="left", padx=(10, 0))

frame = ttk.LabelFrame(main_frame, text="设置", padding=10)
frame.pack(fill="x")

length_label = ttk.Label(frame, text="密码长度")
length_label.grid(row=0, column=0, sticky="e", padx=(0,5))
length_entry = ttk.Entry(frame, textvariable=length_var, width=7)
length_entry.grid(row=0, column=1, sticky="w")

letters_cb = ttk.Checkbutton(frame, text="字母", variable=letters_var)
letters_cb.grid(row=1, column=0, sticky="w")
digits_cb = ttk.Checkbutton(frame, text="数字", variable=digits_var)
digits_cb.grid(row=1, column=1, sticky="w")
upper_cb = ttk.Checkbutton(frame, text="大写字母", variable=upper_var)
upper_cb.grid(row=1, column=2, sticky="w")
special_cb = ttk.Checkbutton(frame, text="特殊字符", variable=special_var)
special_cb.grid(row=2, column=0, sticky="w")
capital_cb = ttk.Checkbutton(frame, text="首字母大写", variable=capital_var)
capital_cb.grid(row=2, column=1, sticky="w")
copy_cb = ttk.Checkbutton(frame, text="生成后自动复制", variable=copy_var)
copy_cb.grid(row=3, column=0, columnspan=2, sticky="w")
save_cb = ttk.Checkbutton(frame, text="保存到文件", variable=save_var)
save_cb.grid(row=3, column=2, sticky="w")

note_label = ttk.Label(frame, text="备注:")
note_label.grid(row=4, column=0, sticky="e")
note_entry = ttk.Entry(frame, textvariable=note_var, width=30)
note_entry.grid(row=4, column=1, sticky="w")
ttk.Label(frame, text="备注将写入文件").grid(row=4, column=2, sticky="w", padx=(5,0))

path_label = ttk.Label(frame, text="日志目录")
path_label.grid(row=5, column=0, sticky="e")
path_entry = ttk.Entry(frame, textvariable=log_path_var, width=25)
path_entry.grid(row=5, column=1, sticky="w")
def choose_dir():
    path = filedialog.askdirectory(initialdir=log_path_var.get() or '.')
    if path:
        log_path_var.set(path)
choose_btn = ttk.Button(frame, text="选择...", command=choose_dir)
choose_btn.grid(row=5, column=2, sticky="w")

generate_button = ttk.Button(frame, text="生成密码", command=generate_password)
generate_button.grid(row=6, column=0, columnspan=3, pady=(5, 0))

result_frame = ttk.Frame(main_frame, padding=(0,10,0,0))
result_frame.pack(fill="x")
result_entry = ttk.Entry(result_frame, textvariable=result_var, state="readonly", style="Result.TEntry")
result_entry.pack(side="left", fill="x", expand=True)
copy_btn = ttk.Button(result_frame, text="复制", command=copy_password)
copy_btn.pack(side="left", padx=(5,0))
status_label = ttk.Label(main_frame, textvariable=status_var)
status_label.pack(fill="x")

# 监听字母复选框变化，控制首字母大写可用性
def on_letters_var_change(*args):
    if not (letters_var.get() or upper_var.get()):
        capital_var.set(False)
        capital_cb.state(["disabled"])
    else:
        capital_cb.state(["!disabled"])

letters_var.trace_add("write", lambda *args: on_letters_var_change())
upper_var.trace_add("write", lambda *args: on_letters_var_change())
# 初始化一次
on_letters_var_change()


def on_close() -> None:
    data = {
        "length": int(length_var.get() or 8),
        "letters": letters_var.get(),
        "upper": upper_var.get(),
        "digits": digits_var.get(),
        "special": special_var.get(),
        "capital": capital_var.get(),
        "copy": copy_var.get(),
        "save": save_var.get(),
        "log_dir": log_path_var.get(),
    }
    save_settings(data)
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
