import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import commonallplayers, commonplayerinfo

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
    "Sixers": {"conference": "East", "division": "Atlantic"},
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

def main():
    season = get_current_season()

    players_response = commonallplayers.CommonAllPlayers(
        is_only_current_season=1,
        league_id="00",
        season=season,
    )
    players_df = players_response.get_data_frames()[0]

    output = []

    for _, row in players_df.iterrows():
        player_id = int(row["PERSON_ID"])
        team_name = row["TEAM_NAME"]
        player_name = row["DISPLAY_FIRST_LAST"]

        if not team_name or team_name not in TEAM_META:
            continue

        try:
            info_response = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            info_df = info_response.get_data_frames()[0]
            info = info_df.iloc[0]

            jersey_raw = str(info.get("JERSEY", "")).strip()
            jersey = int(jersey_raw) if jersey_raw.isdigit() else None

            player = {
                "id": str(player_id),
                "name": player_name,
                "team": team_name,
                "conference": TEAM_META[team_name]["conference"],
                "division": TEAM_META[team_name]["division"],
                "position": normalize_position(str(info.get("POSITION", ""))),
                "heightInches": parse_height_to_inches(info.get("HEIGHT")),
                "age": parse_age(info.get("BIRTHDATE")),
                "jersey": jersey,
                "imageUrl": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",
            }

            if (
                player["position"]
                and player["heightInches"] is not None
                and player["age"] is not None
            ):
                output.append(player)

            time.sleep(0.6)

        except Exception as exc:
            print(f"Skipping {player_name}: {exc}")

    output.sort(key=lambda player: player["name"])

    out_path = Path("src/data/players.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Wrote {len(output)} players to {out_path}")

if __name__ == "__main__":
    main()