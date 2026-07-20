from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def time_to_seconds(time_str):
    """
    Converts StatsBomb time strings like '83:10'
    into total seconds.
    """
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds


def calculate_player_match_minutes(
    positions,
    match_end_seconds,
):
    """
    Calculate minutes played in a single match
    using StatsBomb position stints.
    """

    if len(positions) == 0:
        return 0.0

    total_seconds = 0

    for stint in positions:

        start_seconds = time_to_seconds(
            stint["from"]
        )

        if stint["to"] is not None:
            end_seconds = time_to_seconds(
                stint["to"]
            )
        else:
            end_seconds = match_end_seconds

        total_seconds += (
            end_seconds - start_seconds
        )

    return total_seconds / 60


def build_minutes() -> None:

    print("Loading data...")

    events = pd.read_parquet(
        RAW_DIR / "events.parquet"
    )

    lineups = pd.read_parquet(
        RAW_DIR / "lineups.parquet"
    )

    print("Building match end lookup...")

    half_end = (
        events.loc[events["type"] == "Half End"]
        .groupby("match_id")[["minute", "second"]]
        .max()
        .reset_index()
    )

    half_end["match_end_seconds"] = (
        half_end["minute"] * 60
        + half_end["second"]
    )

    match_end_lookup = dict(
        zip(
            half_end["match_id"],
            half_end["match_end_seconds"],
        )
    )

    print("Calculating match minutes...")

    minutes_df = lineups.copy()

    minutes_df["match_minutes"] = minutes_df.apply(
        lambda row: calculate_player_match_minutes(
            row["positions"],
            match_end_lookup[row["match_id"]],
        ),
        axis=1,
    )

    print("Aggregating player totals...")

    player_minutes_summary = (
        minutes_df.assign(
            played=lambda df: (
                df["positions"].apply(
                    lambda x: len(x) > 0
                )
            )
        )
        .groupby(
            [
                "player_id",
                "player_name",
                "season",
            ],
            as_index=False,
        )
        .agg(
            squad_matches=("match_id", "count"),
            appearances=("played", "sum"),
            bench_only=(
                "played",
                lambda x: (~x).sum(),
            ),
            minutes_played=(
                "match_minutes",
                "sum",
            ),
        )
    )

    player_minutes_summary[
        "minutes_played"
    ] = (
        player_minutes_summary[
            "minutes_played"
        ]
        .round()
        .astype(int)
    )

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PROCESSED_DIR
        / "player_minutes_summary.parquet"
    )

    player_minutes_summary.to_parquet(
        output_path,
        index=False,
    )

    print(
        f"Saved {len(player_minutes_summary)} players "
        f"to {output_path}"
    )

def main():

    build_minutes()

if __name__ == "__main__":
    main()