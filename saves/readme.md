# Saves Directory

Place CLB (Comets League Baseball) LineupBuilder export files here.

## Usage

1. Go to the CLB Lineup Builder: https://cometsleague.baseball/tools/lineup
2. Build your team lineup
3. Click "Export" and save the `.json` file
4. Place the exported file in this `saves/` folder
5. Run AutoTeam - your team will appear in the dropdown automatically

## File Format

Each `.json` file should be a single team in CLB export format:

```json
{
  "name": "Team Name",
  "roster": {
    "P": { "id": "mario", "name": "Mario", "databaseId": "Mario", "isMii": false },
    "C": { "id": "luigi", "name": "Luigi", "databaseId": "Luigi", "isMii": false },
    ...
  },
  "battingOrder": [...],
  "chemistry": { "positive": 0, "negative": 0 },
  "exportedAt": "2024-01-15T10:30:00.000Z",
  "season": "current"
}
```

## Notes

- Teams created/edited via AutoTeam's Team Manager are also saved here
- Deleting a team in AutoTeam removes the corresponding `.json` file
- Files are loaded alphabetically by filename on startup
