# Planned Improvements

## Input Handling Robustness

**Issue:** Potential for stuck keyboard inputs during automation if an exception occurs between `kb.press()` and `kb.release()` calls, or if focus changes mid-sequence.

**Status (April 2026):**

- Done: Implemented a safety wrapper around `automate()` that calls `release_all_keys()` in a `finally` block.
- Done: Implemented try/finally release guarantees in key tap handlers via a shared `_tap_key()` helper.
- Done: Implemented a key-hold context manager and applied it to `startGame()` for guaranteed cleanup of held keys.
- Future: Optional enhancement — key state tracking/verification if we want richer diagnostics.

**Proposed Solutions (reference):**

1. **Safety wrapper around `automate()`**
   - Add `release_all_keys()` method to `Formationizer` class
   - Call it in a `finally` block wrapping the entire automation sequence
   - Ensures all keys are released even if automation fails

2. **Try/finally protection on individual press methods**
   - Wrap each `press_*` method to guarantee release
   - Example:
     ```python
     def press_right(self):
         kb.press('d')
         try:
             time.sleep(INPUT_DELAY)
         finally:
             kb.release('d')
         time.sleep(RELEASE_DELAY)
     ```

3. **Context manager for complex sequences**
   - `startGame()` holds 'q' while pressing other keys
   - A context manager pattern would ensure proper cleanup:
     ```python
     @contextmanager
     def hold_key(self, key):
         kb.press(key)
         try:
             yield
         finally:
             kb.release(key)
     ```

4. **Key state tracking**
   - Track which keys are currently pressed in a set
   - Allows verification and forced cleanup if needed

**Related files:** `main.py` (Formationizer class input methods and automation flow)
