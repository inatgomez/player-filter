from pathlib import Path

import pandas as pd

from config.role_config import (
    ROLE_METRICS,
    DISPLAY_NAMES,
    LOWER_IS_BETTER,
)
from radar import generate_radars

PROFILES_PATH = Path(
    "data/processed/player_profiles.parquet"
)

DEFAULT_MIN_MINUTES = 900

def load_profiles() -> pd.DataFrame:

    if not PROFILES_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {PROFILES_PATH}"
        )

    return pd.read_parquet(PROFILES_PATH)

def choose_option(options, prompt):

    while True:

        try:

            choice = int(input(prompt)) - 1

            if 0 <= choice < len(options):
                return options[choice]

        except ValueError:
            pass

        print("Invalid selection.")


def add_population_percentiles(
    population: pd.DataFrame,
    metrics: list[str],
    ) -> pd.DataFrame:

    population = population.copy()

    for metric in metrics:

        lower_is_better = (
            metric in LOWER_IS_BETTER
        )

        population[f"{metric}_pct"] = (
            population[metric]
            .rank(
                pct=True,
                ascending=not lower_is_better,
            )
            .mul(100)
            .round(1)
        )

    return population

def print_header(title):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def build_population(
    profiles: pd.DataFrame,
    role: str,
):

    population = profiles[
        profiles["role"] == role
    ].copy()

    print_header("Comparison Scope")

    print("1. Competition + Season")
    print("2. Season")
    print("3. Global")

    scope = input("\nSelect option: ").strip()

    if scope == "1":

        competitions = sorted(
            population["competition_name"].unique()
        )

        print_header("Choose at least one competition")
        print()

        for i, comp in enumerate(
            competitions,
            start=1,
        ):
            print(f"{i}. {comp}")

        competition = choose_option(
            competitions,
            "\nCompetition: ",
        )

        population = population[
            population["competition_name"]
            == competition
        ]

        seasons = sorted(
            population["season"].unique()
        )

        print_header("Choose at least one season")
        print()

        for i, season in enumerate(
            seasons,
            start=1,
        ):
            print(f"{i}. {season}")

        season = choose_option(
            seasons,
            "\nSeason: ",
        )

        population = population[
            population["season"] == season
        ]

    elif scope == "2":

        seasons = sorted(
            population["season"].unique()
        )

        print_header("Choose at least one season")
        print()

        for i, season in enumerate(
            seasons,
            start=1,
        ):
            print(f"{i}. {season}")

        season = choose_option(
            seasons,
            "\nSeason: ",
        )

        population = population[
            population["season"] == season
        ]

    elif scope == "3":

        print(
            "\nWarning: Global populations may mix "
            "different competitions and seasons."
        )

    else:

        print("Invalid selection.")
        return build_population(
            profiles,
            role,
        )

    return population

def build_filtered_population(
    profiles: pd.DataFrame,
    role: str,
) -> pd.DataFrame:

    population = build_population(
        profiles,
        role,
    )

    minutes_input = input(
        f"\nMinimum minutes "
        f"[{DEFAULT_MIN_MINUTES}]: "
    ).strip()

    min_minutes = (
        int(minutes_input)
        if minutes_input
        else DEFAULT_MIN_MINUTES
    )

    population = population[
        population["minutes_played"]
        >= min_minutes
    ].copy()

    if population.empty:

        print(
            "\nNo players satisfy "
            "the selected filters."
        )

        return pd.DataFrame()

    population = add_population_percentiles(
        population,
        ROLE_METRICS[role],
    )

    return population

def ranking_flow(profiles):

    print_header("Role Selection")

    roles = sorted(
        profiles["role"].unique()
    )

    for i, role in enumerate(
        roles,
        start=1,
    ):
        print(f"{i}. {role}")

    role = choose_option(
        roles,
        "\nRole: ",
    )

    population = build_filtered_population(
    profiles,
    role,
    )

    if population.empty:
        return

    metrics = ROLE_METRICS[role]

    print_header("Ranking Metric")

    for i, metric in enumerate(
        metrics,
        start=1,
    ):
        print(
            f"{i}. "
            f"{DISPLAY_NAMES[metric]}"
        )

    metric = choose_option(
        metrics,
        "\nMetric: ",
    )

    lower_is_better = (
        metric in LOWER_IS_BETTER
    )

    population["percentile"] = (
        population[f"{metric}_pct"]
    )

    population = population.sort_values(
        metric,
        ascending=lower_is_better,
    ).reset_index(drop=True)

    display_cols = [
        "profile_id",
        "player_name",
        "competition_name",
        "season",
        "minutes_played",
        "role",
        metric,
        "percentile",
    ]

    print_header(
        f"Top Players "
        f"({DISPLAY_NAMES[metric]})"
    )

    print(
        population[display_cols]
        .head(10)
        .to_string(index=True)
    )

    radar_prompt(population)

def search_flow(profiles):

    print_header("Player Search")

    query = input(
        "Player name: "
    ).strip()

    matches = profiles[
        profiles["player_name"]
        .str.contains(
            query,
            case=False,
            na=False,
        )
    ].copy()

    if matches.empty:

        print(
            "\nNo matches found. "
            "Make sure to use full name."
        )

        return

    matches = matches.reset_index(
        drop=True
    )

    display_cols = [
        "profile_id",
        "player_name",
        "competition_name",
        "season",
        "role",
        "minutes_played",
    ]

    print()
    print(
        matches[display_cols]
        .to_string(index=True)
    )

    try:

        row = int(
            input(
                "\nSelect player row: "
            )
        )

    except ValueError:

        print(
            "\nInvalid selection."
        )

        return

    if row not in matches.index:

        print(
            "\nInvalid selection."
        )

        return

    selected_profile = (
        matches.iloc[row]
    )

    role = (
        selected_profile["role"]
    )

    population = (
        build_filtered_population(
            profiles,
            role,
        )
    )

    if population.empty:
        return

    profile_id = (
        selected_profile["profile_id"]
    )

    if profile_id not in set(
        population["profile_id"]
    ):

        print(
            "\nSelected player is not "
            "part of the chosen "
            "comparison population."
        )

        return

    generate_radars(
        profile_ids=[profile_id],
        population=population,
    )

def radar_prompt(population):

    answer = input(
        "\nGenerate radar(s)? [y/n]: "
    ).lower()

    if answer != "y":
        return

    rows = input(
        "\nEnter row numbers "
        "(example: 0,1): "
    ).strip()

    try:

        row_ids = [
            int(x.strip())
            for x in rows.split(",")
        ]

    except Exception:

        print(
            "\nInvalid selection."
        )

        return

    if len(row_ids) > 2:

        print(
            "\nComparison radar "
            "supports a maximum "
            "of two players."
        )

        return

    selected_profiles = (
        population.iloc[row_ids]
        ["profile_id"]
        .tolist()
    )

    generate_radars(
        profile_ids=selected_profiles,
        population=population,
    )

def main():

    profiles = load_profiles()

    while True:

        print_header(
            "PLAYER RECRUITMENT EXPLORER"
        )

        print("1. Explore Rankings")
        print("2. Search Player")
        print("3. Exit")

        choice = input(
            "\nSelect option: "
        ).strip()

        if choice == "1":

            ranking_flow(
                profiles
            )

        elif choice == "2":

            search_flow(
                profiles
            )

        elif choice == "3":

            print(
                "\nSee you in your next exploration."
            )
            break

        else:

            print(
                "\nInvalid selection."
            )


if __name__ == "__main__":
    main()