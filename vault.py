"""
vault.py - 加密密码库管理模块

使用 Fernet 对称加密 + PBKDF2HMAC 主密码派生，
将密码条目安全地存储在本地 JSON 文件中。
"""

import os
import json
import uuid
import base64
import hashlib
from datetime import datetime
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

VAULT_DIR = Path.home() / ".acoolpwd"
VAULT_FILE = VAULT_DIR / "vault.json"

CATEGORIES = ["全部", "工作", "个人", "金融", "社交", "购物", "娱乐", "其他"]


class VaultError(Exception):
    pass


def _derive_key(password: str, salt: bytes) -> bytes:
    """从主密码 + 盐派生 Fernet 密钥（PBKDF2HMAC）"""
    if not CRYPTO_AVAILABLE:
        raise VaultError("缺少 cryptography 库，请运行: pip install cryptography")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def _hash_master(password: str, salt: bytes) -> str:
    """对主密码做 PBKDF2 哈希，用于验证而不存储明文"""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 480000)
    return base64.b64encode(dk).decode("utf-8")


class PasswordVault:
    """加密密码库：管理所有密码条目的存储、加解密和 CRUD 操作"""

    def __init__(self):
        self._fernet = None
        self._data = None
        self._unlocked = False
        VAULT_DIR.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def is_initialized(self) -> bool:
        """是否已创建过密码库文件"""
        return VAULT_FILE.exists()

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked

    @property
    def entry_count(self) -> int:
        return len(self._data.get("entries", [])) if self._data else 0

    # ------------------------------------------------------------------
    # 初始化 / 解锁 / 锁定
    # ------------------------------------------------------------------

    def setup(self, master_password: str):
        """首次使用：用主密码初始化密码库"""
        salt = os.urandom(32)
        self._data = {
            "version": 1,
            "salt": base64.b64encode(salt).decode(),
            "master_hash": _hash_master(master_password, salt),
            "entries": [],
        }
        key = _derive_key(master_password, salt)
        self._fernet = Fernet(key)
        self._unlocked = True
        self._save()

    def unlock(self, master_password: str) -> bool:
        """用主密码解锁密码库，成功返回 True"""
        if not self.is_initialized:
            return False
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        salt = base64.b64decode(data["salt"])
        if _hash_master(master_password, salt) != data["master_hash"]:
            return False
        key = _derive_key(master_password, salt)
        self._fernet = Fernet(key)
        self._data = data
        self._unlocked = True
        return True

    def lock(self):
        """锁定密码库，清除内存中的密钥和数据"""
        self._fernet = None
        self._data = None
        self._unlocked = False

    # ------------------------------------------------------------------
    # 内部加解密
    # ------------------------------------------------------------------

    def _enc(self, text: str) -> str:
        return self._fernet.encrypt(text.encode("utf-8")).decode("utf-8")

    def _dec(self, token: str) -> str:
        return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")

    def _save(self):
        with open(VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # CRUD 操作
    # ------------------------------------------------------------------

    def add_entry(
        self,
        service: str,
        username: str,
        password: str,
        url: str = "",
        notes: str = "",
        category: str = "其他",
    ) -> str:
        """添加新密码条目，返回条目 ID"""
        entry_id = str(uuid.uuid4())
        self._data["entries"].append(
            {
                "id": entry_id,
                "service": service,
                "username": username,
                "password": self._enc(password),
                "url": url,
                "notes": self._enc(notes) if notes else "",
                "category": category,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "favorite": False,
            }
        )
        self._save()
        return entry_id

    def get_entries(self, category: str = None, search: str = None) -> list:
        """获取所有条目（已解密），支持分类过滤和关键词搜索"""
        result = []
        for e in self._data["entries"]:
            # 分类过滤
            if category and category not in ("全部", ""):
                if e.get("category") != category:
                    continue
            entry = dict(e)
            try:
                entry["password"] = self._dec(e["password"])
            except Exception:
                entry["password"] = "[解密失败]"
            try:
                entry["notes"] = self._dec(e["notes"]) if e.get("notes") else ""
            except Exception:
                entry["notes"] = ""
            # 关键词搜索
            if search:
                sl = search.lower()
                if not any(
                    sl in str(entry.get(f, "")).lower()
                    for f in ("service", "username", "url", "notes")
                ):
                    continue
            result.append(entry)
        # 收藏优先，再按服务名排序
        return sorted(
            result, key=lambda x: (not x.get("favorite", False), x.get("service", "").lower())
        )

    def get_entry(self, entry_id: str):
        """按 ID 获取单个条目（已解密）"""
        for e in self._data["entries"]:
            if e["id"] == entry_id:
                entry = dict(e)
                try:
                    entry["password"] = self._dec(e["password"])
                except Exception:
                    entry["password"] = "[解密失败]"
                try:
                    entry["notes"] = self._dec(e["notes"]) if e.get("notes") else ""
                except Exception:
                    entry["notes"] = ""
                return entry
        return None

    def update_entry(self, entry_id: str, **kwargs):
        """更新指定条目的字段"""
        for entry in self._data["entries"]:
            if entry["id"] == entry_id:
                if "password" in kwargs:
                    kwargs["password"] = self._enc(kwargs["password"])
                if "notes" in kwargs:
                    kwargs["notes"] = self._enc(kwargs["notes"]) if kwargs["notes"] else ""
                kwargs["updated_at"] = datetime.now().isoformat()
                entry.update(kwargs)
                break
        self._save()

    def delete_entry(self, entry_id: str):
        """删除指定条目"""
        self._data["entries"] = [
            e for e in self._data["entries"] if e["id"] != entry_id
        ]
        self._save()

    def toggle_favorite(self, entry_id: str):
        """切换收藏状态"""
        for e in self._data["entries"]:
            if e["id"] == entry_id:
                e["favorite"] = not e.get("favorite", False)
                break
        self._save()

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_json(self, filepath: str):
        """导出为 JSON 文件（含明文密码，请妥善保管）"""
        entries = self.get_entries()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

    def export_csv(self, filepath: str):
        """导出为 CSV 文件（含明文密码，请妥善保管）"""
        import csv

        entries = self.get_entries()
        fields = ["service", "username", "password", "url", "notes", "category", "created_at"]
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for e in entries:
                writer.writerow({k: e.get(k, "") for k in fields})

    # ------------------------------------------------------------------
    # 修改主密码
    # ------------------------------------------------------------------

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """修改主密码（会重新加密所有条目）"""
        salt = base64.b64decode(self._data["salt"])
        if _hash_master(old_password, salt) != self._data["master_hash"]:
            return False
        # 先解密所有条目
        plain_entries = self.get_entries()
        # 生成新盐和新密钥
        new_salt = os.urandom(32)
        new_key = _derive_key(new_password, new_salt)
        new_fernet = Fernet(new_key)
        # 用新密钥重新加密
        for entry in self._data["entries"]:
            plain = next((e for e in plain_entries if e["id"] == entry["id"]), None)
            if plain:
                entry["password"] = new_fernet.encrypt(plain["password"].encode()).decode()
                entry["notes"] = (
                    new_fernet.encrypt(plain["notes"].encode()).decode()
                    if plain.get("notes")
                    else ""
                )
        self._data["salt"] = base64.b64encode(new_salt).decode()
        self._data["master_hash"] = _hash_master(new_password, new_salt)
        self._fernet = new_fernet
        self._save()
        return True
