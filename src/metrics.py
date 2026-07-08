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