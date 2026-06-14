# 鼠标连点器 Auto Clicker

一个简单易用的 Windows 鼠标连点器，支持自定义快捷键、点击间隔、点击类型等。

## 功能

- **点击间隔**：1~99999 毫秒可调
- **点击类型**：单击 / 双击
- **鼠标按键**：左键 / 右键 / 中键
- **点击位置**：鼠标当前位置 / 指定屏幕坐标
- **重复模式**：无限点击 / 指定次数
- **全局快捷键**：默认 F6 启动/停止，支持自定义

## 使用

直接运行 `dist/鼠标连点器.exe`，无需安装 Python。

1. 设置点击参数（间隔、类型、按键等）
2. 按 **F6** 开始自动点击
3. 再按 **F6** 停止

## 源码运行

需要 Python 3.6+：

```bash
pip install -r requirements.txt
python main.py
```

## 打包

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "鼠标连点器" main.py
```
