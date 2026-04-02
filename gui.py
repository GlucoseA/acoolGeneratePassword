"""
gui.py - acoolPwd 密码管理器 v2.0

全面升级的图形界面密码管理器，功能包括：
- 加密密码库（Fernet + PBKDF2HMAC 主密码保护）
- 增强密码/密码短语/PIN 生成器
- 可视化密码强度评估
- 密码库管理（增删改查、搜索、分类、收藏）
- 深色/浅色主题切换
- 导出 JSON/CSV
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from generator import (
    generate_password, generate_passphrase, generate_pin,
    calculate_strength, PRESETS,
)
from vault import PasswordVault, CATEGORIES, CRYPTO_AVAILABLE


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------

THEMES = {
    "light": {
        "bg": "#f5f6fa",
        "sidebar": "#2c3e50",
        "sidebar_hover": "#34495e",
        "sidebar_active": "#3498db",
        "sidebar_text": "#ecf0f1",
        "card": "#ffffff",
        "text": "#2c3e50",
        "text2": "#7f8c8d",
        "accent": "#3498db",
        "accent2": "#2980b9",
        "border": "#dfe6e9",
        "danger": "#e74c3c",
        "success": "#27ae60",
        "warning": "#f39c12",
        "input_bg": "#ffffff",
        "pw_fg": "#e67e22",
    },
    "dark": {
        "bg": "#1a1a2e",
        "sidebar": "#16213e",
        "sidebar_hover": "#1a2a4a",
        "sidebar_active": "#e94560",
        "sidebar_text": "#e0e0e0",
        "card": "#16213e",
        "text": "#e0e0e0",
        "text2": "#a0a0b0",
        "accent": "#e94560",
        "accent2": "#c73652",
        "border": "#2a2a4a",
        "danger": "#e74c3c",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "input_bg": "#0f3460",
        "pw_fg": "#e94560",
    },
}

SETTINGS_FILE = Path.home() / ".acoolpwd" / "settings.json"


def _load_app_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_app_settings(data):
    try:
        SETTINGS_FILE.parent.mkdir(exist_ok=True)
        existing = _load_app_settings()
        existing.update(data)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------

class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("acoolPwd - 密码管理器")
        self.resizable(False, False)

        settings = _load_app_settings()
        self.current_theme = settings.get("theme", "light")
        self.vault = PasswordVault()

        w, h = 960, 660
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self._login_page = None
        self._main_page = None
        self._show_login()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.vault.lock()
        _save_app_settings({"theme": self.current_theme})
        self.destroy()

    def t(self):
        """Return current theme dict."""
        return THEMES[self.current_theme]

    def _show_login(self):
        if self._main_page:
            self._main_page.destroy()
            self._main_page = None
        self._login_page = LoginPage(self)
        self._login_page.pack(fill="both", expand=True)

    def on_login_success(self):
        if self._login_page:
            self._login_page.destroy()
            self._login_page = None
        self._main_page = MainPage(self)
        self._main_page.pack(fill="both", expand=True)

    def do_lock(self):
        self.vault.lock()
        self._show_login()

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        _save_app_settings({"theme": self.current_theme})
        if self._main_page:
            self._main_page.destroy()
            self._main_page = MainPage(self)
            self._main_page.pack(fill="both", expand=True)

