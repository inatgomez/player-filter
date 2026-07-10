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

population = profiles[
    profiles["role"] == selected_role
].copy()

if scope == "1":

    competitions = sorted(
        population["competition_name"].unique()
    )

    for i, comp in enumerate(competitions, start=1):
        print(f"{i}. {comp}")

    comp_idx = int(input("\nSelect competition: ")) - 1
    selected_comp = competitions[comp_idx]

    seasons = sorted(
        population.loc[
            population["competition_name"] == selected_comp,
            "season"
        ].unique()
    )

    for i, season in enumerate(seasons, start=1):
        print(f"{i}. {season}")

    season_idx = int(input("\nSelect season: ")) - 1
    selected_season = seasons[season_idx]

    population = population[
        (population["competition_name"] == selected_comp)
        &
        (population["season"] == selected_season)
    ]

elif scope == "2":

    seasons = sorted(
        population["season"].unique()
    )

    for i, season in enumerate(seasons, start=1):
        print(f"{i}. {season}")

    season_idx = int(input("\nSelect season: ")) - 1
    selected_season = seasons[season_idx]

    population = population[
        population["season"] == selected_season
    ]

default_minutes = 900

minutes = input(
    f"\nMinimum minutes [{default_minutes}]: "
).strip()

min_minutes = (
    int(minutes)
    if minutes
    else default_minutes
)

population = population[
    population["minutes_played"] >= min_minutes
].copy()

metrics = ROLE_METRICS[selected_role]

print("\nRanking metric:")

for i, metric in enumerate(metrics, start=1):
    print(
        f"{i}. {DISPLAY_NAMES[metric]}"
    )

metric_idx = int(input("> ")) - 1
selected_metric = metrics[metric_idx]

