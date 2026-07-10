from pathlib import Path

import pandas as pd

from config.role_config import (
    ROLE_METRICS,
    DISPLAY_NAMES,
    LOWER_IS_BETTER,
)

PROFILES_PATH = Path("data/processed/player_profiles.parquet")

def calculate_percentile(series, ascending=False):
    return series.rank(
        pct=True,
        ascending=ascending
    ) * 100

profiles = pd.read_parquet(PROFILES_PATH)

roles = sorted(profiles["role"].unique())

for i, role in enumerate(roles, start=1):
    print(f"{i}. {role}")

role_idx = int(input("\nSelect role: ")) - 1
selected_role = roles[role_idx]

print("\nComparison scope:")
print("1. Competition + Season")
print("2. Season")
print("3. Global")

scope = input("> ")

