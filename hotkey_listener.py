"""
Global hotkey listener for triggering the automation workflow.
Uses pynput for cross-platform hotkey detection.
"""

import threading
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


# Mapping of modifier key names to pynput Key objects
MODIFIER_MAP = {
    "cmd": Key.cmd,
    "command": Key.cmd,
    "ctrl": Key.ctrl,
    "control": Key.ctrl,
    "alt": Key.alt,
    "option": Key.alt,
    "shift": Key.shift,
    "fn": Key.f20,  # Fn key handling is limited
}


def parse_hotkey(hotkey_str: str) -> tuple[set, Optional[KeyCode]]:
    """
    Parse a hotkey string like "cmd+l" into modifiers and key.
    
    Args:
        hotkey_str: Hotkey string (e.g., "cmd+l", "ctrl+shift+k")
    
    Returns:
        Tuple of (set of modifier Keys, main KeyCode)
    """
    parts = hotkey_str.lower().replace(" ", "").split("+")
    modifiers = set()
    main_key = None
    
    for part in parts:
        if part in MODIFIER_MAP:
            modifiers.add(MODIFIER_MAP[part])
        elif len(part) == 1:
            main_key = KeyCode.from_char(part)
        else:
            # Handle special keys like "space"
            if part == "space":
                main_key = Key.space
            elif part == "enter" or part == "return":
                main_key = Key.enter
            elif part == "tab":
                main_key = Key.tab
            elif part == "escape" or part == "esc":
                main_key = Key.esc
    
    return modifiers, main_key


class HotkeyListener:
    """
    Global hotkey listener that runs in a background thread.
    """
    
    def __init__(self, hotkey_str: str, callback: Callable[[], None]):
        """
        Initialize the hotkey listener.
        
        Args:
            hotkey_str: Hotkey string (e.g., "cmd+l")
            callback: Function to call when hotkey is pressed
        """
        self.hotkey_str = hotkey_str
        self.callback = callback
        self.listener: Optional[keyboard.Listener] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False
        
        # Parse the hotkey
        self.required_modifiers, self.main_key = parse_hotkey(hotkey_str)
        self.current_modifiers: set = set()
    
    def _on_press(self, key):
        """Handle key press events."""
        # Track modifier keys
        if key in (Key.cmd, Key.cmd_l, Key.cmd_r):
            self.current_modifiers.add(Key.cmd)
        elif key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            self.current_modifiers.add(Key.ctrl)
        elif key in (Key.alt, Key.alt_l, Key.alt_r):
            self.current_modifiers.add(Key.alt)
        elif key in (Key.shift, Key.shift_l, Key.shift_r):
            self.current_modifiers.add(Key.shift)
        
        # Check if hotkey combination is pressed
        if self.main_key is not None:
            key_matches = False
            
            if hasattr(key, 'char') and key.char:
                key_matches = (KeyCode.from_char(key.char.lower()) == self.main_key)
            elif key == self.main_key:
                key_matches = True
            
            if key_matches and self.required_modifiers.issubset(self.current_modifiers):
                # Hotkey triggered!
                self.callback()
    
    def _on_release(self, key):
        """Handle key release events."""
        # Remove modifier keys from tracking
        if key in (Key.cmd, Key.cmd_l, Key.cmd_r):
            self.current_modifiers.discard(Key.cmd)
        elif key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            self.current_modifiers.discard(Key.ctrl)
        elif key in (Key.alt, Key.alt_l, Key.alt_r):
            self.current_modifiers.discard(Key.alt)
        elif key in (Key.shift, Key.shift_l, Key.shift_r):
            self.current_modifiers.discard(Key.shift)
    
    def start(self) -> bool:
        """
        Start listening for the hotkey in a background thread.
        
        Returns:
            True if started successfully, False if already running
        """
        if self.running:
            return False
        
        self.running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        return True
    
    def stop(self) -> None:
        """Stop the hotkey listener."""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def is_running(self) -> bool:
        """Check if the listener is currently running."""
        return self.running


if __name__ == "__main__":
    # Test the hotkey listener
    def test_callback():
        print("🔥 Hotkey triggered!")
    
    listener = HotkeyListener("cmd+l", test_callback)
    print("Starting hotkey listener for Cmd+L...")
    print("Press Cmd+L to test. Press Ctrl+C to exit.")
    
    listener.start()
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
        print("\nStopped.")
