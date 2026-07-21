from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Radar

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

def build_metric_table_rows(
    profile: pd.Series,
    metrics: list[str],
) -> list[list[str]]:

    return [
        [
            DISPLAY_NAMES[m],
            f"{profile[m]:.2f}",
            f"{profile[f'{m}_pct']:.0f}",
        ]
        for m in metrics
    ]

def draw_metric_table(
    fig,
    rows: list[list[str]],
    bbox: list[float],
    col_labels: list[str] = None,
):

    ax = fig.add_axes(bbox)
    ax.axis("off")

    col_labels = col_labels or ["Metric", "Value", "Pct"]

    table = ax.table(
        cellText=rows,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colWidths=[0.55, 0.225, 0.225],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)

    header_color = "#1565c0"
    row_colors = ["#ffffff", "#eef3fa"]

    for (row, col), cell in table.get_celld().items():

        cell.set_edgecolor("#cccccc")
        cell.set_linewidth(0.6)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(weight="bold", color="white")
        else:
            pct = float(rows[row - 1][2])

            if col == 2:

                if pct >= 75:
                    cell.set_facecolor("#d8f3dc")

                elif pct <= 25:
                    cell.set_facecolor("#ffccd5")

    return table

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
        figsize=(14, 10),
    )

    ax.set_position([0.03, 0.08, 0.55, 0.82])

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
        f"{profile['team_name']}\n"
        f"{profile['competition_name']} | "
        f"{profile['season']}\n"
        f"{profile['role']}"
    ),
    pad=30,
    )

    filepath = single_radar_filename(
        profile
    )

    rows = build_metric_table_rows(profile, metrics)
    draw_metric_table(fig, rows, bbox=[0.62, 0.2, 0.34, 0.6])

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
        figsize=(16, 10),
    )

    ax.set_position([0.03, 0.1, 0.5, 0.8])

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
            profile[f"{metric}_pct"]
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

    y_positions = [0.50, 0.00]

    for idx, (_, profile) in enumerate(profiles.iterrows()):
        rows = build_metric_table_rows(profile, metrics)
        fig.text(
            0.58,
            y_positions[idx] + 0.42,
            (
                f"{profile['player_name']}\n"
                f"{profile['role']}\n"
                f"{profile['season']}\n"
                f"{profile['competition_name']}\n"
                f"{profile['team_name']}"
            ),
            fontsize=10,
            weight="bold",
            va="bottom",
        )
        draw_metric_table(
            fig,
            rows,
            bbox=[0.58, y_positions[idx], 0.38, 0.4],
            col_labels=["Metric", "Value", "Pct"],
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