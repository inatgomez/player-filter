# Player Recruitment Filter

A football recruitment pipeline built on StatsBomb open data.

The project transforms StatsBomb Open Data into role-specific player profiles that can be filtered, compared, and visualized through radar charts. Users can build custom datasets by selecting competition-season combinations from the available StatsBomb Open Data catalog before generating player profiles.

This project is the third project in an applied sports analytics curriculum focused on moving from descriptive analysis to decision-support tools.

## Dataset

**Source:** StatsBomb Open Data

**Competition:** La Liga

**Season:** 2015/16

La Liga 2015/16 was selected because it is the only league season in the public StatsBomb dataset with complete coverage of all 380 matches.

## Repository Structure

```text
player-filter/
│
├── src/
│   ├── build_dataset.py      # Runs the full data pipeline
│   ├── ingest.py             # Downloads StatsBomb open data
│   ├── build_minutes.py      # Calculates player minutes played
│   ├── build_populations.py  # Assigns players to role populations
│   ├── build_profiles.py     # Creates player-season profiles
│   ├── filter.py             # Interactive player exploration tool
│   ├── radar.py              # Generates radar visualizations
│   ├── metrics.py            # Metric calculations and aggregations
│   └── config/
│       └── role_config.py    # Role definitions and metric mappings
│
├── data/
│   ├── raw/                  # Raw StatsBomb datasets
│   └── processed/            # Generated player datasets
│
├── notebooks/
│   ├── position_threshold_exploration.ipynb
│   └── total_minutes_played_exploration.ipynb
│
├── outputs/
│   └── radars/               # Generated radar charts
│
├── design_document.md        # Methodology and role definitions
├── requirements.txt
└── README.md
```

## Setup

Clone the repository and create a virtual environment.

```bash
git clone <repo-url>
cd player-filter

python -m venv .venv
source .venv/bin/activate

# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

Build a dataset:

```bash
python src/build_dataset.py
```

The application will:

1. Display the available StatsBomb Open Data competitions and seasons.
2. Prompt you to select one or more competition-season combinations.
3. Download the required match, lineup, and event data.
4. Calculate player minutes played.
5. Construct role populations.
6. Generate player-season profiles.

The resulting datasets are written to:

```text
data/raw/
data/processed/
```

Once the dataset has been built, launch the exploration tool:

```bash
python src/filter.py
```

The application then guides the user through the analysis workflow:

1. Select a role population.
2. Choose a minimum minutes threshold.
3. Select a ranking metric.
4. View ranked player profiles.
5. Generate radar chart visualizations.

Generated radar charts are saved to:

```text
outputs/radars/
```

## Supported Roles

- Full Back
- Defensive Midfielder
- Creative Midfielder

Detailed role definitions, population construction rules, metric selection rationale, and methodological decisions are documented in `design_document.md` and `notebooks/position_threshold_exploration.ipynb`.

## Outputs

The pipeline generates:

- Player role populations
- Player-season profiles
- Ranked player shortlists
- Radar chart visualizations

Generated radar charts are saved to:

```text
outputs/radars/
```

## Limitations

The project relies exclusively on event data. Off-ball movement, positioning, and other tracking-data-derived behaviours are not captured.

Results reflect the tactical environment of La Liga 2015/16 and should not be interpreted as league-independent player ratings.

The project is intended as a player profiling and comparison tool rather than a predictive recruitment model.

## Credits

Data provided by [StatsBomb Open Data](https://github.com/statsbomb/open-data).

Metric definitions and radar design reference: [Hudl StatsBomb event data glossary — player metrics](https://support.hudl.com/s/article/event-data-glossary-player-metrics?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary).

See `design_document.md` for detailed methodology and references.

If you'd like to discuss the project, sports analytics, or product development, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/nat-gomez-162144331/).
