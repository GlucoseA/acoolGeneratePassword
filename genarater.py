#!/usr/bin/env python3
"""
genarater.py - 命令行密码生成器（v2.0）

调用 generator.py 中的增强生成逻辑，支持：
- 密码 / 密码短语 / PIN 三种模式
- 排除相似字符、歧义字符
- 快速预设（高安全/标准/易记/PIN）
- 密码强度显示
"""

import os
import json
import hashlib

try:
    import pyperclip
except ImportError:
    pyperclip = None

from generator import (
    generate_password,
    generate_passphrase,
    generate_pin,
    calculate_strength,
    PRESETS,
)

SETTINGS_DIR = os.path.join(os.path.expanduser("~"), ".acoolpwd")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict) -> None:
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def ask_int(prompt: str, default: int, min_val: int = 1, max_val: int = 9999) -> int:
    while True:
        raw = input(f"{prompt} (默认 {default}): ").strip()
        if raw == "":
            return default
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  请输入 {min_val}~{max_val} 之间的整数。")
        except ValueError:
            print("  请输入整数。")


def ask_yn(prompt: str, default: bool) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} ({hint}): ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  请输入 y 或 n。")


def ask_choice(prompt: str, choices: list, default: int = 0) -> int:
    print(prompt)
    for i, c in enumerate(choices):
        marker = " [默认]" if i == default else ""
        print(f"  {i+1}. {c}{marker}")
    while True:
        raw = input(f"选择 (1-{len(choices)}, 默认 {default+1}): ").strip()
        if raw == "":
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return idx
        except ValueError:
            pass
        print(f"  请输入 1~{len(choices)} 之间的数字。")


def print_strength(password: str) -> None:
    info = calculate_strength(password)
    bars = "█" * (info["level"] + 1) + "░" * (5 - info["level"])
    print(f"  强度: [{bars}] {info['label']}  熵值: {info['entropy']} bits  破解时间: ~{info['crack_time']}")


def main() -> None:
    settings = load_settings()
    print("=" * 50)
    print("  acoolPwd 命令行密码生成器 v2.0")
    print("=" * 50)

    # 选择模式
    modes = ["随机密码", "密码短语（易记）", "数字PIN"]
    mode_idx = ask_choice("\n生成模式:", modes, default=0)

    password = ""

    if mode_idx == 0:
        # 随机密码模式
        print("\n快速预设（直接回车跳过，手动配置）:")
        preset_names = list(PRESETS.keys())
        preset_idx = ask_choice("", ["手动配置"] + preset_names, default=0)

        if preset_idx > 0:
            preset = PRESETS[preset_names[preset_idx - 1]]
        else:
            preset = {
                "length": int(settings.get("length", 16)),
                "use_lower": settings.get("use_lower", True),
                "use_upper": settings.get("use_upper", True),
                "use_digits": settings.get("use_digits", True),
                "use_special": settings.get("use_special", True),
                "exclude_similar": settings.get("exclude_similar", False),
                "exclude_ambiguous": settings.get("exclude_ambiguous", False),
            }

        length = ask_int("\n密码长度", preset["length"], 4, 128)
        use_lower = ask_yn("包含小写字母", preset.get("use_lower", True))
        use_upper = ask_yn("包含大写字母", preset.get("use_upper", True))
        use_digits = ask_yn("包含数字", preset.get("use_digits", True))
        use_special = ask_yn("包含特殊字符", preset.get("use_special", True))
        capitalize_first = ask_yn("首字母大写", settings.get("capitalize_first", False))
        exclude_similar = ask_yn("排除相似字符 (0/O/1/l/I)", preset.get("exclude_similar", False))
        exclude_ambiguous = ask_yn("排除歧义字符", preset.get("exclude_ambiguous", False))

        try:
            password = generate_password(
                length=length,
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_special=use_special,
                capitalize_first=capitalize_first,
                exclude_similar=exclude_similar,
                exclude_ambiguous=exclude_ambiguous,
            )
        except ValueError as e:
            print(f"\n错误: {e}")
            return

        settings.update({
            "length": length,
            "use_lower": use_lower,
            "use_upper": use_upper,
            "use_digits": use_digits,
            "use_special": use_special,
            "capitalize_first": capitalize_first,
            "exclude_similar": exclude_similar,
            "exclude_ambiguous": exclude_ambiguous,
        })

    elif mode_idx == 1:
        # 密码短语模式
        num_words = ask_int("单词数量", settings.get("pp_words", 4), 3, 8)
        separator = input(f"分隔符 (默认 -): ").strip() or "-"
        capitalize = ask_yn("首字母大写", True)
        add_number = ask_yn("末尾添加数字", True)
        password = generate_passphrase(num_words, separator, capitalize, add_number)
        settings.update({"pp_words": num_words})

    else:
        # PIN 模式
        pin_length = ask_int("PIN 位数", settings.get("pin_length", 6), 4, 12)
        password = generate_pin(pin_length)
        settings.update({"pin_length": pin_length})

    print(f"\n生成的密码: {password}")
    print_strength(password)

    # 复制到剪贴板
    copy_clipboard = ask_yn("\n复制到剪贴板", settings.get("copy", False))
    if copy_clipboard:
        if pyperclip:
            pyperclip.copy(password)
            print("  已复制到剪贴板。")
        else:
            print("  未安装 pyperclip，无法复制。请运行: pip install pyperclip")

    # 保存到日志文件（SHA256）
    save_file = ask_yn("保存 SHA256 摘要到日志文件", settings.get("save", False))
    if save_file:
        log_dir = settings.get("log_dir", "data_file")
        custom = input(f"日志目录 (默认 {log_dir}): ").strip()
        if custom:
            log_dir = custom
        note = input("备注: ")
        os.makedirs(log_dir, exist_ok=True)
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        with open(os.path.join(log_dir, "Token.txt"), "a", encoding="utf-8") as f:
            f.write(f"{note}: {digest}\n")
        print(f"  已保存到 {log_dir}/Token.txt")
        settings.update({"save": True, "log_dir": log_dir})

    save_settings(settings)
    print("\n设置已保存，下次启动将自动加载。")


if __name__ == "__main__":
    main()
