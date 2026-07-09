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

match_metadata = matches_clean.copy()

event_frames = []

for match_id in tqdm(matches_df["match_id"]):

    events = sb.events(match_id=match_id)

    events["match_id"] = match_id

    metadata = match_metadata.loc[
        match_metadata["match_id"] == match_id
    ].iloc[0]

    events["competition_name"] = (
        metadata["competition_name"]
    )

    events["season"] = (
        metadata["season"]
    )

    event_frames.append(events)

events_df = pd.concat(
    event_frames,
    ignore_index=True
)

events_df.to_parquet("data/raw/events.parquet", index=False)

lineup_frames = []

for match_id in tqdm(matches_df["match_id"]):

    lineup = sb.lineups(match_id)

    metadata = match_metadata.loc[
        match_metadata["match_id"] == match_id
    ].iloc[0]

    for team_name, team_df in lineup.items():

        team_df["match_id"] = match_id

        team_df["team_name"] = team_name

        team_df["competition_name"] = (
            metadata["competition_name"]
        )

        team_df["season"] = (
            metadata["season"]
        )

        lineup_frames.append(team_df)

lineups_df = pd.concat(
    lineup_frames,
    ignore_index=True
)

lineups_df.to_parquet("data/raw/lineups.parquet", index=False)

print("Data ingestion complete.")