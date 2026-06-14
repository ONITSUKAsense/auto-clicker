import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput import keyboard as pynput_keyboard
from pynput.mouse import Button as MouseButton, Controller as MouseController


class AutoClickerApp:
    """鼠标连点器 - GUI application with global hotkey support."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("鼠标连点器")
        self.root.resizable(False, False)

        self.mouse_ctrl = MouseController()

        # Clicking state
        self.clicking = False
        self.click_thread = None
        self._stop_event = threading.Event()

        # Settings vars
        self.interval_var = tk.IntVar(value=100)
        self.click_type_var = tk.StringVar(value="single")
        self.mouse_button_var = tk.StringVar(value="left")
        self.location_mode_var = tk.StringVar(value="current")
        self.coord_x_var = tk.StringVar(value="0")
        self.coord_y_var = tk.StringVar(value="0")
        self.repeat_mode_var = tk.StringVar(value="unlimited")
        self.repeat_count_var = tk.IntVar(value=10)
        self.status_var = tk.StringVar(value="就绪  |  快捷键: F6")

        # Hotkey config
        self.hotkey = pynput_keyboard.Key.f6
        self.hotkey_name = tk.StringVar(value="F6")
        self.listening_hotkey = False

        # Button text (updates dynamically)
        self.btn_text = tk.StringVar(value="开始点击 (F6)")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Start global keyboard listener
        self.keyboard_listener = pynput_keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def _build_ui(self):
        """Build the GUI layout."""
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        # Row 0 - Interval
        ttk.Label(main, text="点击间隔 (毫秒):").grid(row=0, column=0, sticky=tk.W, pady=4)
        interval_spin = ttk.Spinbox(
            main, from_=1, to=99999, textvariable=self.interval_var, width=8
        )
        interval_spin.grid(row=0, column=1, sticky=tk.W, padx=8, pady=4)

        # Row 1 - Click type
        ttk.Label(main, text="点击类型:").grid(row=1, column=0, sticky=tk.W, pady=4)
        type_frame = ttk.Frame(main)
        type_frame.grid(row=1, column=1, sticky=tk.W, padx=8, pady=4)
        ttk.Radiobutton(
            type_frame, text="单击", variable=self.click_type_var, value="single"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            type_frame, text="双击", variable=self.click_type_var, value="double"
        ).pack(side=tk.LEFT, padx=8)

        # Row 2 - Mouse button
        ttk.Label(main, text="鼠标按键:").grid(row=2, column=0, sticky=tk.W, pady=4)
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=2, column=1, sticky=tk.W, padx=8, pady=4)
        ttk.Radiobutton(
            btn_frame, text="左键", variable=self.mouse_button_var, value="left"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            btn_frame, text="右键", variable=self.mouse_button_var, value="right"
        ).pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(
            btn_frame, text="中键", variable=self.mouse_button_var, value="middle"
        ).pack(side=tk.LEFT)

        # Row 3 - Click location
        ttk.Label(main, text="点击位置:").grid(row=3, column=0, sticky=tk.W, pady=4)
        loc_frame = ttk.Frame(main)
        loc_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=8, pady=4)
        ttk.Radiobutton(
            loc_frame, text="鼠标当前位置", variable=self.location_mode_var, value="current"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            loc_frame, text="指定坐标:", variable=self.location_mode_var, value="fixed"
        ).pack(side=tk.LEFT, padx=8)

        # Row 4 - Coordinates
        coord_frame = ttk.Frame(main)
        coord_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=8, pady=2)
        ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT)
        x_entry = ttk.Entry(coord_frame, textvariable=self.coord_x_var, width=6)
        x_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT, padx=(8, 2))
        y_entry = ttk.Entry(coord_frame, textvariable=self.coord_y_var, width=6)
        y_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(
            coord_frame, text="获取当前", command=self._record_position
        ).pack(side=tk.LEFT, padx=8)

        # Row 5 - Repeat mode
        ttk.Label(main, text="重复模式:").grid(row=5, column=0, sticky=tk.W, pady=4)
        repeat_frame = ttk.Frame(main)
        repeat_frame.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=8, pady=4)
        ttk.Radiobutton(
            repeat_frame, text="无限", variable=self.repeat_mode_var, value="unlimited"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            repeat_frame, text="次数:", variable=self.repeat_mode_var, value="count"
        ).pack(side=tk.LEFT, padx=8)
        count_spin = ttk.Spinbox(
            repeat_frame, from_=1, to=99999, textvariable=self.repeat_count_var, width=6
        )
        count_spin.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(main, orient=tk.HORIZONTAL).grid(
            row=6, column=0, columnspan=3, sticky=tk.EW, pady=10
        )

        # Row 7 - Control buttons
        btn_frame2 = ttk.Frame(main)
        btn_frame2.grid(row=7, column=0, columnspan=3, pady=6)

        self.toggle_btn = ttk.Button(
            btn_frame2, textvariable=self.btn_text, command=self._toggle_clicking, width=20
        )
        self.toggle_btn.pack(side=tk.LEFT)

        ttk.Button(
            btn_frame2, text="修改快捷键", command=self._start_hotkey_listen
        ).pack(side=tk.LEFT, padx=8)

        # Row 8 - Status bar
        ttk.Label(main, textvariable=self.status_var, foreground="#555").grid(
            row=8, column=0, columnspan=3, pady=(8, 0)
        )

    # ── Hotkey handling ────────────────────────────────────────────

    def _on_key_press(self, key):
        """Global keyboard listener running in a background thread."""
        if self.listening_hotkey:
            self.root.after(0, self._set_hotkey, key)
            return

        if key == self.hotkey:
            self.root.after(0, self._toggle_clicking)

    def _start_hotkey_listen(self):
        """Enter hotkey-capture mode (next keypress becomes the hotkey)."""
        if self.listening_hotkey:
            return
        self.listening_hotkey = True
        self.status_var.set("请按下新的快捷键...")

    MODIFIER_KEYS = {
        pynput_keyboard.Key.ctrl, pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r,
        pynput_keyboard.Key.alt, pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r,
        pynput_keyboard.Key.shift, pynput_keyboard.Key.shift_l, pynput_keyboard.Key.shift_r,
        pynput_keyboard.Key.cmd, pynput_keyboard.Key.cmd_l, pynput_keyboard.Key.cmd_r,
    }

    KEY_DISPLAY_NAMES = {
        "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
        "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
        "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
        "insert": "Insert", "home": "Home", "delete": "Delete",
        "end": "End", "page_up": "PageUp", "page_down": "PageDown",
        "pause": "Pause", "print_screen": "PrintScreen",
        "scroll_lock": "ScrollLock", "caps_lock": "CapsLock",
        "tab": "Tab", "enter": "Enter", "space": "Space",
        "backspace": "BackSpace", "escape": "Esc",
    }

    def _set_hotkey(self, key):
        """Capture the pressed key as the new hotkey."""
        if not self.listening_hotkey:
            return
        self.listening_hotkey = False

        # Reject modifier-only keys
        if key in self.MODIFIER_KEYS:
            self.status_var.set(f"不能单独使用修饰键, 请重试  |  当前: {self.hotkey_name.get()}")
            return

        try:
            if hasattr(key, "char") and key.char is not None:
                name = key.char.upper()
                self.hotkey = key
            elif hasattr(key, "name") and key.name is not None:
                name = key.name
                self.hotkey = key
            else:
                self.status_var.set(f"按键无效, 请重试  |  当前: {self.hotkey_name.get()}")
                return

            display = self.KEY_DISPLAY_NAMES.get(name.lower(), name.upper())
            self.hotkey_name.set(display)

            # Update button text
            action = "停止" if self.clicking else "开始"
            self.btn_text.set(f"{action}点击 ({display})")
            self.status_var.set(f"快捷键已设置为: {display}")
        except Exception:
            self.status_var.set(f"快捷键设置失败  |  当前: {self.hotkey_name.get()}")

    # ── Click control ──────────────────────────────────────────────

    def _toggle_clicking(self):
        if self.clicking:
            self._stop_clicking()
        else:
            self._start_clicking()

    def _start_clicking(self):
        if self.clicking:
            return
        self.clicking = True
        self._stop_event.clear()
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()
        self.btn_text.set(f"停止点击 ({self.hotkey_name.get()})")
        self.status_var.set(f"正在点击...  |  快捷键: {self.hotkey_name.get()}")

    def _stop_clicking(self):
        if not self.clicking:
            return
        self.clicking = False
        self._stop_event.set()
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=2.0)
        self.click_thread = None
        self.btn_text.set(f"开始点击 ({self.hotkey_name.get()})")
        self.status_var.set(f"已停止  |  快捷键: {self.hotkey_name.get()}")

    def _click_loop(self):
        """The auto-click loop — runs in a daemon thread."""
        interval = max(self.interval_var.get(), 1) / 1000.0

        btn_map = {
            "left": MouseButton.left,
            "right": MouseButton.right,
            "middle": MouseButton.middle,
        }
        button = btn_map.get(self.mouse_button_var.get(), MouseButton.left)

        double_click = self.click_type_var.get() == "double"
        fixed_pos = self.location_mode_var.get() == "fixed"
        repeat_mode = self.repeat_mode_var.get()
        max_clicks = self.repeat_count_var.get() if repeat_mode == "count" else float("inf")

        click_count = 0

        if fixed_pos:
            try:
                target = (int(self.coord_x_var.get()), int(self.coord_y_var.get()))
            except ValueError:
                target = None

        while not self._stop_event.is_set() and click_count < max_clicks:
            pos = target if (fixed_pos and target is not None) else self.mouse_ctrl.position

            # Move mouse to target position (no-op if at current pos)
            if fixed_pos and target is not None:
                self.mouse_ctrl.position = pos

            self.mouse_ctrl.click(button)
            click_count += 1

            if double_click:
                time.sleep(0.03)
                self.mouse_ctrl.click(button)
                click_count += 1

            # Interval sleep (check stop event in short increments)
            remaining = interval
            while remaining > 0 and not self._stop_event.is_set():
                chunk = min(remaining, 0.05)
                time.sleep(chunk)
                remaining -= chunk

            # Periodic status update
            if click_count % 50 == 0 and not self._stop_event.is_set():
                self.root.after(0, self._update_status, click_count)

        # Loop ended
        self.clicking = False
        self.root.after(0, self._on_click_loop_end)

    def _update_status(self, count: int):
        if self.clicking:
            self.status_var.set(f"正在点击... ({count} 次)  |  快捷键: {self.hotkey_name.get()}")

    def _on_click_loop_end(self):
        self.btn_text.set(f"开始点击 ({self.hotkey_name.get()})")
        self.status_var.set(f"已完成  |  快捷键: {self.hotkey_name.get()}")
        self.click_thread = None

    # ── Utilities ──────────────────────────────────────────────────

    def _record_position(self):
        """Read the current mouse position into the X/Y fields."""
        x, y = self.mouse_ctrl.position
        self.coord_x_var.set(str(int(x)))
        self.coord_y_var.set(str(int(y)))

    def _on_closing(self):
        """Clean shutdown."""
        self._stop_clicking()
        if self.keyboard_listener and self.keyboard_listener.running:
            self.keyboard_listener.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoClickerApp()
    app.run()
