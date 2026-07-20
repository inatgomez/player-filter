from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
import uuid

from metrics import (
    compute_team_match_possession,
    deep_progressions,
    open_play_xg_assisted,
    turnovers,
    aerial_win_pct,
    padj_tackles_interceptions,
    padj_pressures,
    fouls,
    tackle_dribbled_past_pct,
    touches_in_box,
    shots,
    npxg,
    fouls_won,
)

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

EVENTS_PATH = RAW_DIR / "events.parquet"

MINUTES_PATH = PROCESSED_DIR / "player_minutes_summary.parquet"

POPULATIONS_PATH = PROCESSED_DIR / "player_populations.parquet"

OUTPUT_PATH = PROCESSED_DIR / "player_profiles.parquet"

PROFILE_KEY = [
    "player_id",
    "season",
]

PROFILE_NAMESPACE = uuid.UUID(
    "3d1bb8a4-1f91-4f7d-a86f-2f4b89a3e001"
)

def report_shape(name, df):
    print(f"{name:<35} {df.shape}")


def validate_unique_key(
    df,
    key_cols,
    name,
):

    duplicates = (
        df.duplicated(key_cols)
        .sum()
    )

    if duplicates:

        raise ValueError(
            f"{name}: "
            f"{duplicates} duplicate rows "
            f"for key {key_cols}"
        )
    
def merge_metric_tables(metric_tables):

    profiles = reduce(
        lambda left, right:
        left.merge(
            right,
            on=[
                "player_id",
                "season",
            ],
            how="outer",
            validate="one_to_one",
        ),
        metric_tables,
    )

    return profiles

def add_per90_metrics(df):

    per90_metrics = [
        "deep_progressions",
        "open_play_xg_assisted",
        "turnovers",
        "padj_tackles_interceptions",
        "padj_pressures",
        "fouls",
        "touches_in_box",
        "shots",
        "npxg",
        "fouls_won",
    ]

    for metric in per90_metrics:

        df[f"{metric}_per90"] = (
            df[metric]
            / df["minutes_played"]
            * 90
        )

    return df

def add_derived_metrics(df):

    df["npxg_per_shot"] = np.where(
        df["shots"] > 0,
        df["npxg"] / df["shots"],
        np.nan,
    )

    return df

def add_profile_id(df):

    keys = (
        df["player_id"].astype(str)
        + "|"
        + df["competition_name"]
        + "|"
        + df["season"]
        + "|"
        + df["role"]
    )

    df["profile_id"] = keys.map(
        lambda x: str(
            uuid.uuid5(
                PROFILE_NAMESPACE,
                x
            )
        )
    )

    return df

def main():
    
    print("\nLoading data...\n")

    events = pd.read_parquet(EVENTS_PATH)

    populations = pd.read_parquet(POPULATIONS_PATH)

    minutes = pd.read_parquet(MINUTES_PATH)

    report_shape("events", events)
    report_shape("populations", populations)
    report_shape("minutes", minutes)

    possession_table = (compute_team_match_possession(events))

    metric_tables = [

        deep_progressions(events),

        open_play_xg_assisted(events),

        turnovers(events),

        aerial_win_pct(events),

        padj_tackles_interceptions(
            events,
            possession_table,
        ),

        padj_pressures(
            events,
            possession_table,
        ),

        fouls(events),

        tackle_dribbled_past_pct(events),

        touches_in_box(events),

        shots(events),

        npxg(events),

        fouls_won(events),
    ]

    profiles = merge_metric_tables(metric_tables)

    profiles = populations.merge(
    profiles,
    on=[
        "player_id",
        "season",
    ],
    how="left",
    validate="many_to_one",
    )

    profiles = profiles.merge(
    minutes[
        [
            "player_id",
            "season",
            "minutes_played",
            "appearances",
            "squad_matches",
        ]
    ],
    on=[
        "player_id",
        "season",
    ],
    how="left",
    validate="many_to_one",
    )

    missing_minutes = (
        profiles["minutes_played"]
        .isna()
        .sum()
    )

    if missing_minutes:

        raise ValueError(
            f"{missing_minutes} players "
            f"missing minutes."
        )
    
    count_metrics = [
        "deep_progressions",
        "open_play_xg_assisted",
        "turnovers",
        "padj_tackles_interceptions",
        "padj_pressures",
        "fouls",
        "touches_in_box",
        "shots",
        "npxg",
        "fouls_won",
    ]

    profiles[count_metrics] = (
        profiles[count_metrics]
        .fillna(0)
    )

    profiles = add_derived_metrics(
        profiles
    )

    profiles = add_per90_metrics(
        profiles
    )

    duplicates = (
        profiles.duplicated(
            subset=[
                "player_id",
                "competition_name",
                "role",
                "season",
            ]
        )
        .sum()
    )

    if duplicates:

        raise ValueError(
            f"{duplicates} duplicate "
            f"player-role-season rows."
        )
    
    profiles = add_profile_id(
    profiles
    )

    validate_unique_key(
    profiles,
    ["profile_id"],
    "profiles",
    )
    
    report_shape(
        "profiles",
        profiles,
    )

    profiles.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved:\n{OUTPUT_PATH}\n"
    )

if __name__ == "__main__":
    main()