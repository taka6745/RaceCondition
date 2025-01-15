import tkinter as tk
from tkinter import ttk, simpledialog
import pyautogui
import datetime
import platform

# Global hotkey library
from pynput import keyboard  # pip install pynput

# For Windows window focus (if needed):
if platform.system().lower().startswith('win'):
    from pywinauto.application import Application
    from pywinauto.findwindows import find_windows
    from pywinauto.controls.hwndwrapper import HwndWrapper


class RaceConditionApp(tk.Tk):
    def __init__(self, debug=0):
        super().__init__()

        self.debug = debug
        self.title("RaceCondition")
        self.geometry("500x350")

        # Configure top-level grid to be flexible
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create the main Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Mouse Clicker tab
        self.mouse_clicker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mouse_clicker_frame, text="Mouse Clicker")

        # Key Clicker tab
        self.key_clicker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.key_clicker_frame, text="Key Clicker")

        # ==================
        # VARIABLES
        # ==================
        # Mouse
        self.mouse_position = None
        self.mouse_time_var = tk.StringVar(
            value=datetime.datetime.now().strftime("%H:%M:%S")
        )
        self.mouse_end_time = None
        self.mouse_countdown_label = None

        # Key
        self.key_position = None
        self.key_time_var = tk.StringVar(
            value=datetime.datetime.now().strftime("%H:%M:%S")
        )
        self.key_end_time = None
        self.key_countdown_label = None
        self.key_to_press = None
        # This will track if we've already done the "move-and-click" for the Key clicker
        # at T-1 second:
        self.key_location_clicked = False

        # Build the two tabs
        self.build_mouse_clicker_tab()
        self.build_key_clicker_tab()

        # Start a global listener for SHIFT
        # Left Shift -> record Mouse position
        # Right Shift -> record Key position
        self.shift_listener = keyboard.Listener(on_press=self.on_key_press)
        self.shift_listener.start()

        # A repeating task to update the "Current Time" labels once per second
        self.update_current_time_labels()

    # =========================
    # BUILD TABS
    # =========================

    def build_mouse_clicker_tab(self):
        container = ttk.Frame(self.mouse_clicker_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # CURRENT TIME
        self.mouse_current_time_label = ttk.Label(
            container, text="Current Time: --:--:--"
        )
        self.mouse_current_time_label.grid(row=0, column=0, columnspan=2, sticky="w")

        # TARGET TIME
        lbl_time = ttk.Label(container, text="Target Time (HH:MM:SS):")
        lbl_time.grid(row=1, column=0, sticky="w", pady=5)
        ent_time = ttk.Entry(container, textvariable=self.mouse_time_var, width=10)
        ent_time.grid(row=1, column=1, sticky="w", pady=5)

        # BUTTON: Set Target to Current Time
        btn_set_now = ttk.Button(
            container, text="Set to Current Time",
            command=lambda: self.mouse_time_var.set(
                datetime.datetime.now().strftime("%H:%M:%S")
            )
        )
        btn_set_now.grid(row=1, column=2, padx=5, pady=5)

        # Quick +10/+20/+30 seconds
        btn_add_10s = ttk.Button(container, text="+10s", command=lambda: self.adjust_time(self.mouse_time_var, 10))
        btn_add_10s.grid(row=2, column=0, padx=5, pady=5)
        btn_add_20s = ttk.Button(container, text="+20s", command=lambda: self.adjust_time(self.mouse_time_var, 20))
        btn_add_20s.grid(row=2, column=1, padx=5, pady=5)
        btn_add_30s = ttk.Button(container, text="+30s", command=lambda: self.adjust_time(self.mouse_time_var, 30))
        btn_add_30s.grid(row=2, column=2, padx=5, pady=5)

        # Position label
        self.lbl_mouse_pos = ttk.Label(container, text="Position: (None, None)")
        self.lbl_mouse_pos.grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        # Start & Cancel
        btn_start = ttk.Button(
            container, text="Start Countdown & Click",
            command=self.start_mouse_clicker
        )
        btn_start.grid(row=4, column=0, sticky="w", pady=5)

        btn_cancel = ttk.Button(
            container, text="Cancel",
            command=self.cancel_mouse_clicker
        )
        btn_cancel.grid(row=4, column=1, sticky="w", pady=5)

        # A label to display a live countdown
        self.mouse_countdown_label = ttk.Label(container, text="Countdown: --:--:--")
        self.mouse_countdown_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=5)

        # Info
        info_label = ttk.Label(
            container,
            text="Move the mouse to where you want to click,\nthen press LEFT SHIFT to record position."
        )
        info_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=10)

    def build_key_clicker_tab(self):
        container = ttk.Frame(self.key_clicker_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # CURRENT TIME
        self.key_current_time_label = ttk.Label(
            container, text="Current Time: --:--:--"
        )
        self.key_current_time_label.grid(row=0, column=0, columnspan=2, sticky="w")

        # TARGET TIME
        lbl_time = ttk.Label(container, text="Target Time (HH:MM:SS):")
        lbl_time.grid(row=1, column=0, sticky="w", pady=5)
        ent_time = ttk.Entry(container, textvariable=self.key_time_var, width=10)
        ent_time.grid(row=1, column=1, sticky="w", pady=5)

        # BUTTON: Set Target to Current Time
        btn_set_now = ttk.Button(
            container, text="Set to Current Time",
            command=lambda: self.key_time_var.set(
                datetime.datetime.now().strftime("%H:%M:%S")
            )
        )
        btn_set_now.grid(row=1, column=2, padx=5, pady=5)

        # Quick +10/+20/+30 seconds
        btn_add_10s = ttk.Button(container, text="+10s", command=lambda: self.adjust_time(self.key_time_var, 10))
        btn_add_10s.grid(row=2, column=0, padx=5, pady=5)
        btn_add_20s = ttk.Button(container, text="+20s", command=lambda: self.adjust_time(self.key_time_var, 20))
        btn_add_20s.grid(row=2, column=1, padx=5, pady=5)
        btn_add_30s = ttk.Button(container, text="+30s", command=lambda: self.adjust_time(self.key_time_var, 30))
        btn_add_30s.grid(row=2, column=2, padx=5, pady=5)

        # Key selection
        btn_record_key = ttk.Button(container, text="Record Key to Press", command=self.record_key_press)
        btn_record_key.grid(row=3, column=0, sticky="w", pady=5)

        self.lbl_key_selected = ttk.Label(container, text="Selected Key: (None)")
        self.lbl_key_selected.grid(row=3, column=1, sticky="w", pady=5)

        # Position label (for the key location)
        self.lbl_key_pos = ttk.Label(container, text="Position: (None, None)")
        self.lbl_key_pos.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)

        # Start & Cancel
        btn_start = ttk.Button(
            container, text="Start Countdown & Key Press", 
            command=self.start_key_clicker
        )
        btn_start.grid(row=5, column=0, sticky="w", pady=5)

        btn_cancel = ttk.Button(
            container, text="Cancel",
            command=self.cancel_key_clicker
        )
        btn_cancel.grid(row=5, column=1, sticky="w", pady=5)

        # A label to display a live countdown
        self.key_countdown_label = ttk.Label(container, text="Countdown: --:--:--")
        self.key_countdown_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=5)

        # Info
        info_label = ttk.Label(
            container,
            text="Move the mouse to where you want the click to happen (1s before 0),\n"
                 "then press RIGHT SHIFT to record position.\n"
                 "At countdown = 0, the selected key will be pressed."
        )
        info_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=10)

    # =========================
    # TIME / COUNTDOWN HELPERS
    # =========================

    def adjust_time(self, time_var, seconds):
        """
        Add the given number of seconds to the time in the given time_var.
        """
        try:
            current_time = datetime.datetime.strptime(time_var.get(), "%H:%M:%S")
            new_time = current_time + datetime.timedelta(seconds=seconds)
            time_var.set(new_time.strftime("%H:%M:%S"))
        except ValueError:
            # If user typed garbage, just ignore
            pass

    def update_current_time_labels(self):
        """
        Update the "Current Time" label for both tabs every 1 second.
        """
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        # Mouse tab
        if self.mouse_current_time_label:
            self.mouse_current_time_label.config(text=f"Current Time: {now_str}")
        # Key tab
        if self.key_current_time_label:
            self.key_current_time_label.config(text=f"Current Time: {now_str}")

        # Schedule again in 1 second
        self.after(1000, self.update_current_time_labels)

    # =========================
    # SHIFT HOTKEY HANDLING
    # =========================

    def on_key_press(self, key):
        """
        Global listener (via pynput).
        - If the user presses Left Shift -> record mouse position
        - If the user presses Right Shift -> record key position
        """
        try:
            if key == keyboard.Key.shift_l:
                # Left Shift -> Mouse
                x, y = pyautogui.position()
                self.mouse_position = (x, y)
                self.lbl_mouse_pos.config(text=f"Position: ({x}, {y})")
                if self.debug:
                    print(f"[DEBUG] Recorded MOUSE position at ({x}, {y})")

            elif key == keyboard.Key.shift_r:
                # Right Shift -> Key
                x, y = pyautogui.position()
                self.key_position = (x, y)
                if self.lbl_key_pos:
                    self.lbl_key_pos.config(text=f"Position: ({x}, {y})")
                if self.debug:
                    print(f"[DEBUG] Recorded KEY position at ({x}, {y})")

        except:
            pass

    # =========================
    # MOUSE CLICKER
    # =========================

    def start_mouse_clicker(self):
        if not self.mouse_position:
            if self.debug:
                print("[DEBUG] No mouse position recorded yet!")
            return

        try:
            target_time = datetime.datetime.strptime(self.mouse_time_var.get(), "%H:%M:%S")
            now = datetime.datetime.now()

            # Combine today's date + user time
            candidate = datetime.datetime(
                year=now.year, month=now.month, day=now.day,
                hour=target_time.hour, minute=target_time.minute, second=target_time.second
            )
            if candidate < now:
                candidate += datetime.timedelta(days=1)

            self.mouse_end_time = candidate

            # Start updating countdown
            self.update_mouse_countdown()

        except ValueError:
            if self.debug:
                print("[DEBUG] Invalid time format for mouse!")
            pass

    def update_mouse_countdown(self):
        """
        Called once per second via Tk.after() to update the countdown label.
        When the countdown hits 0, do the mouse click.
        """
        if not self.mouse_end_time:
            return

        now = datetime.datetime.now()
        diff = (self.mouse_end_time - now).total_seconds()

        if diff <= 0:
            # Time's up!
            self.mouse_countdown_label.config(text="Countdown: 00:00:00")
            # Do the mouse click
            pyautogui.moveTo(*self.mouse_position)
            pyautogui.click()
            # Reset end_time
            self.mouse_end_time = None
        else:
            # Still counting down
            h, remainder = divmod(int(diff), 3600)
            m, s = divmod(remainder, 60)
            self.mouse_countdown_label.config(text=f"Countdown: {h:02d}:{m:02d}:{s:02d}")
            # Schedule the next update in 1 second
            self.after(1000, self.update_mouse_countdown)

    def cancel_mouse_clicker(self):
        """
        Cancel the mouse countdown (if any).
        """
        self.mouse_end_time = None
        self.mouse_countdown_label.config(text="Countdown: CANCELED")

    # =========================
    # KEY CLICKER
    # =========================

    def record_key_press(self):
        """
        Prompt user to enter a key string for pyautogui.press()
        """
        self.key_to_press = simpledialog.askstring("Key Input", "Enter the key to press:")
        if self.key_to_press:
            self.lbl_key_selected.config(text=f"Selected Key: {self.key_to_press}")

    def start_key_clicker(self):
        if not self.key_position:
            if self.debug:
                print("[DEBUG] No key position recorded yet!")
            return
        if not self.key_to_press:
            if self.debug:
                print("[DEBUG] No key selected yet!")
            return

        try:
            target_time = datetime.datetime.strptime(self.key_time_var.get(), "%H:%M:%S")
            now = datetime.datetime.now()

            candidate = datetime.datetime(
                year=now.year, month=now.month, day=now.day,
                hour=target_time.hour, minute=target_time.minute, second=target_time.second
            )
            if candidate < now:
                candidate += datetime.timedelta(days=1)

            self.key_end_time = candidate
            self.key_location_clicked = False  # reset so we can click again at T-1
            self.update_key_countdown()

        except ValueError:
            if self.debug:
                print("[DEBUG] Invalid time format for key press!")
            pass

    def update_key_countdown(self):
        """
        Called once per second via Tk.after() to update the countdown label
        for the key press. 
        - At T-1 (or less), move & click if not done already.
        - At T=0, press the key.
        """
        if not self.key_end_time:
            return

        now = datetime.datetime.now()
        diff = (self.key_end_time - now).total_seconds()

        if diff <= 0:
            # Time's up! Press the key
            self.key_countdown_label.config(text="Countdown: 00:00:00")
            pyautogui.press(self.key_to_press)
            self.key_end_time = None
        else:
            # If we haven't done the "move & click" yet, do it at T <= 1
            if diff <= 1 and not self.key_location_clicked:
                # Move and click at key_position
                pyautogui.moveTo(*self.key_position)
                pyautogui.click()
                self.key_location_clicked = True

            h, remainder = divmod(int(diff), 3600)
            m, s = divmod(remainder, 60)
            self.key_countdown_label.config(text=f"Countdown: {h:02d}:{m:02d}:{s:02d}")

            # Schedule the next update in 1 second
            self.after(1000, self.update_key_countdown)

    def cancel_key_clicker(self):
        """
        Cancel the key countdown (if any).
        """
        self.key_end_time = None
        self.key_countdown_label.config(text="Countdown: CANCELED")


if __name__ == "__main__":
    app = RaceConditionApp(debug=1)
    app.mainloop()
