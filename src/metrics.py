import numpy as np
import pandas as pd

GROUP_COLS = ["player_id", "player_name"]

def validate_columns(df:pd.DataFrame, required:list[str], name:str) -> None:
    """
    Raise an informative error if required columns are missing.
    """

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"{name}: missing required columns: {missing}"
        )
    
def validate_unique_player_rows(df:pd.DataFrame, metric_name:str) -> None:
    """
    Ensure each metric returns exactly one row per player.
    """

    duplicates = df.duplicated(GROUP_COLS).sum()

    if duplicates:
        raise ValueError (
            f"{metric_name}: found {duplicates} duplicated player rows."
        )
    
def empty_metric(metric_name:str) -> pd.DataFrame:
    """
    Standard empty return shape.
    """

    return pd.DataFrame(
        columns=GROUP_COLS + [metric_name]
    )

def compute_team_match_possession(events:pd.DataFrame) -> pd.DataFrame:
    """
    Team possession by match.
    
    possession = 
    team_passes /
    (team_passes + opponent_passes)
    """

    validate_columns(
        events,
        ["match_id", "team", "type"],
        "compute_team_match_possession"
    )

    passes = events.loc[
        events["type"] == "Pass"
    ]

    team_passes = (
        passes.groupby(["match_id", "team"])
        .size()
        .reset_index(name="team_passes")
    )

    possession_rows = []

    for match_id, match_df in team_passes.groupby("match_id"):

        if len(match_df) != 2: 
            continue

        row_a = match_df.iloc[0]
        row_b = match_df.iloc[1]

        possession_rows.append(
            {
                "match_id": match_id,
                "team": row_a["team"],
                "team_passes": row_a["team_passes"],
                "opponent_passes": row_b["team_passes"],
            }
        )

        possession_rows.append(
            {
                "match_id": match_id,
                "team": row_b["team"],
                "team_passes": row_b["team_passes"],
                "opponent_passes": row_a["team_passes"],
            }
        )

        possession = pd.DataFrame(possession_rows)

        possession["possession"] = (
            possession["team_passes"] /
            (
                possession["team_passes"] + possession["opponent_passes"]
            )
        )

        possession["adjustment_factor"] = (
            2 /
            (
                1 + np.exp(-10 * (possession["possession"] - 0.5))
            )
        )

        return possession
    
