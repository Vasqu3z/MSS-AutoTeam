# MSS-AutoTeam — Project Context

Python utility for automating Mario Super Sluggers team entry. Part of the Comets League Baseball tooling ecosystem.

## Working Style

- This is a fork — be mindful of upstream compatibility if changes might be contributed back.
- Surgical changes only. Don't refactor working code.
- Don't break existing functionality; the tool is actively used for CLB game recording.
- Test changes against actual Dolphin/game workflow when possible.

## Key Files

- `main.py` — Main application and UI
- `clb_loader.py` — CLB-specific team loading
- `options_manager.py` — Configuration handling

## Verification

Before finalizing changes, confirm:
- Gecko codes still generate correctly
- Team entry automation still works end-to-end
- No regressions in existing features
