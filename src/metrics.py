import numpy as np
import pandas as pd

GROUP_COLS = [
    "player_id",
    "player_name",
    "season",
]

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

    duplicates = df.duplicated(
    [
        "player_id",
        "season",
    ]
    ).sum()

    if duplicates:
        raise ValueError (
            f"{metric_name}: found {duplicates} duplicated player rows."
        )
    
    if len(df) == 0:
        raise ValueError (
            f"{metric_name}: returned 0 rows"
        )
    
    print(
        f"{metric_name}: "
        f"{len(df):,} rows"
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
    
def deep_progressions(events: pd.DataFrame) -> pd.DataFrame:
    """
    Completed passes and carries entering final third.
    """

    required = [ 
        "player_id", 
        "player",
        "season", 
        "type", 
        "location", 
        "pass_end_location", 
        "carry_end_location" 
    ]
    
    validate_columns(events, required, "deep_progressions")

    actions = events.loc[ 
        events["type"].isin(["Pass", "Carry"]) 
    ].copy()
    
    start_x = actions["location"].str[0]

    end_x = np.where( 
        actions["type"] == "Pass", 
        actions["pass_end_location"].str[0], 
        actions["carry_end_location"].str[0] 
    )
    
    entered_final_third = ( 
        start_x < 80 
        ) & ( 
        end_x >= 80 
    )

    completed_pass = (
        (events["type"] == "Pass")
        & (events["pass_outcome"].isna())
    )

    carry = events["type"] == "Carry"

    result = (
        actions.loc[entered_final_third & completed_pass | carry]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(name="deep_progressions")
        .rename(columns={"player": "player_name"})
    )
    
    validate_unique_player_rows(result, "deep_progressions") 
    
    return result

def turnovers(events: pd.DataFrame) -> pd.DataFrame:
    """
    Miscontrols + failed dribbles.
    """

    validate_columns(
        events,
        ["player_id", "player", "season", "type", "outcome"],
        "turnovers"
    )

    miscontrols = (events["type"] == "Miscontrol")

    failed_dribbles = (
        events["type"] == "Dribble") & (events["dribble_outcome"] != "Complete"
    )

    turnover_events = miscontrols | failed_dribbles

    result = (
        events.loc[turnover_events]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(name="turnovers")
        .rename(columns={"player": "player_name"})
    )

    validate_unique_player_rows(result, "turnovers")

    return result

def fouls(events: pd.DataFrame) -> pd.DataFrame:
    """
    Fouls committed count.
    """

    validate_columns(events, ["player_id", "player", "season", "type"], "fouls")

    result = (
        events.loc[events["type"] == "Foul"]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(name="fouls")
        .rename(columns={"player": "player_name"})
    )

    validate_unique_player_rows(result, "fouls")

    return result

def fouls_won(events:pd.DataaFrame) -> pd.DataFrame:
    """
    Fouls won count.
    """

    validate_columns(events, ["player_id", "player", "season", "type"], "fouls_won")

    result = (
        events.loc[events["type"] == "Foul Won"]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(name="fouls_won")
        .rename(columns={"player": "player_name"})
    )

    validate_unique_player_rows(result, "fouls_won")

    return result

def shots(events: pd.DataFrame) -> pd.DataFrame:
    """
    Shot count.
    """
    
    validate_columns(
        events,
        ["player_id", "player", "season", "type"],
        "shots"
    )

    result = (
        events.loc[events["type"] == "Shot"]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(name="shots")
        .rename(columns={"player": "player_name"})
    )

    validate_unique_player_rows(
        result,
        "shots"
    )

    return result

def npxg(events: pd.DataFrame) -> pd.DataFrame:
    """
    Non-penalty xG.
    """
    validate_columns(
        events,
        [
            "player_id",
            "player",
            "season",
            "type",
            "shot_statsbomb_xg",
            "shot_type"
        ],
        "npxg"
    )

    shots_df = events.loc[
        events["type"] == "Shot"
    ]

    npxg_df = shots_df.loc[
        shots_df["shot_type"] != "Penalty"
    ]

    result = (
        npxg_df
        .groupby(
            GROUP_COLS
        )["shot_statsbomb_xg"]
        .sum()
        .reset_index(name="npxg")
        .rename(columns={"player": "player_name"})
    )

    validate_unique_player_rows(
        result,
        "npxg"
    )

    return result

def npxg_per_shot(npxg_df: pd.DataFrame, shots_df: pd.DataFrame,) -> pd.DataFrame:

    result = (
        npxg_df.merge(
            shots_df,
            on=GROUP_COLS,
            how="outer",
            validate="one_to_one",
        )
        .fillna(0)
    )

    result["npxg_per_shot"] = np.where(
        result["shots"] > 0,
        result["npxg"] / result["shots"],
        np.nan,
    )

    return result[
        GROUP_COLS
        + ["npxg_per_shot"]
    ]

def open_play_xg_assisted(events: pd.DataFrame) -> pd.DataFrame:
    """
    Sum of xG from open-play shots assisted by the player.
    """

    validate_columns(events, ["player_id", "player_name", "season","type", "shot_type", "shot_statsbomb_xg", "pass_assisted_shot_id"], "open_play_xg_assisted")

    shots = (
        events.loc[
            (events["type"] == "Shot")
            &
            (events["shot_type"] == "Open Play")
        ,
            [
                "id",
                "shot_statsbomb_xg",
            ]
        ]
        .rename(
            columns={
                "id": "shot_id"
            }
        )
    )

    assists = (
        events.loc[
            events["pass_assisted_shot_id"].notna(),
            [
                "player_id",
                "player_name",
                "pass_assisted_shot_id",
            ]
        ]
    )

    assisted_shots = assists.merge(
        shots,
        left_on="pass_assisted_shot_id",
        right_on="shot_id",
        how="inner",
        validate="many_to_one",
    )

    result = (
        assisted_shots
        .groupby(GROUP_COLS)["shot_statsbomb_xg"]
        .sum()
        .reset_index(name="open_play_xg_assisted")
    )

    validate_unique_player_rows(
        result,
        "open_play_xg_assisted"
    )

    return result

def aerial_win_pct(events: pd.DataFrame) -> pd.DataFrame:
    """
    Aerial duels a player enters and wins.
    """

    validate_columns(events, ["player_id", "player_name", "season", "type", "duel_type", "pass_aerial_won", "clearance_aerial_won", "shot_aerial_won", "miscontrol_aerial_won"], "aerial_win_pct")

    aerial_wins = (
        (
            (events["type"] == "Pass")
            & (events["pass_aerial_won"] == True)
        )
        |
        (
            (events["type"] == "Clearance")
            & (events["clearance_aerial_won"] == True)
        )
        |
        (
            (events["type"] == "Shot")
            & (events["shot_aerial_won"] == True)
        )
        |
        (
            (events["type"] == "Miscontrol")
            & (events["miscontrol_aerial_won"] == True)
        )
    )

    aerial_losses = (
        events["duel_type"] == "Aerial Lost"
    )

    wins = (
        events.loc[aerial_wins]
        .groupby(GROUP_COLS)
        .size()
        .rename("wins")
    )

    losses = (
        events.loc[aerial_losses]
        .groupby(GROUP_COLS)
        .size()
        .rename("losses")
    )

    result = (
        pd.concat([wins, losses], axis=1)
        .fillna(0)
        .reset_index()
    )

    denom = (
        result["wins"]
        + result["losses"]
    )

    result["aerial_win_pct"] = np.where(
        denom > 0,
        result["wins"] / denom,
        np.nan,
    )

    validate_unique_player_rows(result, "aerial_win_pct")

    return result[
        GROUP_COLS + ["aerial_win_pct"]
    ]

def padj_tackles_interceptions(events: pd.DataFrame, possession_table: pd.DataFrame,) -> pd.DataFrame:
    """
    Tackles + interceptions adjusted by match possession.
    """

    validate_columns(events, ["player_id", "player_name", "season", "match_id", "team", "type", "duel_type"], "padj_tackles_interceptions")

    tackles = (
        events["type"] == "Duel"
        &
        events["duel_type"] == "Tackle"
    )

    interceptions = (
        events["type"] == "Interception"
    )

    actions = events.loc[
        tackles | interceptions,
        [
            "player_id",
            "player_name",
            "match_id",
            "team",
        ]
    ].copy()

    actions = actions.merge(
        possession_table[
            [
                "match_id",
                "team",
                "adjustment_factor",
            ]
        ],
        on=["match_id", "team"],
        how="left",
        validate="many_to_one",
    )

    result = (
        actions
        .groupby(GROUP_COLS)["adjustment_factor"]
        .sum()
        .reset_index(
            name="padj_tackles_interceptions"
        )
    )

    validate_unique_player_rows(result, "padj_tackles_interceptions")

    return result

def padj_pressures(events: pd.DataFrame, possession_table: pd.DataFrame,) -> pd.DataFrame:
    """
    Interceptions adjusted by possession.
    """

    validate_columns(events, ["player_id", "player_name", "season", "match_id", "team", "type"], "padj_pressures")

    interceptions = events.loc[
        events["type"] == "Interception",
        [
            "player_id",
            "player_name",
            "season",
            "match_id",
            "team",
        ]
    ].copy()

    interceptions = interceptions.merge(
        possession_table[
            [
                "match_id",
                "team",
                "adjustment_factor",
            ]
        ],
        on=["match_id", "team"],
        how="left",
        validate="many_to_one",
    )

    result = (
        interceptions
        .groupby(GROUP_COLS)["adjustment_factor"]
        .sum()
        .reset_index(name="padj_pressures")
    )

    validate_unique_player_rows(result, "padj_pressures")

    return result

def tackle_dribbled_past_pct(events: pd.DataFrame,) -> pd.DataFrame:
    """
    Percentage of duels a player wins when they are dribbled at.
    """

    validate_columns(events, ["player_id", "player_name", "season", "type", "duel_type"], "tackle_dribbled_past_pct")

    tackles = (
        events.loc[
            events["duel_type"] == "Tackle"
        ]
        .groupby(GROUP_COLS)
        .size()
        .rename("tackles")
    )

    dribbled_past = (
        events.loc[
            events["type"] == "Dribbled Past"
        ]
        .groupby(GROUP_COLS)
        .size()
        .rename("dribbled_past")
    )

    result = (
        pd.concat(
            [tackles, dribbled_past],
            axis=1,
        )
        .fillna(0)
        .reset_index()
    )

    denom = (
        result["tackles"]
        + result["dribbled_past"]
    )

    result["tackle_dribbled_past_pct"] = np.where(
        denom > 0,
        result["tackles"] / denom,
        np.nan,
    )

    validate_unique_player_rows(result, "tackle_dribbled_past_pct")

    return result[
        GROUP_COLS
        + ["tackle_dribbled_past_pct"]
    ]

def touches_in_box(events: pd.DataFrame) -> pd.DataFrame:
    """
    Touches in opposition box.

    Included:

    - completed passes (offside passes allowed)
    - completed dribbles
    - successful tackles
    - successful interceptions
    - clearances
    - shots
    - blocks
    - ball receipts

    Location:
    x >= 102
    18 <= y <= 62
    """

    validate_columns(events, ["player_id", "player_name", "season","type", "location", "pass_outcome", "dribble_outcome", "duel_type", "duel_outcome", "interception_outcome"], "touches_in_box")

    x = events["location"].str[0]
    y = events["location"].str[1]

    in_box = (
        (x >= 102)
        &
        (y >= 18)
        &
        (y <= 62)
    )

    completed_pass = (
        (events["type"] == "Pass")
        &
        (
            events["pass_outcome"].isna()
            |
            (
                events["pass_outcome"]
                == "Pass Offside"
            )
        )
    )

    completed_dribble = (
        (events["type"] == "Dribble")
        &
        (
            events["dribble_outcome"]
            == "Complete"
        )
    )

    successful_tackle = (
        (events["type"] == "Duel")
        &
        (
            events["duel_type"]
            == "Tackle"
        )
        &
        (
            ~events["duel_outcome"].isin(
        [
            "Lost In Play",
            "Lost Out"
        ]
            )
        )
    )

    successful_interception = (
        (events["type"] == "Interception")
        &
        (
            events["interception_outcome"]
            .isin(
                [
                    "Won",
                    "Success",
                    "Success In Play",
                    "Success Out",
                ]
            )
        )
    )

    clearance = (
        events["type"] == "Clearance"
    )

    shot = (
        events["type"] == "Shot"
    )

    block = (
        events["type"] == "Block"
    )

    receipt = (
        events["type"] == "Ball Receipt*"
    )

    valid_touch = (
        completed_pass
        |
        completed_dribble
        |
        successful_tackle
        |
        successful_interception
        |
        clearance
        |
        shot
        |
        block
        |
        receipt
    )

    result = (
        events.loc[
            valid_touch
            &
            in_box
        ]
        .groupby(GROUP_COLS)
        .size()
        .reset_index(
            name="touches_in_box"
        )
    )

    validate_unique_player_rows(
        result,
        "touches_in_box"
    )

    return result

