"""
Options Manager for MSS-AutoTeam

Provides centralized, robust options storage with:
- Automatic file creation with defaults
- Backward compatibility with existing options.json
- Consistent error handling
- Type validation
- Atomic saves (write to temp, then rename)
- UI state persistence between sessions
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

# Default options structure
DEFAULT_OPTIONS = {
    "version": 1,
    "mii": {
        "databasePath": ""
    },
    "defaults": {
        "awayCaptainID": 0,
        "homeCaptainID": 1
    },
    "automation": {
        "autoStartGame": False,
        "inputDelay": 0.05,
        "releaseDelay": 0.05
    },
    "ui": {
        "lastAwayTeam": "",
        "lastHomeTeam": "",
        "lastStadium": "Mario Stadium",
        "lastDayNight": "Day",
        "lastInnings": 9,
        "lastMercy": "On",
        "lastStars": "On",
        "lastItems": "Off"
    }
}


class OptionsManager:
    """Centralized options management for MSS-AutoTeam."""

    def __init__(self, options_path: str = "options.json"):
        """
        Initialize the OptionsManager.

        Args:
            options_path: Path to the options.json file
        """
        self.options_path = Path(options_path)
        self._options: dict = {}
        self._load()

    def _get_default_options(self) -> dict:
        """Return a deep copy of the default options."""
        import copy
        return copy.deepcopy(DEFAULT_OPTIONS)

    def _migrate_legacy_options(self, legacy: dict) -> dict:
        """
        Migrate legacy flat options.json to new nested structure.

        Args:
            legacy: The legacy options dictionary

        Returns:
            Migrated options in new format
        """
        options = self._get_default_options()

        # Migrate MiiDBPath -> mii.databasePath
        if "MiiDBPath" in legacy:
            options["mii"]["databasePath"] = legacy["MiiDBPath"]

        # Migrate DefaultAwayCaptainID -> defaults.awayCaptainID
        if "DefaultAwayCaptainID" in legacy:
            options["defaults"]["awayCaptainID"] = int(legacy["DefaultAwayCaptainID"])

        # Migrate DefaultHomeCaptainID -> defaults.homeCaptainID
        if "DefaultHomeCaptainID" in legacy:
            options["defaults"]["homeCaptainID"] = int(legacy["DefaultHomeCaptainID"])

        # Migrate AutoStartGame -> automation.autoStartGame
        if "AutoStartGame" in legacy:
            options["automation"]["autoStartGame"] = bool(legacy["AutoStartGame"])

        # Preserve any new-format keys that might already exist
        if "version" in legacy:
            # Already migrated or partially migrated
            for section in ["mii", "defaults", "automation", "ui"]:
                if section in legacy and isinstance(legacy[section], dict):
                    options[section].update(legacy[section])

        return options

    def _load(self) -> None:
        """Load options from file, creating with defaults if not exists."""
        if not self.options_path.exists():
            # Create new options file with defaults
            self._options = self._get_default_options()
            self._save()
            print(f"[OptionsManager] Created new options file: {self.options_path}")
            return

        try:
            with open(self.options_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            # Check if this is legacy format (no version key or flat structure)
            if "version" not in loaded or not isinstance(loaded.get("mii"), dict):
                print("[OptionsManager] Migrating legacy options format...")
                self._options = self._migrate_legacy_options(loaded)
                self._save()  # Save migrated options
                print("[OptionsManager] Migration complete")
            else:
                # Merge with defaults to ensure all keys exist
                self._options = self._get_default_options()
                self._deep_update(self._options, loaded)

        except json.JSONDecodeError as e:
            print(f"[OptionsManager] Error parsing options.json: {e}")
            print("[OptionsManager] Using default options")
            self._options = self._get_default_options()
            # Backup corrupt file and create new one
            self._backup_and_reset()
        except Exception as e:
            print(f"[OptionsManager] Error loading options: {e}")
            self._options = self._get_default_options()

    def _deep_update(self, base: dict, updates: dict) -> None:
        """
        Recursively update base dict with values from updates.

        Args:
            base: The base dictionary to update
            updates: The dictionary with new values
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def _backup_and_reset(self) -> None:
        """Backup corrupt options file and create new one."""
        if self.options_path.exists():
            backup_path = self.options_path.with_suffix('.json.backup')
            try:
                os.rename(self.options_path, backup_path)
                print(f"[OptionsManager] Backed up corrupt file to: {backup_path}")
            except Exception as e:
                print(f"[OptionsManager] Could not backup file: {e}")
        self._save()

    def _save(self) -> bool:
        """
        Save options to file atomically.

        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Write to temporary file first
            dir_path = self.options_path.parent or Path('.')
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                suffix='.tmp',
                dir=dir_path,
                delete=False
            ) as tmp_file:
                json.dump(self._options, tmp_file, indent=4)
                tmp_path = tmp_file.name

            # Atomic rename (on most systems)
            os.replace(tmp_path, self.options_path)
            return True

        except Exception as e:
            print(f"[OptionsManager] Error saving options: {e}")
            # Clean up temp file if it exists
            try:
                if 'tmp_path' in locals():
                    os.unlink(tmp_path)
            except Exception:
                pass
            return False

    def save(self) -> bool:
        """
        Public method to save current options to file.

        Returns:
            True if save was successful, False otherwise
        """
        return self._save()

    # -------------------------------------------------------------------------
    # Mii Settings
    # -------------------------------------------------------------------------

    @property
    def mii_database_path(self) -> str:
        """Get the Mii database path."""
        return self._options["mii"]["databasePath"]

    @mii_database_path.setter
    def mii_database_path(self, value: str) -> None:
        """Set the Mii database path."""
        self._options["mii"]["databasePath"] = str(value)

    # -------------------------------------------------------------------------
    # Default Captain Settings
    # -------------------------------------------------------------------------

    @property
    def default_away_captain_id(self) -> int:
        """Get the default away captain ID."""
        return int(self._options["defaults"]["awayCaptainID"])

    @default_away_captain_id.setter
    def default_away_captain_id(self, value: int) -> None:
        """Set the default away captain ID."""
        self._options["defaults"]["awayCaptainID"] = int(value)

    @property
    def default_home_captain_id(self) -> int:
        """Get the default home captain ID."""
        return int(self._options["defaults"]["homeCaptainID"])

    @default_home_captain_id.setter
    def default_home_captain_id(self, value: int) -> None:
        """Set the default home captain ID."""
        self._options["defaults"]["homeCaptainID"] = int(value)

    # -------------------------------------------------------------------------
    # Automation Settings
    # -------------------------------------------------------------------------

    @property
    def auto_start_game(self) -> bool:
        """Get whether to auto-start game after setup."""
        return bool(self._options["automation"]["autoStartGame"])

    @auto_start_game.setter
    def auto_start_game(self, value: bool) -> None:
        """Set whether to auto-start game after setup."""
        self._options["automation"]["autoStartGame"] = bool(value)

    @property
    def input_delay(self) -> float:
        """Get the input delay in seconds."""
        return float(self._options["automation"]["inputDelay"])

    @input_delay.setter
    def input_delay(self, value: float) -> None:
        """Set the input delay in seconds."""
        self._options["automation"]["inputDelay"] = max(0.01, float(value))

    @property
    def release_delay(self) -> float:
        """Get the release delay in seconds."""
        return float(self._options["automation"]["releaseDelay"])

    @release_delay.setter
    def release_delay(self, value: float) -> None:
        """Set the release delay in seconds."""
        self._options["automation"]["releaseDelay"] = max(0.01, float(value))

    # -------------------------------------------------------------------------
    # UI State Persistence
    # -------------------------------------------------------------------------

    @property
    def last_away_team(self) -> str:
        """Get the last selected away team name."""
        return self._options["ui"]["lastAwayTeam"]

    @last_away_team.setter
    def last_away_team(self, value: str) -> None:
        """Set the last selected away team name."""
        self._options["ui"]["lastAwayTeam"] = str(value)

    @property
    def last_home_team(self) -> str:
        """Get the last selected home team name."""
        return self._options["ui"]["lastHomeTeam"]

    @last_home_team.setter
    def last_home_team(self, value: str) -> None:
        """Set the last selected home team name."""
        self._options["ui"]["lastHomeTeam"] = str(value)

    @property
    def last_stadium(self) -> str:
        """Get the last selected stadium."""
        return self._options["ui"]["lastStadium"]

    @last_stadium.setter
    def last_stadium(self, value: str) -> None:
        """Set the last selected stadium."""
        self._options["ui"]["lastStadium"] = str(value)

    @property
    def last_day_night(self) -> str:
        """Get the last selected day/night setting."""
        return self._options["ui"]["lastDayNight"]

    @last_day_night.setter
    def last_day_night(self, value: str) -> None:
        """Set the last selected day/night setting."""
        if value in ("Day", "Night"):
            self._options["ui"]["lastDayNight"] = value

    @property
    def last_innings(self) -> int:
        """Get the last selected innings count."""
        return int(self._options["ui"]["lastInnings"])

    @last_innings.setter
    def last_innings(self, value: int) -> None:
        """Set the last selected innings count."""
        if value in (1, 3, 5, 7, 9):
            self._options["ui"]["lastInnings"] = int(value)

    @property
    def last_mercy(self) -> str:
        """Get the last selected mercy rule setting."""
        return self._options["ui"]["lastMercy"]

    @last_mercy.setter
    def last_mercy(self, value: str) -> None:
        """Set the last selected mercy rule setting."""
        if value in ("Off", "On"):
            self._options["ui"]["lastMercy"] = value

    @property
    def last_stars(self) -> str:
        """Get the last selected stars setting."""
        return self._options["ui"]["lastStars"]

    @last_stars.setter
    def last_stars(self, value: str) -> None:
        """Set the last selected stars setting."""
        if value in ("Off", "On"):
            self._options["ui"]["lastStars"] = value

    @property
    def last_items(self) -> str:
        """Get the last selected items setting."""
        return self._options["ui"]["lastItems"]

    @last_items.setter
    def last_items(self, value: str) -> None:
        """Set the last selected items setting."""
        if value in ("Off", "On"):
            self._options["ui"]["lastItems"] = value

    # -------------------------------------------------------------------------
    # Legacy Compatibility Properties
    # -------------------------------------------------------------------------

    def get_legacy_format(self) -> dict:
        """
        Get options in the legacy flat format for backward compatibility.

        Returns:
            Dictionary in legacy format
        """
        return {
            "MiiDBPath": self.mii_database_path,
            "DefaultAwayCaptainID": self.default_away_captain_id,
            "DefaultHomeCaptainID": self.default_home_captain_id,
            "AutoStartGame": self.auto_start_game
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value using legacy key names for backward compatibility.

        Args:
            key: The legacy key name
            default: Default value if key not found

        Returns:
            The value for the key, or default if not found
        """
        legacy_map = {
            "MiiDBPath": lambda: self.mii_database_path,
            "DefaultAwayCaptainID": lambda: self.default_away_captain_id,
            "DefaultHomeCaptainID": lambda: self.default_home_captain_id,
            "AutoStartGame": lambda: self.auto_start_game,
        }

        if key in legacy_map:
            return legacy_map[key]()
        return default

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access for legacy compatibility."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment for legacy compatibility."""
        if key == "MiiDBPath":
            self.mii_database_path = value
        elif key == "DefaultAwayCaptainID":
            self.default_away_captain_id = value
        elif key == "DefaultHomeCaptainID":
            self.default_home_captain_id = value
        elif key == "AutoStartGame":
            self.auto_start_game = value
        else:
            raise KeyError(f"Unknown option key: {key}")


# Singleton instance for global access
_options_manager: Optional[OptionsManager] = None


def get_options_manager(options_path: str = "options.json") -> OptionsManager:
    """
    Get the global OptionsManager instance (singleton pattern).

    Args:
        options_path: Path to options file (only used on first call)

    Returns:
        The global OptionsManager instance
    """
    global _options_manager
    if _options_manager is None:
        _options_manager = OptionsManager(options_path)
    return _options_manager
