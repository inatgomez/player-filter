from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Radar

from config.role_config import (
    RADAR_METRICS,
    DISPLAY_NAMES,
    LOWER_IS_BETTER,
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

def radar_value(
    metric: str,
    percentile: float,
) -> float:

    if metric in LOWER_IS_BETTER:
        return 100 - percentile

    return percentile

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

    plot_values = [
        radar_value(
            m,
            profile[f"{m}_pct"],
        )
        for m in metrics
    ]

    percentiles = [
        profile[f"{m}_pct"]
        for m in metrics
    ]

    return (
        labels,
        plot_values,
        percentiles,
    )


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

    (
        labels,
        values,
    ) = build_radar_values(
        profile,
        metrics,
    )

    radar = Radar(
        params=labels,
        min_range=[0] * len(labels),
        max_range=[100] * len(labels),
    )

    fig, ax = radar.setup_axis(
        figsize=(10, 10),
    )

    radar.draw_circles(
        ax=ax,
        facecolor="#f7f7f7",
        edgecolor="#dddddd",
        linewidth=0.8,
    )

    radar.draw_radar(
        values,
        ax=ax,
        kwargs_radar={
            "linewidth": 3,
            "color": "#1565c0",
            "alpha": 0.3,
        },
        kwargs_rings={
            "facecolor": "#1565c0",
            "alpha": 0.2,
        },
    )

    radar.draw_range_labels(
        ax=ax,
        fontsize=10,
    )

    radar.draw_param_labels(
        ax=ax,
        fontsize=11,
    )

    ax.add_artist(
        plt.Circle(
            (0, 0),
            50,
            fill=False,
            linestyle="--",
            linewidth=1.2,
            color="#888888",
        )
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

    if len(profile_ids) != 2:

        raise ValueError(
            "Comparison radar "
            "requires exactly "
            "two players."
        )

    profiles = population[
        population["profile_id"]
        .isin(profile_ids)
    ].copy()

    role = (
        profiles["role"]
        .iloc[0]
    )

    metrics = RADAR_METRICS[role]

    labels = [
        DISPLAY_NAMES[m]
        for m in metrics
    ]

    radar = Radar(
        params=labels,
        min_range=[0] * len(labels),
        max_range=[100] * len(labels),
    )

    fig, ax = radar.setup_axis(
        figsize=(10, 10),
    )

    radar.draw_circles(
        ax=ax,
        facecolor="#f7f7f7",
        edgecolor="#dddddd",
        linewidth=0.8,
    )

    colors = [
        "#1565c0",
        "#d84315",
    ]

    linestyles = [
        "-",
        "--",
    ]

    for idx, (_, profile) in enumerate(
        profiles.iterrows()
    ):

        values = [
            radar_value(
                metric,
                profile[f"{metric}_pct"],
            )
            for metric in metrics
        ]

        radar.draw_radar(
            values,
            ax=ax,
            kwargs_radar={
                "linewidth": 3,
                "linestyle": linestyles[idx],
                "color": colors[idx],
                "alpha": 0.3,
                "label": profile[
                    "player_name"
                ],
            },
            kwargs_rings={
                "facecolor": colors[idx],
                "alpha": 0.15,
            },
        )

    radar.draw_range_labels(
        ax=ax,
        fontsize=10,
    )

    radar.draw_param_labels(
        ax=ax,
        fontsize=11,
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
        frameon=False,
    )

    players = "_vs_".join(
        slugify(x)
        for x in profiles[
            "player_name"
        ]
    )

    filepath = (
        OUTPUT_DIR
        / f"{players}_{slugify(role)}.png"
    )

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