# Planned Improvements

## Input Handling Robustness

**Issue:** Potential for stuck keyboard inputs during automation if an exception occurs between `kb.press()` and `kb.release()` calls, or if focus changes mid-sequence.

**Proposed Solutions (in priority order):**

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

**Related files:** `main.py` (Formationizer class, lines 535-603)
