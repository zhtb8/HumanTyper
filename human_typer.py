import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import random
import time
import threading
import keyboard

class HumanTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Human-like Typer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.typing = False
        self.stop_requested = False
        
    def setup_ui(self):
        # Frame for input text
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(input_frame, text="Paste the text you want to type:").pack(anchor=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Settings frame
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Speed settings
        speed_frame = tk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(speed_frame, text="Typing Speed:").pack(side=tk.LEFT)
        
        self.speed_var = tk.DoubleVar(value=0.1)
        speed_scale = tk.Scale(speed_frame, from_=0.01, to=0.3, resolution=0.01, 
                              orient=tk.HORIZONTAL, variable=self.speed_var, 
                              label="Delay between keystrokes (seconds)")
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Error settings
        error_frame = tk.Frame(settings_frame)
        error_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(error_frame, text="Error Rate:").pack(side=tk.LEFT)
        
        self.error_var = tk.DoubleVar(value=0.03)  # Reduced from 0.05 to 0.03
        error_scale = tk.Scale(error_frame, from_=0, to=0.2, resolution=0.01, 
                              orient=tk.HORIZONTAL, variable=self.error_var,
                              label="Probability of making a typo")
        error_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start Typing (F8)", 
                                     command=self.start_typing, bg="#4CAF50", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop Typing (Esc)", 
                                    command=self.stop_typing, bg="#F44336", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Click 'Start Typing' then click where you want to type.")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind hotkeys
        keyboard.add_hotkey('f8', self.start_typing)
        keyboard.add_hotkey('esc', self.stop_typing)
        
    def start_typing(self):
        if self.typing:
            return
            
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please enter some text to type")
            return
            
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Click where you want to type...")
        
        self.typing = True
        self.stop_requested = False
        
        # Start typing in a separate thread
        threading.Thread(target=self.wait_and_type, args=(text,), daemon=True).start()
    
    def wait_and_type(self, text):
        # Wait for user to click somewhere
        self.root.iconify()  # Minimize the window
        time.sleep(2)  # Give user time to click
        
        if not self.typing:
            return
            
        self.status_var.set("Typing... Press Esc to stop")
        
        try:
            self.type_with_human_errors(text)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.typing = False
            self.root.deiconify()  # Restore window
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Ready. Click 'Start Typing' then click where you want to type.")
    
    def type_with_human_errors(self, text):
        delay = self.speed_var.get()
        error_rate = self.error_var.get()
        
        # Track consecutive errors to prevent too many in a row
        consecutive_errors = 0
        max_consecutive_errors = 2
        
        i = 0
        while i < len(text) and not self.stop_requested:
            char = text[i]
            
            # Reduce error probability for special characters
            current_error_rate = error_rate
            if char in ".,;:'\"!?-()[]{}":
                current_error_rate = error_rate * 0.3
            elif char == "'":  # Special handling for apostrophes
                current_error_rate = error_rate * 0.1
            
            # Decide whether to make an error, but prevent too many consecutive errors
            if random.random() < current_error_rate and consecutive_errors < max_consecutive_errors:
                self.make_typing_error(char)
                consecutive_errors += 1
                # Only increment i after successfully typing the character
                # This happens in make_typing_error now
                if random.random() < 0.9:  # 90% chance to continue with correct char after error
                    pyautogui.write(char)
                    i += 1
                    consecutive_errors = 0
            else:
                # Type the correct character
                pyautogui.write(char)
                i += 1
                consecutive_errors = 0
            
            # Random delay between keystrokes
            time.sleep(delay * random.uniform(0.5, 1.5))
            
            # Occasionally pause like a human would
            if random.random() < 0.01:
                time.sleep(random.uniform(0.5, 2.0))
    
    def make_typing_error(self, correct_char):
        # Adjust probabilities based on error type
        if correct_char.isalpha():
            error_type = random.choices(
                ['adjacent', 'double', 'wrong'],
                weights=[0.6, 0.3, 0.1],  # More adjacent key errors, fewer random errors
                k=1
            )[0]
        else:
            # For non-alphabetic characters, prefer adjacent key errors
            error_type = random.choices(
                ['adjacent', 'double', 'wrong'],
                weights=[0.8, 0.1, 0.1],
                k=1
            )[0]
        
        if error_type == 'adjacent':
            # Type an adjacent key on the keyboard
            adjacent_keys = self.get_adjacent_keys(correct_char)
            if adjacent_keys:
                wrong_char = random.choice(adjacent_keys)
                pyautogui.write(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.press('backspace')
                
        elif error_type == 'double':
            # Double type the character
            pyautogui.write(correct_char)
            time.sleep(random.uniform(0.05, 0.2))
            pyautogui.press('backspace')
            
        elif error_type == 'wrong':
            # Type a random wrong character
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            pyautogui.write(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))
            pyautogui.press('backspace')
    
    def get_adjacent_keys(self, char):
        keyboard_layout = {
            'q': ['w', 'a', '1'],
            'w': ['q', 'e', 'a', 's', '2'],
            'e': ['w', 'r', 's', 'd', '3'],
            'r': ['e', 't', 'd', 'f', '4'],
            't': ['r', 'y', 'f', 'g', '5'],
            'y': ['t', 'u', 'g', 'h', '6'],
            'u': ['y', 'i', 'h', 'j', '7'],
            'i': ['u', 'o', 'j', 'k', '8'],
            'o': ['i', 'p', 'k', 'l', '9'],
            'p': ['o', '[', 'l', ';', '0'],
            'a': ['q', 'w', 's', 'z'],
            's': ['w', 'e', 'a', 'd', 'z', 'x'],
            'd': ['e', 'r', 's', 'f', 'x', 'c'],
            'f': ['r', 't', 'd', 'g', 'c', 'v'],
            'g': ['t', 'y', 'f', 'h', 'v', 'b'],
            'h': ['y', 'u', 'g', 'j', 'b', 'n'],
            'j': ['u', 'i', 'h', 'k', 'n', 'm'],
            'k': ['i', 'o', 'j', 'l', 'm', ','],
            'l': ['o', 'p', 'k', ';', ',', '.'],
            'z': ['a', 's', 'x'],
            'x': ['s', 'd', 'z', 'c'],
            'c': ['d', 'f', 'x', 'v'],
            'v': ['f', 'g', 'c', 'b'],
            'b': ['g', 'h', 'v', 'n'],
            'n': ['h', 'j', 'b', 'm'],
            'm': ['j', 'k', 'n', ','],
            ',': ['k', 'l', 'm', '.'],
            '.': ['l', ';', ',', '/'],
            ' ': ['c', 'v', 'b', 'n', 'm'],
            "'": [';', 'l', 'p'],
            '"': ["'", ';', 'l'],
            '-': ['0', 'p', '['],
            '1': ['q', 'w', '2'],
            '2': ['1', 'q', 'w', '3'],
            '3': ['2', 'w', 'e', '4'],
            '4': ['3', 'e', 'r', '5'],
            '5': ['4', 'r', 't', '6'],
            '6': ['5', 't', 'y', '7'],
            '7': ['6', 'y', 'u', '8'],
            '8': ['7', 'u', 'i', '9'],
            '9': ['8', 'i', 'o', '0'],
            '0': ['9', 'o', 'p', '-']
        }
        
        # Convert to lowercase for lookup
        char_lower = char.lower()
        
        # Return adjacent keys if available, otherwise empty list
        return keyboard_layout.get(char_lower, [])
    
    def stop_typing(self):
        if not self.typing:
            return
            
        self.stop_requested = True
        self.status_var.set("Stopping...")

if __name__ == "__main__":
    root = tk.Tk()
    app = HumanTyperApp(root)
    root.mainloop()