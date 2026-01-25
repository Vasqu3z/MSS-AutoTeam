"""
CLB Loader Module for MSS-AutoTeam

Handles loading and saving teams in CLB (Comets League Baseball) LineupBuilder format.
This replaces the old teams.json format with individual CLB JSON files in the saves/ directory.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

# Directory for CLB lineup files
SAVES_DIR = Path(__file__).parent / "saves"

# MSS Character name to index mapping (indices 0-76)
# Matches AutoTeam's charList exactly
# Names should match CLB Player Registry column A (Database ID)
CHARACTER_MAP = {
    "Mario": 0,
    "Luigi": 1,
    "Donkey Kong": 2,
    "Diddy Kong": 3,
    "Peach": 4,
    "Daisy": 5,
    "Green Yoshi": 6,
    "Baby Mario": 7,
    "Baby Luigi": 8,
    "Bowser": 9,
    "Wario": 10,
    "Waluigi": 11,
    "Green Koopa Troopa": 12,
    "Red Toad": 13,
    "Boo": 14,
    "Toadette": 15,
    "Red Shy Guy": 16,
    "Birdo": 17,
    "Monty Mole": 18,
    "Bowser Jr.": 19,
    "Red Koopa Paratroopa": 20,
    "Blue Pianta": 21,
    "Red Pianta": 22,
    "Yellow Pianta": 23,
    "Blue Noki": 24,
    "Red Noki": 25,
    "Green Noki": 26,
    "Hammer Bro": 27,
    "Toadsworth": 28,
    "Blue Toad": 29,
    "Yellow Toad": 30,
    "Green Toad": 31,
    "Purple Toad": 32,
    "Blue Magikoopa": 33,
    "Red Magikoopa": 34,
    "Green Magikoopa": 35,
    "Yellow Magikoopa": 36,
    "King Boo": 37,
    "Petey Piranha": 38,
    "Dixie Kong": 39,
    "Goomba": 40,
    "Paragoomba": 41,
    "Red Koopa Troopa": 42,
    "Green Koopa Paratroopa": 43,
    "Blue Shy Guy": 44,
    "Yellow Shy Guy": 45,
    "Green Shy Guy": 46,
    "Gray Shy Guy": 47,
    "Gray Dry Bones": 48,
    "Green Dry Bones": 49,
    "Dark Bones": 50,
    "Blue Dry Bones": 51,
    "Fire Bro": 52,
    "Boomerang Bro": 53,
    "Wiggler": 54,
    "Blooper": 55,
    "Funky Kong": 56,
    "Tiny Kong": 57,
    "Green Kritter": 58,
    "Blue Kritter": 59,
    "Red Kritter": 60,
    "Brown Kritter": 61,
    "King K. Rool": 62,
    "Baby Peach": 63,
    "Baby Daisy": 64,
    "Baby DK": 65,
    "Red Yoshi": 66,
    "Blue Yoshi": 67,
    "Yellow Yoshi": 68,
    "Light Blue Yoshi": 69,
    "Pink Yoshi": 70,
    # Unused characters (71-76)
    "Unused Yoshi 2": 71,
    "Unused Yoshi": 72,
    "Unused Toad": 73,
    "Unused Pianta": 74,
    "Unused Kritter": 75,
    "Unused Koopa": 76,
}

# Reverse lookup: index -> name
CHARACTER_NAMES = {v: k for k, v in CHARACTER_MAP.items()}

# Mii character IDs start at 77 (after the 77 base characters: 0-76)
MII_START_INDEX = 77

# Position name to AutoTeam index mapping
POSITION_MAP = {
    "P": 0,
    "C": 1,
    "1B": 2,
    "2B": 3,
    "3B": 4,
    "SS": 5,
    "LF": 6,
    "CF": 7,
    "RF": 8,
}

# Reverse lookup: index -> position name
POSITION_NAMES = {v: k for k, v in POSITION_MAP.items()}


def resolve_character_id(player: dict, mii_list: list) -> Optional[int]:
    """
    Resolve a player to their MSS character ID.

    Args:
        player: Player dict with 'databaseId', 'name', and 'isMii' fields
        mii_list: List of Mii objects from RFL_DB.dat

    Returns:
        Character ID (0-76 for base characters, 77+ for Miis), or None if not found
    """
    if player is None:
        return None

    database_id = player.get('databaseId', '')
    player_name = player.get('name', '')
    is_mii = player.get('isMii', False)

    if is_mii:
        # For Miis, match player_name against mii_list
        # Case-insensitive matching
        for idx, mii in enumerate(mii_list):
            if mii.name.lower() == player_name.lower():
                return MII_START_INDEX + idx
        print(f"  Warning: Mii '{player_name}' not found in RFL_DB.dat")
        return None
    else:
        # For base game characters, use databaseId
        if database_id in CHARACTER_MAP:
            return CHARACTER_MAP[database_id]
        else:
            print(f"  Warning: Character '{database_id}' not found in CHARACTER_MAP")
            return None


def convert_clb_lineup(lineup_data: dict, mii_list: list) -> Optional[List[List[int]]]:
    """
    Convert a CLB lineup to AutoTeam format.

    Args:
        lineup_data: CLB export JSON data
        mii_list: List of Mii objects from RFL_DB.dat

    Returns:
        Team roster as list of [character_id, batting_order, field_position], or None on failure
    """
    roster = lineup_data.get('roster', {})
    batting_order = lineup_data.get('battingOrder', [])

    # Detect export format (new format has player objects, old format has player ID strings)
    sample_roster_value = next((v for v in roster.values() if v is not None), None)
    is_new_format = isinstance(sample_roster_value, dict)

    if not is_new_format:
        print(f"  Error: This lineup uses the old export format (player IDs only).")
        print(f"  Please re-export the lineup from the CLB Lineup Builder.")
        return None

    # Build position map: player_id -> field_position_index
    position_lookup = {}
    for pos_name, player in roster.items():
        if player and isinstance(player, dict) and pos_name in POSITION_MAP:
            position_lookup[player['id']] = POSITION_MAP[pos_name]

    # Build the team roster
    team_roster = []

    for batting_idx, player in enumerate(batting_order):
        if player is None:
            continue

        if isinstance(player, str):
            print(f"  Error: Batting order uses old format (player ID string)")
            return None

        player_id = player.get('id')
        if not player_id:
            continue

        char_id = resolve_character_id(player, mii_list)
        if char_id is None:
            continue

        field_pos = position_lookup.get(player_id)
        if field_pos is None:
            print(f"  Warning: No field position for {player.get('name', 'Unknown')}")
            continue

        team_roster.append([char_id, batting_idx, field_pos])

    if len(team_roster) != 9:
        print(f"  Warning: Team has {len(team_roster)} players instead of 9")

    if len(team_roster) < 1:
        return None

    return team_roster


def load_clb_saves(saves_dir: Path, mii_list: list) -> Tuple[list, list]:
    """
    Load all CLB lineup files from the saves directory.

    Args:
        saves_dir: Path to the saves directory
        mii_list: List of Mii objects from RFL_DB.dat

    Returns:
        Tuple of (teams, team_names) lists
    """
    teams = []
    team_names = []

    if not saves_dir.exists():
        print(f"Saves directory not found: {saves_dir}")
        return teams, team_names

    json_files = sorted(saves_dir.glob("*.json"))

    if not json_files:
        print(f"No .json files found in {saves_dir}")
        return teams, team_names

    print(f"Loading teams from {saves_dir}...")

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            team_name = data.get('name', json_file.stem)
            team_roster = convert_clb_lineup(data, mii_list)

            if team_roster:
                teams.append(team_roster)
                team_names.append(team_name)
                print(f"  Loaded: {team_name} ({len(team_roster)} players)")
            else:
                print(f"  Skipped: {json_file.name} (conversion failed)")

        except json.JSONDecodeError as e:
            print(f"  Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"  Error loading {json_file.name}: {e}")

    print(f"Loaded {len(teams)} team(s)")
    return teams, team_names


def autoteam_to_clb_format(team_roster: list, team_name: str, char_list: list) -> dict:
    """
    Convert AutoTeam format back to CLB export format.

    Args:
        team_roster: List of [character_id, batting_order, field_position]
        team_name: Name of the team
        char_list: Full character list (base characters + Miis)

    Returns:
        CLB export format dict
    """
    roster = {}
    batting_order = [None] * 9

    for char_id, batting_idx, field_pos in team_roster:
        # Get character name from char_list
        if char_id < len(char_list):
            char_name = char_list[char_id]
        else:
            char_name = f"Unknown_{char_id}"

        is_mii = char_id >= MII_START_INDEX

        # Create player object
        player = {
            "id": char_name.lower().replace(" ", "-"),
            "name": char_name,
            "databaseId": char_name if not is_mii else "Mii",
            "isMii": is_mii
        }

        # Add to roster at field position
        pos_name = POSITION_NAMES.get(field_pos, "P")
        roster[pos_name] = player

        # Add to batting order
        if 0 <= batting_idx < 9:
            batting_order[batting_idx] = player

    return {
        "name": team_name,
        "roster": roster,
        "battingOrder": batting_order,
        "bench": [],
        "chemistry": {"positive": 0, "negative": 0},
        "exportedAt": datetime.now().isoformat(),
        "season": "custom"
    }


def save_clb_lineup(saves_dir: Path, team_name: str, team_roster: list, char_list: list) -> bool:
    """
    Save a team as a CLB format JSON file.

    Args:
        saves_dir: Path to the saves directory
        team_name: Name of the team
        team_roster: List of [character_id, batting_order, field_position]
        char_list: Full character list (base characters + Miis)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure saves directory exists
        saves_dir.mkdir(exist_ok=True)

        # Convert to CLB format
        clb_data = autoteam_to_clb_format(team_roster, team_name, char_list)

        # Generate safe filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in team_name)
        filename = saves_dir / f"{safe_name}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clb_data, f, indent=2)

        print(f"Saved team to: {filename}")
        return True

    except Exception as e:
        print(f"Error saving team '{team_name}': {e}")
        return False


def delete_clb_lineup(saves_dir: Path, team_name: str) -> bool:
    """
    Delete a team's CLB JSON file.

    Args:
        saves_dir: Path to the saves directory
        team_name: Name of the team to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        # Generate safe filename (same logic as save)
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in team_name)
        filename = saves_dir / f"{safe_name}.json"

        if filename.exists():
            os.remove(filename)
            print(f"Deleted team file: {filename}")
            return True
        else:
            # Try to find by team name in file contents
            for json_file in saves_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    if data.get('name') == team_name:
                        os.remove(json_file)
                        print(f"Deleted team file: {json_file}")
                        return True
                except:
                    continue
            print(f"Team file not found for: {team_name}")
            return False

    except Exception as e:
        print(f"Error deleting team '{team_name}': {e}")
        return False


def get_team_filename(saves_dir: Path, team_name: str) -> Optional[Path]:
    """
    Find the filename for a team by name.

    Args:
        saves_dir: Path to the saves directory
        team_name: Name of the team

    Returns:
        Path to the team file, or None if not found
    """
    # Try direct filename match first
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in team_name)
    filename = saves_dir / f"{safe_name}.json"

    if filename.exists():
        return filename

    # Search by name in file contents
    for json_file in saves_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            if data.get('name') == team_name:
                return json_file
        except:
            continue

    return None
