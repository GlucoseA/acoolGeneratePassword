# Password Generator

一个简单的密码生成器，支持命令行和图形界面两种方式。现在可以根据需要选择字符集、控制首字母大写，并将结果复制到剪切板。同时可为每个密码添加备注，统一保存到 `data_file/Token.txt` 中。

- `genarater.py`：在命令行交互式选择密码长度、字符类型等设置，并可选择是否复制到剪切板。
- `gui.py`：使用 Tkinter 提供同样的功能界面。

每次生成的密码会与用户输入的备注一起追加到 `data_file/Token.txt`。


## 声明 / Disclaimer
此仓库的代码由我通过 Codex 自动生成，仅供学习参考，请勿直接用于生产环境。

This repository contains code generated with Codex and should not be used in critical settings.

## 使用 PyInstaller 打包 Windows 可执行文件

以下步骤可以将 `gui.py` 打包成独立的 `.exe` 文件，适合在未安装 Python 的 Windows 电脑上直接运行。

1. **安装依赖**
   ```bash
   pip install pyinstaller pyperclip
   ```
   如果使用了 `ttk` 或其他库，请确保一并安装。

2. **进入项目目录**，执行打包命令：
   ```bash
   pyinstaller --noconsole --onefile \
       --add-data "resources;resources" \
       --icon=resources/logo.png gui.py
   ```
   - `--noconsole` 隐藏命令行黑窗口，使应用更像普通桌面程序。
   - `--onefile` 将所有内容打包成单个 `exe`，方便分发。
   - `--add-data` 用于包含程序运行所需的资源文件，例如图标。
   - `--icon` 指定自定义图标。请将自己的 `resources/logo.png` 放入仓库相同路径
     下，仓库中未包含此文件。

3. **查找结果**：打包完成后，在 `dist/` 目录下会生成 `gui.exe`。双击即可运行，无需额外安装 Python。

常见问题：
* 若 `pyinstaller` 提示缺少模块，请确保在打包前安装好相应依赖。
* 部分杀毒软件可能会误报新生成的 `.exe`，可尝试在白名单中添加或重新打包。


