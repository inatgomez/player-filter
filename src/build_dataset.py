from pathlib import Path

import pandas as pd
from statsbombpy import sb

from ingest import build_raw_dataset
from build_minutes import build_minutes
from build_populations import build_populations
from build_profiles import build_profiles


RAW_FILES = [
    "data/raw/events.parquet",
    "data/raw/lineups.parquet",
    "data/raw/matches.parquet",
]

PROCESSED_FILES = [
    "data/processed/player_minutes_summary.parquet",
    "data/processed/player_populations.parquet",
    "data/processed/player_profiles.parquet",
]


def check_existing_files() -> None:
    """
    Warn user before overwriting datasets.
    """

    existing = [
        path
        for path in RAW_FILES + PROCESSED_FILES
        if Path(path).exists()
    ]

    if not existing:
        return

    print("\nWARNING: Existing datasets detected.\n")

    for file in existing:
        print(file)

    print("\nThese files will be overwritten.\n")

    response = input(
        "Continue? (y/n): "
    ).strip().lower()

    if response != "y":
        raise SystemExit(
            "\nDataset build cancelled."
        )


def load_competitions() -> pd.DataFrame:
    """
    Load StatsBomb open-data competitions.
    """

    competitions = sb.competitions()

    competitions = competitions[
        [
            "competition_id",
            "competition_name",
            "season_id",
            "season_name",
        ]
    ].copy()

    return competitions.sort_values(
        [
            "competition_name",
            "season_name",
        ]
    ).reset_index(drop=True)


def build_competition_menu(
    competitions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add match coverage counts.
    """

    rows = []

    print(
        "\nLoading competition coverage...\n"
    )

    for idx, row in competitions.iterrows():

        try:

            matches = sb.matches(
                competition_id=row["competition_id"],
                season_id=row["season_id"],
            )

            match_count = len(matches)

        except Exception:

            match_count = "?"

        rows.append(
            {
                "menu_id": idx + 1,
                "competition_id": row[
                    "competition_id"
                ],
                "season_id": row[
                    "season_id"
                ],
                "competition_name": row[
                    "competition_name"
                ],
                "season_name": row[
                    "season_name"
                ],
                "match_count": match_count,
            }
        )

    return pd.DataFrame(rows)


def display_menu(
    menu_df: pd.DataFrame,
) -> None:

    print(
        "\nAvailable competitions:\n"
    )

    for _, row in menu_df.iterrows():

        print(
            f"[{row['menu_id']}] "
            f"{row['competition_name']} | "
            f"{row['season_name']} | "
            f"{row['match_count']} matches"
        )


def get_user_selection(
    menu_df: pd.DataFrame,
) -> list[tuple[int, int]]:

    selection = input(
        "\nSelect competitions/seasons "
        "(comma separated): "
    )

    try:

        menu_ids = [
            int(x.strip())
            for x in selection.split(",")
        ]

    except ValueError:

        raise ValueError(
            "Invalid selection."
        )

    selected_rows = menu_df[
        menu_df["menu_id"].isin(menu_ids)
    ]

    if selected_rows.empty:

        raise ValueError(
            "No valid selections made."
        )

    print("\nSelected:\n")

    for _, row in selected_rows.iterrows():

        print(
            f"✓ {row['competition_name']} | "
            f"{row['season_name']} | "
            f"{row['match_count']} matches"
        )

    return list(
        zip(
            selected_rows["competition_id"],
            selected_rows["season_id"],
        )
    )


def print_ingestion_summary() -> None:

    matches = pd.read_parquet(
        "data/raw/matches.parquet"
    )

    events = pd.read_parquet(
        "data/raw/events.parquet"
    )

    lineups = pd.read_parquet(
        "data/raw/lineups.parquet"
    )

    print("\nIngestion complete.\n")

    print(
        f"Matches: {len(matches):,}"
    )

    print(
        f"Events: {len(events):,}"
    )

    print(
        f"Lineups: {len(lineups):,}"
    )


def main():

    check_existing_files()

    print(
        "\nLoading StatsBomb competitions..."
    )

    competitions = (
        load_competitions()
    )

    menu_df = (
        build_competition_menu(
            competitions
        )
    )

    display_menu(menu_df)

    selections = (
        get_user_selection(menu_df)
    )

    print(
        "\n[1/4] Ingesting data..."
    )

    build_raw_dataset(
        selections
    )

    print_ingestion_summary()

    print(
        "\n[2/4] Building minutes..."
    )

    build_minutes()

    print(
        "\n[3/4] Building populations..."
    )

    build_populations()

    print(
        "\n[4/4] Building profiles..."
    )

    build_profiles()

    print(
        "\nDataset build complete.\n"
    )

    print(
        "Profiles saved to:\n"
    )

    print(
        "data/processed/player_profiles.parquet\n"
    )

    print(
        "Run:\n"
    )

    print(
        "python src/filter.py\n"
    )

    print(
        "to start your player exploration."
    )


if __name__ == "__main__":
    main()