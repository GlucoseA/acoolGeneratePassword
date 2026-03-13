# acoolPwd - 密码管理器

> **v2.0 全面升级** — 在原密码生成器基础上，升级为功能完整的本地加密密码管理器。

## 主要功能

### 🔐 加密密码库
- 主密码保护，使用 **PBKDF2HMAC（480,000 次迭代）** 派生密钥
- 所有密码条目使用 **Fernet 对称加密** 存储（AES-128-CBC + HMAC）
- 密码库文件保存在 `~/.acoolpwd/vault.json`，主密码不存储，仅保存验证哈希

### ⚡ 增强密码生成
- **密码模式**：可选小写/大写/数字/特殊字符，支持排除相似字符（0/O/1/l/I）和歧义字符
- **密码短语模式**：基于词库生成易记的多词组合（如 `Tiger-Moon-River-42`）
- **PIN 码模式**：生成纯数字 PIN
- **快速预设**：高安全（20位）、标准（16位）、易记（12位无特殊字符）、PIN码
- 使用 Python `secrets` 模块，密码学安全的随机数

### 📊 密码强度评估
- 基于熵值（bits）的强度等级：极弱 / 弱 / 一般 / 强 / 很强 / 极强
- 估算 GPU 集群暴力破解所需时间（假设 1e11 次/秒）
- 可视化进度条（颜色随强度变化）

### 🗂️ 密码库管理
- 存储服务名、用户名、密码、网址、备注、分类
- 支持分类（工作/个人/金融/社交/购物/娱乐/其他）和全文搜索
- 收藏标记、排序
- 右键菜单：一键复制密码/用户名、编辑、删除

### 🎨 界面特性
- 现代侧栏导航 UI
- 深色 / 浅色主题切换
- 所有操作均有反馈提示

### 📤 数据管理
- 导出为 JSON 或 CSV（含明文密码，注意安全保存）
- 修改主密码（自动重新加密所有条目）

---

## 快速开始

### 安装依赖

```bash
pip install cryptography pyperclip
```

或直接使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 运行 GUI

```bash
python gui.py
```

首次运行会引导你创建主密码，之后每次启动需要输入主密码解锁。

### 运行命令行版本

```bash
python genarater.py
```

命令行版本提供基本的密码生成功能（无密码库）。

---

## 文件结构

```
acoolGeneratePassword/
├── gui.py           # 主 GUI 程序（v2.0 全面重写）
├── vault.py         # 加密密码库核心逻辑（新增）
├── generator.py     # 密码/密码短语/PIN 生成逻辑（新增）
├── genarater.py     # 命令行版本（原有，保留兼容）
├── requirements.txt # Python 依赖
├── gui.spec         # PyInstaller 打包配置
└── resources/
    └── logo.png     # 应用图标
```

**运行时生成的文件：**

| 文件 | 说明 |
|------|------|
| `~/.acoolpwd/vault.json` | 加密密码库 |
| `~/.acoolpwd/settings.json` | 应用设置（主题等） |

---

## 安全说明

- **主密码不可找回**：丢失主密码意味着无法解密密码库，请牢记或安全备份
- **本地存储**：所有数据仅存储在本机，不联网，不上传
- **导出文件包含明文密码**：请妥善保管导出的 JSON/CSV 文件

---

## 使用 PyInstaller 打包

### Windows

```bash
pip install pyinstaller cryptography pyperclip
pyinstaller --noconsole --onefile --add-data "resources;resources" --icon=resources/logo.png gui.py
```

### Linux

```bash
pip install pyinstaller cryptography pyperclip
pyinstaller --noconsole --onefile --add-data "resources:resources" gui.py
```

---

## 声明

本项目仅供学习参考，请勿将密码库文件存储于不可信的位置。
