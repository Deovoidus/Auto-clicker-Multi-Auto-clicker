import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import time
import keyboard
import json
import os


class AutoClicker:
    SETTINGS_FILE = "auto_clicker_settings.json"
    DEFAULT_INTERVAL_MS = 100
    DEFAULT_KEYBIND = 'F6'
    DEFAULT_CLICK_TYPE = 'left'
    DEFAULT_CLICK_MODE = 'single'
    DEFAULT_COORDINATES = False
    DEFAULT_UNTIL_STOPPED = True
    DEFAULT_SPECIFIC_CLICKS = 10
    DEFAULT_ALWAYS_ON_TOP = False
    DEFAULT_BUTTON_WIDTH = 20
    DEFAULT_BUTTON_HEIGHT = 2

    def __init__(self, root):
        self.root = root
        self.root.title("Deo Clicker")
        
        self.interval_ms = tk.IntVar(value=self.DEFAULT_INTERVAL_MS)
        self.interval_s = tk.IntVar(value=0)
        self.interval_m = tk.IntVar(value=0)
        self.interval_h = tk.IntVar(value=0)
        self.keybind = tk.StringVar(value=self.DEFAULT_KEYBIND)
        self.click_type = tk.StringVar(value=self.DEFAULT_CLICK_TYPE)
        self.click_mode = tk.StringVar(value=self.DEFAULT_CLICK_MODE)
        self.click_coordinates = tk.BooleanVar(value=self.DEFAULT_COORDINATES)
        self.coordinates = []
        self.click_until_stopped = tk.BooleanVar(value=self.DEFAULT_UNTIL_STOPPED)
        self.specific_clicks = tk.IntVar(value=self.DEFAULT_SPECIFIC_CLICKS)
        self.always_on_top = tk.BooleanVar(value=self.DEFAULT_ALWAYS_ON_TOP)
        self.button_width = tk.IntVar(value=self.DEFAULT_BUTTON_WIDTH)
        self.button_height = tk.IntVar(value=self.DEFAULT_BUTTON_HEIGHT)
        self.running = False

        self.load_settings()
        self.create_widgets()
        self.setup_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Interval label and input
        interval_frame = ttk.LabelFrame(main_frame, text="Interval Between Clicks", padding="10")
        interval_frame.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.W, tk.E))
        self.create_interval_widgets(interval_frame)

        # Mouse options
        mouse_options_frame = ttk.LabelFrame(main_frame, text="Mouse Options", padding="10")
        mouse_options_frame.grid(column=0, row=1, padx=10, pady=10, sticky=(tk.W, tk.E))
        self.create_mouse_options_widgets(mouse_options_frame)

        # Coordinates
        coordinates_frame = ttk.LabelFrame(main_frame, text="Coordinates", padding="10")
        coordinates_frame.grid(column=0, row=2, padx=10, pady=10, sticky=(tk.W, tk.E))
        self.create_coordinates_widgets(coordinates_frame)

        # Buttons
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(column=0, row=3, padx=10, pady=10, sticky=(tk.W, tk.E))
        self.create_button_widgets(button_frame)

    def create_interval_widgets(self, frame):
        ttk.Label(frame, text="Hours:").grid(column=0, row=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.interval_h, width=5).grid(column=1, row=0, padx=5, pady=5)
        ttk.Label(frame, text="Minutes:").grid(column=2, row=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.interval_m, width=5).grid(column=3, row=0, padx=5, pady=5)
        ttk.Label(frame, text="Seconds:").grid(column=4, row=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.interval_s, width=5).grid(column=5, row=0, padx=5, pady=5)
        ttk.Label(frame, text="Milliseconds:").grid(column=6, row=0, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.interval_ms, width=5).grid(column=7, row=0, padx=5, pady=5)

    def create_mouse_options_widgets(self, frame):
        click_type_frame = ttk.Frame(frame)
        click_type_frame.grid(column=0, row=0, padx=5, pady=5)
        ttk.Label(click_type_frame, text="Click Type:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        click_type_menu = ttk.OptionMenu(click_type_frame, self.click_type, 'left', 'left', 'right')
        click_type_menu.grid(column=1, row=0, padx=10, pady=5, sticky=tk.W)

        click_mode_frame = ttk.Frame(frame)
        click_mode_frame.grid(column=1, row=0, padx=5, pady=5)
        ttk.Label(click_mode_frame, text="Click Mode:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        click_mode_menu = ttk.OptionMenu(click_mode_frame, self.click_mode, 'single', 'single', 'double')
        click_mode_menu.grid(column=1, row=0, padx=10, pady=5, sticky=tk.W)

        ttk.Radiobutton(frame, text="Until Stopped", variable=self.click_until_stopped, value=True).grid(column=0, row=1, padx=5, pady=5)
        ttk.Radiobutton(frame, text="Specific Number of Clicks", variable=self.click_until_stopped, value=False).grid(column=1, row=1, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.specific_clicks, width=5).grid(column=2, row=1, padx=5, pady=5)

    def create_coordinates_widgets(self, frame):
        ttk.Checkbutton(frame, text="Click Specific Coordinates", variable=self.click_coordinates, command=self.toggle_coordinates).grid(column=0, row=0, padx=5, pady=5)
        self.add_coord_button = tk.Button(frame, text="Add Coordinate", command=self.add_coordinate, width=self.button_width.get(), height=self.button_height.get())
        self.add_coord_button.grid(column=1, row=0, padx=5, pady=5)
        self.add_coord_button.config(state=tk.DISABLED)

        self.coord_listbox = tk.Listbox(frame, height=5)
        self.coord_listbox.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.coord_listbox.bind('<Double-1>', self.edit_coordinate)

    def create_button_widgets(self, frame):
        self.start_button = tk.Button(frame, text="Start", command=self.start_autoclicker, width=self.button_width.get(), height=self.button_height.get())
        self.start_button.grid(column=0, row=0, padx=10, pady=10)
        self.stop_button = tk.Button(frame, text="Stop", command=self.stop_autoclicker, width=self.button_width.get(), height=self.button_height.get())
        self.stop_button.grid(column=1, row=0, padx=10, pady=10)
        self.stop_button.config(state=tk.DISABLED)

        self.keybind_button = tk.Button(frame, text="Keybind Settings", command=self.open_keybind_settings, width=self.button_width.get(), height=self.button_height.get())
        self.keybind_button.grid(column=0, row=1, padx=10, pady=10)
        self.settings_button = tk.Button(frame, text="Settings", command=self.open_settings, width=self.button_width.get(), height=self.button_height.get())
        self.settings_button.grid(column=1, row=1, padx=10, pady=10)

    def setup_hotkeys(self):
        keyboard.add_hotkey(self.keybind.get(), self.toggle_autoclicker)

    def apply_hotkeys(self):
        keyboard.unhook_all_hotkeys()
        self.setup_hotkeys()
        print(f"Applied hotkey: {self.keybind.get()}")

    def toggle_autoclicker(self):
        if self.running:
            self.stop_autoclicker()
        else:
            self.start_autoclicker()

    def start_autoclicker(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.autoclick, daemon=True).start()

    def stop_autoclicker(self):
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def autoclick(self):
        try:
            interval = (self.interval_h.get() * 3600 + self.interval_m.get() * 60 + self.interval_s.get()) + (self.interval_ms.get() / 1000)
            clicks = 0
            while self.running:
                if self.click_coordinates.get() and self.coordinates:
                    for coord in self.coordinates:
                        if not self.running:
                            break
                        self.perform_click(coord)
                        time.sleep(interval)
                else:
                    self.perform_click()
                    time.sleep(interval)

                clicks += 1
                if not self.click_until_stopped.get() and clicks >= self.specific_clicks.get():
                    self.stop_autoclicker()
        except Exception as e:
            print(f"An error occurred: {e}")

    def perform_click(self, coord=None):
        if coord:
            if self.click_mode.get() == 'single':
                pyautogui.click(x=coord[0], y=coord[1], button=self.click_type.get())
            else:
                pyautogui.doubleClick(x=coord[0], y=coord[1], button=self.click_type.get())
        else:
            if self.click_mode.get() == 'single':
                pyautogui.click(button=self.click_type.get())
            else:
                pyautogui.doubleClick(button=self.click_type.get())

    def toggle_coordinates(self):
        if self.click_coordinates.get():
            self.add_coord_button.config(state=tk.NORMAL)
        else:
            self.add_coord_button.config(state=tk.DISABLED)

    def add_coordinate(self):
        self.root.withdraw()
        time.sleep(2)  # Give the user time to switch to the desired location
        x, y = pyautogui.position()
        self.coordinates.append((x, y))
        self.coord_listbox.insert(tk.END, f"X: {x}, Y: {y}")
        self.root.deiconify()

    def edit_coordinate(self, event):
        selection = self.coord_listbox.curselection()
        if selection:
            index = selection[0]
            coord = self.coordinates[index]
            new_x = tk.simpledialog.askinteger("Edit Coordinate", "Enter new X:", initialvalue=coord[0])
            new_y = tk.simpledialog.askinteger("Edit Coordinate", "Enter new Y:", initialvalue=coord[1])
            if new_x is not None and new_y is not None:
                self.coordinates[index] = (new_x, new_y)
                self.coord_listbox.delete(index)
                self.coord_listbox.insert(index, f"X: {new_x}, Y: {new_y}")

    def open_keybind_settings(self):
        keybind_window = tk.Toplevel(self.root)
        keybind_window.title("Keybind Settings")
        keybind_window.geometry("250x150")
        keybind_window.attributes("-topmost", True)

        ttk.Label(keybind_window, text="Keybind:").grid(column=0, row=0, padx=10, pady=10)
        ttk.Entry(keybind_window, textvariable=self.keybind).grid(column=1, row=0, padx=10, pady=10)

        apply_button = ttk.Button(keybind_window, text="Apply Keybind", command=self.apply_hotkeys)
        apply_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.attributes("-topmost", True)

        # Always on top checkbox
        always_on_top_checkbox = ttk.Checkbutton(settings_window, text="Always on Top", variable=self.always_on_top, command=self.update_always_on_top)
        always_on_top_checkbox.grid(column=0, row=0, padx=10, pady=10)

        # Button size settings
        ttk.Label(settings_window, text="Button Width:").grid(column=0, row=1, padx=10, pady=10)
        ttk.Entry(settings_window, textvariable=self.button_width).grid(column=1, row=1, padx=10, pady=10)
        ttk.Label(settings_window, text="Button Height:").grid(column=0, row=2, padx=10, pady=10)
        ttk.Entry(settings_window, textvariable=self.button_height).grid(column=1, row=2, padx=10, pady=10)

        apply_button = ttk.Button(settings_window, text="Apply", command=self.update_button_sizes)
        apply_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

    def update_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top.get())

    def update_button_sizes(self):
        self.start_button.config(width=self.button_width.get(), height=self.button_height.get())
        self.stop_button.config(width=self.button_width.get(), height=self.button_height.get())
        self.keybind_button.config(width=self.button_width.get(), height=self.button_height.get())
        self.settings_button.config(width=self.button_width.get(), height=self.button_height.get())
        self.add_coord_button.config(width=self.button_width.get(), height=self.button_height.get())

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r') as file:
                    settings = json.load(file)
                    self.interval_ms.set(settings.get('interval_ms', self.DEFAULT_INTERVAL_MS))
                    self.interval_s.set(settings.get('interval_s', 0))
                    self.interval_m.set(settings.get('interval_m', 0))
                    self.interval_h.set(settings.get('interval_h', 0))
                    self.keybind.set(settings.get('keybind', self.DEFAULT_KEYBIND))
                    self.click_type.set(settings.get('click_type', self.DEFAULT_CLICK_TYPE))
                    self.click_mode.set(settings.get('click_mode', self.DEFAULT_CLICK_MODE))
                    self.click_coordinates.set(settings.get('click_coordinates', self.DEFAULT_COORDINATES))
                    self.coordinates = settings.get('coordinates', [])
                    self.click_until_stopped.set(settings.get('click_until_stopped', self.DEFAULT_UNTIL_STOPPED))
                    self.specific_clicks.set(settings.get('specific_clicks', self.DEFAULT_SPECIFIC_CLICKS))
                    self.always_on_top.set(settings.get('always_on_top', self.DEFAULT_ALWAYS_ON_TOP))
                    self.button_width.set(settings.get('button_width', self.DEFAULT_BUTTON_WIDTH))
                    self.button_height.set(settings.get('button_height', self.DEFAULT_BUTTON_HEIGHT))
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        settings = {
            'interval_ms': self.interval_ms.get(),
            'interval_s': self.interval_s.get(),
            'interval_m': self.interval_m.get(),
            'interval_h': self.interval_h.get(),
            'keybind': self.keybind.get(),
            'click_type': self.click_type.get(),
            'click_mode': self.click_mode.get(),
            'click_coordinates': self.click_coordinates.get(),
            'coordinates': self.coordinates,
            'click_until_stopped': self.click_until_stopped.get(),
            'specific_clicks': self.specific_clicks.get(),
            'always_on_top': self.always_on_top.get(),
            'button_width': self.button_width.get(),
            'button_height': self.button_height.get()
        }
        try:
            with open(self.SETTINGS_FILE, 'w') as file:
                json.dump(settings, file)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def on_closing(self):
        self.save_settings()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()