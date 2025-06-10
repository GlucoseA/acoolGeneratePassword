# Password Generator

一个简单的密码生成器，支持命令行和图形界面两种方式。现在可以根据需要选择字符集、控制首字母大写，并将结果复制到剪切板。同时可为每个密码添加备注，统一保存到 `data_file/Token.txt` 中（保存的是密码的 SHA256 摘要）。

- `genarater.py`：在命令行交互式选择密码长度、字符类型等设置，并可选择是否复制到剪切板。
- `gui.py`：使用 Tkinter 提供同样的功能界面。
- 新增可选项：允许随机包含大写字母，独立于首字母大写选项。

每次生成的密码会与用户输入的备注一起追加到 `data_file/Token.txt` 中（保存的是 SHA256 摘要）。

程序会在用户主目录下的 `.acoolpwd/settings.json` 中保存上次使用的设置（密码长度、字符组合、是否保存及
日志目录等），下次启动时会自动加载，无需重复选择。


## 声明 / Disclaimer
此仓库的代码由 Codex 自动生成，仅供学习参考，请勿直接用于生产环境。

This repository contains code generated with Codex and should not be used in critical settings.

## 使用 PyInstaller 打包

本项目建议在与目标系统相同的环境中执行打包操作，避免跨平台生成可执行文件的兼容性问题。

### Windows 环境生成 `.exe`
1. **安装依赖**
   ```bash
   pip install pyinstaller pyperclip
   ```
   若使用了 `ttk` 或其他库，请一并安装。
2. **进入项目目录** 执行：
   ```bash
   pyinstaller --noconsole --onefile --add-data "resources;resources" --icon=resources/logo.png gui.py

   ```
   打包完成后 `dist/gui.exe` 即可在 Windows 上运行。

### Linux 环境生成可执行文件
1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller pyperclip
   ```
2. 在仓库根目录执行：
   ```bash
   pyinstaller --noconsole --onefile gui.py
   ```
   程序会生成 `dist/gui`，可在 Linux 终端运行。
