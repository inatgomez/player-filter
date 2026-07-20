from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config.role_config import (
    RADAR_METRICS,
    DISPLAY_NAMES,
)

PROFILES_PATH = Path(
    "data/processed/player_profiles.parquet"
)

OUTPUT_DIR = Path(
    "outputs/radars"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

def load_profiles() -> pd.DataFrame:

    return pd.read_parquet(
        PROFILES_PATH
    )

def calculate_percentiles(
    population: pd.DataFrame,
    metrics: list[str],
    lower_is_better: set[str],
) -> pd.DataFrame:

    population = population.copy()

    for metric in metrics:

        ascending = (
            metric in lower_is_better
        )

        population[f"{metric}_pct"] = (
            population[metric]
            .rank(
                pct=True,
                ascending=ascending,
            )
            * 100
        )

    return population

def get_profile(
    profiles: pd.DataFrame,
    profile_id: str,
) -> pd.Series:

    match = profiles.loc[
        profiles["profile_id"] == profile_id
    ]

    if match.empty:

        raise ValueError(
            f"Profile not found: {profile_id}"
        )

    return match.iloc[0]

def build_radar_values(
    profile: pd.Series,
    metrics: list[str],
):

    labels = [
        DISPLAY_NAMES[m]
        for m in metrics
    ]

    values = [
        profile[f"{m}_pct"]
        for m in metrics
    ]

    values.append(values[0])

    return labels, values


def slugify(text: str) -> str:

    return (
        text.lower()
        .replace(" ", "_")
        .replace("/", "_")
    )


def single_radar_filename(
    profile: pd.Series,
) -> Path:

    player = slugify(
        profile["player_name"]
    )

    competition = slugify(
        profile["competition_name"]
    )

    season = slugify(
        profile["season"]
    )

    role = slugify(
        profile["role"]
    )

    return (
        OUTPUT_DIR
        / f"{player}_{competition}_{season}_{role}.png"
    )

def generate_single_radar(
    profile_id: str,
    population: pd.DataFrame,
):

    profile = get_profile(
        population,
        profile_id,
    )

    role = profile["role"]

    metrics = RADAR_METRICS[role]

    labels, values = build_radar_values(
        profile,
        metrics,
    )

    num_vars = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        num_vars,
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw=dict(
            polar=True
        ),
    )

    ax.plot(
        angles,
        values,
        linewidth=2,
    )

    ax.fill(
        angles,
        values,
        alpha=0.25,
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_title(
        (
            f"{profile['player_name']}\n"
            f"{profile['competition_name']} | "
            f"{profile['season']}\n"
            f"{profile['role']}"
        ),
        pad=30,
    )

    filepath = single_radar_filename(
        profile
    )

    plt.tight_layout()
    plt.savefig(
        filepath,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(
        f"Saved radar: {filepath}"
    )

def generate_comparison_radar(
    profile_ids: list[str],
    population: pd.DataFrame,
):

    if len(profile_ids) < 2:

        raise ValueError(
            "Comparison radar requires "
            "at least two profiles."
        )

    profiles = population[
        population["profile_id"]
        .isin(profile_ids)
    ].copy()

    roles = (
        profiles["role"]
        .unique()
        .tolist()
    )

    if len(roles) != 1:

        raise ValueError(
            "All comparison profiles "
            "must share the same role."
        )

    role = roles[0]

    metrics = RADAR_METRICS[role]

    labels = [
        DISPLAY_NAMES[m]
        for m in metrics
    ]

    num_vars = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        num_vars,
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw=dict(
            polar=True
        ),
    )

    for _, profile in profiles.iterrows():

        values = [
            profile[f"{m}_pct"]
            for m in metrics
        ]

        values.append(
            values[0]
        )

        label = (
            f"{profile['player_name']} | "
            f"{profile['competition_name']} | "
            f"{profile['season']}"
        )

        ax.plot(
            angles,
            values,
            linewidth=2,
            label=label,
        )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.3, 1.1),
    )

    ax.set_title(
        f"{role} Comparison",
        pad=30,
    )

    players = "_vs_".join(
        slugify(x)
        for x in profiles[
            "player_name"
        ].tolist()
    )

    filepath = (
        OUTPUT_DIR
        / f"{players}_{slugify(role)}.png"
    )

    plt.tight_layout()

    plt.savefig(
        filepath,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved comparison radar: "
        f"{filepath}"
    )

def generate_radars(
    profile_ids: list[str],
    population: pd.DataFrame,
):

    if len(profile_ids) == 1:

        generate_single_radar(
            profile_ids[0],
            population,
        )

    else:

        generate_comparison_radar(
            profile_ids,
            population,
        )