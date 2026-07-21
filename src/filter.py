from pathlib import Path

import pandas as pd

from config.role_config import (
    ROLE_METRICS,
    DISPLAY_NAMES,
    LOWER_IS_BETTER,
)
from radar import generate_single_radar, generate_comparison_radar

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
        "player_name",
        "team_name",
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

def search_player_in_population(
    population: pd.DataFrame,
    label: str,
):

    print_header(label)

    query = input(
        "Player name: "
    ).strip()

    matches = population[
        population["player_name"]
        .str.contains(
            query,
            case=False,
            na=False,
        )
    ].copy()

    if matches.empty:

        print(
            "\nNo matches found."
        )

        return None

    matches = matches.reset_index(
        drop=True
    )

    display_cols = [
        "player_name",
        "team_name",
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
                "\nSelect row: "
            )
        )

    except ValueError:

        print(
            "\nInvalid selection."
        )

        return None

    if row not in matches.index:

        print(
            "\nInvalid selection."
        )

        return None

    return matches.iloc[row]

def choose_role_population(
    profiles: pd.DataFrame,
):

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

    population = (
        build_filtered_population(
            profiles,
            role,
        )
    )

    return role, population

def search_flow(profiles):

    print_header("Player Search")

    print("1. Comparison radar")
    print("2. Single radar(s)")

    mode = input(
        "\nSelect option: "
    ).strip()

    if mode == "1":

        role, population = (
            choose_role_population(
                profiles
            )
        )

        if population.empty:
            return

        player_1 = (
            search_player_in_population(
                population,
                "Player 1",
            )
        )

        if player_1 is None:
            return

        player_2 = (
            search_player_in_population(
                population,
                "Player 2",
            )
        )

        if player_2 is None:
            return
        
        if (
            player_1["profile_id"]
            == player_2["profile_id"]
        ):

            print(
                "\nPlease select two "
                "different players."
            )

            return

        generate_comparison_radar(
            profile_ids=[
                player_1["profile_id"],
                player_2["profile_id"],
            ],
            population=population,
        )

    elif mode == "2":

        role, population = (
            choose_role_population(
                profiles
            )
        )

        if population.empty:
            return

        player = (
            search_player_in_population(
                population,
                "Player",
            )
        )

        if player is None:
            return

        generate_single_radar(
            profile_id=player["profile_id"],
            population=population,
        )

    else:

        print(
            "\nInvalid selection."
        )

def radar_prompt(population):

    answer = input(
        "\nGenerate radar(s)? [y/n]: "
    ).lower()

    if answer != "y":
        return

    print_header("Radar Type")
    print("1. Single radar(s) — one or more players")
    print("2. Comparison radar — exactly two players")

    mode = input("\nSelect option: ").strip()

    if mode not in ("1", "2"):
        print("\nInvalid selection.")
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

    selected_profiles = (
        population.iloc[row_ids]
        ["profile_id"]
        .tolist()
    )

    if mode == "1":

        for profile_id in selected_profiles:

            generate_single_radar(
                profile_id=profile_id,
                population=population,
            )

    else:

        if len(selected_profiles) != 2:

            print(
                "\nComparison radar "
                "requires exactly "
                "two players."
            )

            return

        generate_comparison_radar(
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