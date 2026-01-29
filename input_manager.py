"""
Input Manager for MSS-AutoTeam

Provides a unified interface for keyboard and mouse input with:
- Configurable key bindings
- Optional mouse button support
- Press/release timing control
- Key capture for rebinding UI
"""

import time
from typing import Optional, Callable

# Try to import pynput, fall back to keyboard library if not available
try:
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    from pynput import keyboard as pynput_keyboard
    PYNPUT_AVAILABLE = True
except ImportError as e:
    print(f"[InputManager] pynput not available: {e}")
    print("[InputManager] Falling back to keyboard library")
    PYNPUT_AVAILABLE = False
    import keyboard as kb


# Default control mappings (matching original hardcoded values)
DEFAULT_CONTROLS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "a_button": "k",
    "b_button": "l",
    "minus_button": "q",
    "plus_button": "e"
}

# Mouse button mappings (only available with pynput)
if PYNPUT_AVAILABLE:
    MOUSE_BUTTONS = {
        "left": Button.left,
        "right": Button.right,
        "middle": Button.middle
    }

    # Special key mappings (pynput Key objects)
    SPECIAL_KEYS = {
        "space": Key.space,
        "enter": Key.enter,
        "tab": Key.tab,
        "escape": Key.esc,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "insert": Key.insert,
        "home": Key.home,
        "end": Key.end,
        "page_up": Key.page_up,
        "page_down": Key.page_down,
        "up_arrow": Key.up,
        "down_arrow": Key.down,
        "left_arrow": Key.left,
        "right_arrow": Key.right,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
        "shift": Key.shift,
        "ctrl": Key.ctrl,
        "alt": Key.alt,
        "caps_lock": Key.caps_lock,
        "num_lock": Key.num_lock,
    }
else:
    MOUSE_BUTTONS = {}
    SPECIAL_KEYS = {}


class InputManager:
    """
    Unified input manager supporting keyboard and mouse input.

    Reads control mappings from OptionsManager and provides methods
    for sending inputs to Dolphin emulator.
    """

    def __init__(self, options_manager):
        """
        Initialize the InputManager.

        Args:
            options_manager: The OptionsManager instance to read controls from
        """
        self.options = options_manager
        self.use_pynput = PYNPUT_AVAILABLE

        if PYNPUT_AVAILABLE:
            self.keyboard = KeyboardController()
            self.mouse = MouseController()
        else:
            self.keyboard = None
            self.mouse = None

    def _get_key(self, key_name: str):
        """
        Convert a key name string to a pynput key.

        Args:
            key_name: The key name (e.g., "w", "space", "f1")

        Returns:
            The pynput key object or character
        """
        key_lower = key_name.lower()

        # Check for special keys first
        if key_lower in SPECIAL_KEYS:
            return SPECIAL_KEYS[key_lower]

        # Single character keys
        if len(key_name) == 1:
            return key_name.lower()

        # Unknown key, return as-is
        return key_name

    def _press_key(self, key_name: str) -> None:
        """Press and release a keyboard key with configured timing."""
        if self.use_pynput:
            key = self._get_key(key_name)
            self.keyboard.press(key)
            time.sleep(self.options.input_delay)
            self.keyboard.release(key)
            time.sleep(self.options.release_delay)
        else:
            # Fallback to keyboard library
            kb.press(key_name)
            time.sleep(self.options.input_delay)
            kb.release(key_name)
            time.sleep(self.options.release_delay)

    def _click_mouse(self, button_name: str) -> None:
        """Click a mouse button."""
        if not self.use_pynput:
            print("[InputManager] Mouse input requires pynput")
            return

        if button_name in MOUSE_BUTTONS:
            self.mouse.click(MOUSE_BUTTONS[button_name])
            time.sleep(self.options.release_delay)

    def _send_input(self, control_name: str) -> None:
        """
        Send input for a named control, using mouse if configured.

        Args:
            control_name: The control name (e.g., "a_button", "up")
        """
        # Check if mouse is enabled for this control
        mouse_key = f"mouse_{control_name}"
        if hasattr(self.options, 'controls_use_mouse') and self.options.controls_use_mouse:
            mouse_binding = self.options.get_control_mouse(control_name)
            if mouse_binding:
                self._click_mouse(mouse_binding)
                return

        # Use keyboard
        key_binding = self.options.get_control(control_name)
        if key_binding:
            self._press_key(key_binding)

    # -------------------------------------------------------------------------
    # Public Input Methods (matching original Formationizer interface)
    # -------------------------------------------------------------------------

    def press_up(self) -> None:
        """Press the up direction."""
        self._send_input("up")

    def press_down(self) -> None:
        """Press the down direction."""
        self._send_input("down")

    def press_left(self) -> None:
        """Press the left direction."""
        self._send_input("left")

    def press_right(self) -> None:
        """Press the right direction."""
        self._send_input("right")

    def press_a(self) -> None:
        """Press the A button."""
        self._send_input("a_button")

    def press_b(self) -> None:
        """Press the B button."""
        self._send_input("b_button")

    def press_plus(self) -> None:
        """Press the + button."""
        self._send_input("plus_button")

    def press_minus(self) -> None:
        """Press the - button."""
        self._send_input("minus_button")

    def start_game(self) -> None:
        """
        Execute the start game input sequence.
        Holds minus while pressing A.
        """
        minus_key_name = self.options.get_control("minus_button")
        a_key_name = self.options.get_control("a_button")

        if self.use_pynput:
            minus_key = self._get_key(minus_key_name)
            a_key = self._get_key(a_key_name)

            self.keyboard.press(minus_key)
            time.sleep(self.options.input_delay)
            self.keyboard.press(a_key)
            time.sleep(self.options.input_delay)
            self.keyboard.release(a_key)
            time.sleep(self.options.release_delay)
            self.keyboard.release(minus_key)
            time.sleep(self.options.release_delay)
        else:
            # Fallback to keyboard library
            kb.press(minus_key_name)
            time.sleep(self.options.input_delay)
            kb.press(a_key_name)
            time.sleep(self.options.input_delay)
            kb.release(a_key_name)
            time.sleep(self.options.release_delay)
            kb.release(minus_key_name)
            time.sleep(self.options.release_delay)

    def execute(self, instructions: str) -> None:
        """
        Execute a string of input instructions.

        Args:
            instructions: String where each character is an instruction:
                         u=up, d=down, l=left, r=right, a=A button, w=wait
        """
        for char in instructions:
            if char == "u":
                self.press_up()
            elif char == "d":
                self.press_down()
            elif char == "l":
                self.press_left()
            elif char == "r":
                self.press_right()
            elif char == "a":
                self.press_a()
            elif char == "w":
                time.sleep(0.5)

        time.sleep(self.options.input_delay)


class KeyCaptureDialog:
    """
    Helper class for capturing key presses in the UI.
    Used for rebinding controls.
    """

    def __init__(self):
        self.captured_key: Optional[str] = None
        self.listener = None
        self._callback: Optional[Callable] = None

    def _on_press(self, key):
        """Handle key press during capture."""
        if not PYNPUT_AVAILABLE:
            return False

        try:
            # Regular character key
            if hasattr(key, 'char') and key.char:
                self.captured_key = key.char
            else:
                # Special key - find its name
                for name, special_key in SPECIAL_KEYS.items():
                    if key == special_key:
                        self.captured_key = name
                        break
                else:
                    # Unknown special key
                    self.captured_key = str(key).replace("Key.", "")
        except AttributeError:
            self.captured_key = str(key).replace("Key.", "")

        # Stop listening after capture
        if self.listener:
            self.listener.stop()

        # Call the callback if set
        if self._callback:
            self._callback(self.captured_key)

        return False  # Stop listener

    def capture(self, callback: Optional[Callable] = None, timeout: float = 5.0) -> Optional[str]:
        """
        Start listening for a key press.

        Args:
            callback: Optional callback function to call with captured key
            timeout: Maximum time to wait for input (seconds)

        Returns:
            The captured key name, or None if timed out
        """
        if not PYNPUT_AVAILABLE:
            print("[KeyCaptureDialog] Key capture requires pynput with X display")
            if callback:
                callback(None)
            return None

        self.captured_key = None
        self._callback = callback

        self.listener = pynput_keyboard.Listener(on_press=self._on_press)
        self.listener.start()
        self.listener.join(timeout=timeout)

        if self.listener.is_alive():
            self.listener.stop()

        return self.captured_key

    def capture_async(self, callback: Callable) -> None:
        """
        Start listening for a key press asynchronously.

        Args:
            callback: Callback function to call with captured key
        """
        if not PYNPUT_AVAILABLE:
            print("[KeyCaptureDialog] Key capture requires pynput with X display")
            callback(None)
            return

        self.captured_key = None
        self._callback = callback

        self.listener = pynput_keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def cancel(self) -> None:
        """Cancel an ongoing capture."""
        if PYNPUT_AVAILABLE and self.listener and self.listener.is_alive():
            self.listener.stop()


def get_display_name(key_name: str) -> str:
    """
    Get a user-friendly display name for a key.

    Args:
        key_name: The internal key name

    Returns:
        A formatted display string
    """
    if not key_name:
        return "(none)"

    # Special key display names
    display_names = {
        "space": "Space",
        "enter": "Enter",
        "tab": "Tab",
        "escape": "Esc",
        "backspace": "Backspace",
        "delete": "Delete",
        "up_arrow": "Up Arrow",
        "down_arrow": "Down Arrow",
        "left_arrow": "Left Arrow",
        "right_arrow": "Right Arrow",
        "shift": "Shift",
        "ctrl": "Ctrl",
        "alt": "Alt",
    }

    key_lower = key_name.lower()
    if key_lower in display_names:
        return display_names[key_lower]

    # F-keys
    if key_lower.startswith("f") and key_lower[1:].isdigit():
        return key_name.upper()

    # Single character - uppercase
    if len(key_name) == 1:
        return key_name.upper()

    # Capitalize first letter
    return key_name.capitalize()


def get_mouse_display_name(button_name: str) -> str:
    """
    Get a user-friendly display name for a mouse button.

    Args:
        button_name: The internal button name

    Returns:
        A formatted display string
    """
    if not button_name:
        return "(none)"

    display_names = {
        "left": "Left Click",
        "right": "Right Click",
        "middle": "Middle Click"
    }

    return display_names.get(button_name.lower(), button_name)
