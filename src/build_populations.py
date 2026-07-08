"""
build_populations.py

Build player role populations from StatsBomb lineups and events data.

Output:
    data/processed/player_populations.parquet

One row per:
    player_id
    season
    competition_name
    role

Membership is determined using event position share thresholds.
Lineup shares are retained for auditing purposes.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

LINEUPS_PATH = RAW_DIR / "lineups.parquet"
EVENTS_PATH = RAW_DIR / "events.parquet"
MATCHES_PATH = RAW_DIR / "matches.parquet"

OUTPUT_PATH = OUTPUT_DIR / "player_populations.parquet"

FULL_BACK_THRESHOLD = 0.60
DEFENSIVE_MIDFIELDER_THRESHOLD = 0.50
CREATIVE_MIDFIELDER_THRESHOLD = 0.50


ROLE_DEFINITIONS = {
    "Full Back": {
        "labels": [
            "Left Back",
            "Right Back",
            "Left Wing Back",
            "Right Wing Back",
        ],
        "threshold": FULL_BACK_THRESHOLD,
    },
    "Defensive Midfielder": {
        "labels": [
            "Center Defensive Midfield",
            "Left Defensive Midfield",
            "Right Defensive Midfield",
        ],
        "threshold": DEFENSIVE_MIDFIELDER_THRESHOLD,
    },
    "Creative Midfielder": {
        "labels": [
            "Center Midfield",
            "Left Midfield",
            "Right Midfield",
            "Left Center Midfield",
            "Right Center Midfield",
            "Center Attacking Midfield",
            "Left Attacking Midfield",
            "Right Attacking Midfield",
        ],
        "threshold": CREATIVE_MIDFIELDER_THRESHOLD,
    },
}


# ============================================================================
# HELPERS
# ============================================================================

def extract_positions(position_history):
    """
    Extract position labels from StatsBomb lineup position history.
    """
    if not isinstance(position_history, (list, tuple, np.ndarray)):
        return []

    return [
        stint["position"]
        for stint in position_history
        if isinstance(stint, dict) and "position" in stint
    ]


def build_lineup_position_shares(lineups, matches):
    """
    Calculate lineup-based position shares per player-season.
    """

    lineups = lineups.merge(
        matches,
        on="match_id",
        how="left"
    )

    lineups["position_list"] = (
        lineups["positions"]
        .apply(extract_positions)
    )

    positions_long = (
        lineups[
            [
                "player_id",
                "player_name",
                "competition_name",
                "season",
                "position_list",
            ]
        ]
        .explode("position_list")
        .rename(columns={"position_list": "position"})
        .dropna(subset=["position"])
    )

    position_counts = (
        positions_long
        .groupby(
            [
                "player_id",
                "player_name",
                "competition_name",
                "season",
                "position",
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "appearances"})
    )

    totals = (
        position_counts
        .groupby(
            [
                "player_id",
                "player_name",
                "competition_name",
                "season",
            ],
            as_index=False,
        )["appearances"]
        .sum()
        .rename(columns={"appearances": "total_appearances"})
    )

    shares = position_counts.merge(
        totals,
        on=[
            "player_id",
            "player_name",
            "competition_name",
            "season",
        ],
        how="left",
    )

    shares["position_share"] = (
        shares["appearances"]
        / shares["total_appearances"]
    )

    return shares


def build_event_position_shares(events, matches):
    """
    Calculate event-based position shares per player-season.
    """

    events = events.merge(
        matches,
        on="match_id",
        how="left"
    )

    position_counts = (
        events
        .dropna(subset=["player_id", "position"])
        .groupby(
            [
                "player_id",
                "player",
                "competition_name",
                "season",
                "position",
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "events"})
    )

    totals = (
        position_counts
        .groupby(
            [
                "player_id",
                "player",
                "competition_name",
                "season",
            ],
            as_index=False,
        )["events"]
        .sum()
        .rename(columns={"events": "total_events"})
    )

    shares = position_counts.merge(
        totals,
        on=[
            "player_id",
            "player",
            "competition_name",
            "season",
        ],
        how="left",
    )

    shares["position_share"] = (
        shares["events"]
        / shares["total_events"]
    )

    return shares


def get_role_shares(
    shares_df,
    labels,
    player_col,
):
    """
    Aggregate position shares into role shares.
    """

    return (
        shares_df[
            shares_df["position"].isin(labels)
        ]
        .groupby(
            [
                "player_id",
                player_col,
                "competition_name",
                "season",
            ],
            as_index=False,
        )["position_share"]
        .sum()
        .rename(
            columns={
                player_col: "player_name",
            }
        )
    )


# ============================================================================
# MAIN
# ============================================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading data...")

    lineups = pd.read_parquet(LINEUPS_PATH)
    events = pd.read_parquet(EVENTS_PATH)
    matches = pd.read_parquet(MATCHES_PATH)

    print("Building position shares...")

    lineup_shares = build_lineup_position_shares(
        lineups,
        matches,
    )

    event_shares = build_event_position_shares(
        events,
        matches,
    )

    population_tables = []

    for role_name, config in ROLE_DEFINITIONS.items():

        labels = config["labels"]
        threshold = config["threshold"]

        lineup_role = (
            get_role_shares(
                lineup_shares,
                labels,
                "player_name",
            )
            .rename(
                columns={
                    "position_share": "lineup_share",
                }
            )
        )

        event_role = (
            get_role_shares(
                event_shares,
                labels,
                "player",
            )
            .rename(
                columns={
                    "position_share": "event_share",
                }
            )
        )

        role_population = (
            lineup_role
            .merge(
                event_role,
                on=[
                    "player_id",
                    "player_name",
                    "competition_name",
                    "season",
                ],
                how="outer",
            )
            .fillna(0)
        )

        role_population = role_population[
            role_population["event_share"] >= threshold
        ].copy()

        role_population["role"] = role_name

        population_tables.append(
            role_population[
                [
                    "player_id",
                    "player_name",
                    "competition_name",
                    "season",
                    "role",
                    "lineup_share",
                    "event_share",
                ]
            ]
        )

    populations = (
        pd.concat(
            population_tables,
            ignore_index=True,
        )
        .sort_values(
            [
                "competition_name",
                "season",
                "role",
                "player_name",
            ]
        )
        .reset_index(drop=True)
    )

    populations.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Saved {len(populations):,} rows to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()