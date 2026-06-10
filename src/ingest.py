import pandas as pd
from statsbombpy import sb
from tqdm import tqdm

SEASONS = [
    (11, 27),
]

matches = []

for competition_id, season_id in SEASONS:
    season_matches = sb.matches(
        competition_id=competition_id,
        season_id=season_id
    )

    matches.append(season_matches)

matches_df = pd.concat(matches, ignore_index=True)

matches_clean = matches_df[
    [
        "match_id",
        "competition_name",
        "season"
    ]
].copy()

matches_clean.to_parquet("data/raw/matches.parquet", index=False)

event_frames = []

for match_id in tqdm(matches_df["match_id"]):
    events = sb.events(match_id=match_id)

    events["match_id"] = match_id

    event_frames.append(events)

events_df = pd.concat(
    event_frames,
    ignore_index=True
)

events_df.to_parquet("data/raw/events.parquet", index=False)

lineup_frames = []

for match_id in tqdm(matches_df["match_id"]):
    lineup = sb.lineups(match_id)

    for team_name, team_df in lineup.items():
        team_df["match_id"] = match_id
        team_df["team_name"] = team_name

        lineup_frames.append(team_df)

lineups_df = pd.concat(
    lineup_frames,
    ignore_index=True
)

lineups_df.to_parquet("data/raw/lineups.parquet", index=False)

print("Data ingestion complete.")