import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.library.http import STATS_HEADERS
from nba_api.stats.static import teams as nba_teams

NBA_API_HEADERS = STATS_HEADERS.copy()
NBA_API_TIMEOUT_SECONDS = 90
NBA_API_RETRIES = 3
NBA_API_RETRY_DELAY_SECONDS = 3

TEAM_META = {
    "Hawks": {"conference": "East", "division": "Southeast"},
    "Celtics": {"conference": "East", "division": "Atlantic"},
    "Nets": {"conference": "East", "division": "Atlantic"},
    "Hornets": {"conference": "East", "division": "Southeast"},
    "Bulls": {"conference": "East", "division": "Central"},
    "Cavaliers": {"conference": "East", "division": "Central"},
    "Mavericks": {"conference": "West", "division": "Southwest"},
    "Nuggets": {"conference": "West", "division": "Northwest"},
    "Pistons": {"conference": "East", "division": "Central"},
    "Warriors": {"conference": "West", "division": "Pacific"},
    "Rockets": {"conference": "West", "division": "Southwest"},
    "Pacers": {"conference": "East", "division": "Central"},
    "Clippers": {"conference": "West", "division": "Pacific"},
    "Lakers": {"conference": "West", "division": "Pacific"},
    "Grizzlies": {"conference": "West", "division": "Southwest"},
    "Heat": {"conference": "East", "division": "Southeast"},
    "Bucks": {"conference": "East", "division": "Central"},
    "Timberwolves": {"conference": "West", "division": "Northwest"},
    "Pelicans": {"conference": "West", "division": "Southwest"},
    "Knicks": {"conference": "East", "division": "Atlantic"},
    "Thunder": {"conference": "West", "division": "Northwest"},
    "Magic": {"conference": "East", "division": "Southeast"},
    "76ers": {"conference": "East", "division": "Atlantic"},
    "Suns": {"conference": "West", "division": "Pacific"},
    "Trail Blazers": {"conference": "West", "division": "Northwest"},
    "Kings": {"conference": "West", "division": "Pacific"},
    "Spurs": {"conference": "West", "division": "Southwest"},
    "Raptors": {"conference": "East", "division": "Atlantic"},
    "Jazz": {"conference": "West", "division": "Northwest"},
    "Wizards": {"conference": "East", "division": "Southeast"},
}

def get_current_season() -> str:
    today = date.today()
    start_year = today.year if today.month >= 7 else today.year - 1
    end_year = str(start_year + 1)[-2:]
    return f"{start_year}-{end_year}"

def parse_height_to_inches(height: str | None) -> int | None:
    if not height or "-" not in height:
        return None
    feet, inches = height.split("-")
    return int(feet) * 12 + int(inches)

def parse_age(birthdate: str | None) -> int | None:
    if not birthdate:
        return None
    born = pd.to_datetime(birthdate).date()
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def parse_jersey(jersey: object) -> int | None:
    jersey_raw = str(jersey or "").strip()
    return int(jersey_raw) if jersey_raw.isdigit() else None

def normalize_position(position: str) -> str:
    value = (position or "").strip().upper()
    if not value:
        return ""

    value = value.replace("FORWARD-CENTER", "F-C")
    value = value.replace("CENTER-FORWARD", "F-C")
    value = value.replace("GUARD-FORWARD", "G-F")
    value = value.replace("FORWARD-GUARD", "G-F")
    value = value.replace("GUARD-CENTER", "G-C")
    value = value.replace("CENTER-GUARD", "G-C")
    value = value.replace("FORWARD", "F")
    value = value.replace("GUARD", "G")
    value = value.replace("CENTER", "C")
    value = value.replace(" ", "")
    return value

def is_timeout_error(exc: Exception) -> bool:
    return isinstance(exc, TimeoutError) or "timed out" in str(exc).lower()

def fetch_with_retries(endpoint_class, **kwargs):
    for attempt in range(1, NBA_API_RETRIES + 1):
        try:
            return endpoint_class(
                headers=NBA_API_HEADERS,
                timeout=NBA_API_TIMEOUT_SECONDS,
                **kwargs,
            )
        except Exception as exc:
            if not is_timeout_error(exc) or attempt == NBA_API_RETRIES:
                raise

            delay = NBA_API_RETRY_DELAY_SECONDS * attempt
            print(
                f"{endpoint_class.__name__} timed out "
                f"(attempt {attempt}/{NBA_API_RETRIES}); retrying in {delay}s..."
            )
            time.sleep(delay)

def main():
    season = get_current_season()
    output = []

    for team in nba_teams.get_teams():
        team_name = team["nickname"]
        if team_name not in TEAM_META:
            continue

        try:
            roster_response = fetch_with_retries(
                commonteamroster.CommonTeamRoster,
                team_id=team["id"],
                season=season,
            )
            roster_df = roster_response.get_data_frames()[0]
        except Exception as exc:
            print(f"Skipping {team_name}: {exc}")
            continue

        for _, row in roster_df.iterrows():
            player = {
                "id": str(int(row["PLAYER_ID"])),
                "name": row["PLAYER"],
                "team": team_name,
                "conference": TEAM_META[team_name]["conference"],
                "division": TEAM_META[team_name]["division"],
                "position": normalize_position(str(row.get("POSITION", ""))),
                "heightInches": parse_height_to_inches(row.get("HEIGHT")),
                "age": parse_age(row.get("BIRTH_DATE")),
                "jersey": parse_jersey(row.get("NUM")),
                "imageUrl": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{int(row['PLAYER_ID'])}.png",
            }

            if (
                player["position"]
                and player["heightInches"] is not None
                and player["age"] is not None
            ):
                output.append(player)

        time.sleep(0.6)

    output.sort(key=lambda player: player["name"])

    out_path = Path("src/data/players.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Wrote {len(output)} players to {out_path}")

if __name__ == "__main__":
    main()
