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


def calculate_percentile(series, lower_is_better=False):

    return (
        series.rank(
            pct=True,
            ascending=lower_is_better,
        )
        * 100
    ).round(1)


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
        calculate_percentile(
            population[metric],
            lower_is_better,
        )
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
        .head(20)
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

        print("\nNo matches found.")
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

    print(
        "\nUse displayed row numbers "
        "for radar generation."
    )

    radar_prompt(matches)

def radar_prompt(population):

    answer = input(
        "\nGenerate radar(s)? [y/n]: "
    ).lower()

    if answer != "y":
        return

    rows = input(
        "\nEnter row numbers "
        "(example: 0,2,4): "
    ).strip()

    try:

        row_ids = [
            int(x.strip())
            for x in rows.split(",")
        ]

        selected_profiles = (
            population.iloc[row_ids]
            ["profile_id"]
            .tolist()
        )

    except Exception:

        print(
            "\nInvalid selection."
        )
        return

    print(
        "\nSelected profile IDs:"
    )

    for pid in selected_profiles:
        print(pid)

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
                "\nGoodbye."
            )
            break

        else:

            print(
                "\nInvalid selection."
            )


if __name__ == "__main__":
    main()