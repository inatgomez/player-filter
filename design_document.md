# Player Recruitment Filter - Position Design Document

## Problem

The goal of this project is to identify player-seasons in StatsBomb open data that match the requirements of a team built around an attacking and possession-oriented style of play.

The project is not intended to produce a universal player rating or determine who the "best" player is in a given position. Instead, it aims to create role-specific comparison populations and rank player-seasons according to metrics that capture responsibilities associated with those roles.

The central question is:

_Which player-seasons show the strongest statistical profile for a specific tactical role within an attacking, positional style of football?_

If event data can identify player profiles associated with possession-oriented football using only a complete 2015/16 season, then the same methodology should remain applicable to richer and more recent datasets.

## Dataset and Scope

The analysis uses StatsBomb open data from the complete La Liga 2015/16 season.

The decision to focus on a single season is driven by data completeness rather than historical preference. While StatsBomb open data includes matches from multiple seasons and competitions, coverage is not uniform across all available datasets. La Liga 2015/16 is the only league season within the open data repository that provides complete coverage of all 380 league matches.

Complete coverage is particularly important for a recruitment project because player comparisons depend on observing players under similar conditions. Partial season coverage introduces differences in data availability that are unrelated to player performance. A player may appear to have limited minutes or incomplete statistics simply because a portion of their matches is unavailable in the public dataset.

By restricting the analysis to a fully observed season, the project ensures that player-season comparisons reflect football performance rather than dataset artifacts.

Although the implementation uses La Liga 2015/16, the methodology and code are designed to be competition-agnostic. The pipeline can be applied to other competitions, seasons, or licensed datasets where sufficient coverage is available.

## Position Assignment Philosophy

One of the main challenges in recruitment analysis is defining who belongs to a comparison population.

StatsBomb event data can associate players with multiple position labels throughout a season. These labels reflect the tactical role assigned to the player at different moments and allow the dataset to capture role changes across formations and match situations.

The objective of this project is not to determine a player's "true" position. Instead, position labels are used as a practical mechanism for constructing comparison populations.

The methodology separates population construction from performance evaluation.

Population construction determines whether a player-season belongs to a specific role population. Performance evaluation then uses all events recorded for that player-season, regardless of position label.

Modern football roles frequently involve movement across multiple areas of the pitch. A full back may spend significant periods operating in midfield. A creative midfielder may alternate between central and attacking zones. Excluding events that occur outside a player's primary label would remove information about how that player actually performs the role.

For this reason, position labels determine eligibility, while all events contribute to the player's statistical profile.

Position-share thresholds will be determined through exploratory analysis of the dataset. The objective is to identify players who predominantly occupy a role while reducing the influence of highly ambiguous or hybrid profiles. Thresholds are therefore treated as data-informed design decisions rather than arbitrary fixed values.

## Role Populations

### Full Back

Modern full backs contribute to both defensive and attacking phases of play. Beyond defending wide areas, they are expected to participate in build-up, provide width, support progression into advanced areas, and contribute to chance creation.

In teams built around positional play, full backs frequently act as connectors between defensive and attacking units. Their value comes from their ability to advance possession while maintaining defensive responsibility during transitions.

The full back population consists of player-seasons whose primary position falls within the following labels:

- Left Back
- Right Back
- Left Wing Back
- Right Wing Back

The metrics selected for this role focus on three dimensions of performance: progression, chance creation, and defensive contribution. Particular emphasis is placed on a player's ability to advance possession, create attacking value from wide areas, recover possession, and maintain defensive effectiveness when isolated in duels.

The role is evaluated using:

- Deep Progressions
- Open Play xG Assisted
- Turnovers
- Aerial Win Percentage
- Possession Adjusted Tackles and Interceptions
- Possession Adjusted Pressures
- Fouls
- Tackle / Dribbled Past Percentage

### Defensive Midfielder

The defensive midfielder acts as the connection between defensive stability and attacking progression.

In possession, the role is responsible for circulating the ball, progressing attacks from deeper areas, and maintaining control of central spaces. Out of possession, the role is expected to disrupt opposition attacks, recover possession, and protect the defensive line.

The project focuses on defensive midfielders who combine defensive responsibility with involvement in possession rather than purely destructive midfield profiles.

The defensive midfielder population consists of player-seasons whose primary position falls within the following labels:

- Left Defensive Midfield
- Centre Defensive Midfield
- Right Defensive Midfield

The metrics selected for this role emphasize progression from deeper areas, defensive actions, ball recovery, and possession security.

The role is evaluated using:

- Deep Progressions
- Open Play xG Assisted
- Possession Adjusted Tackles and Interceptions
- Tackle / Dribbled Past Percentage
- Possession Adjusted Pressures
- Fouls
- Turnovers

### Creative Midfielder

The purpose of this role is to identify players responsible for progressing possession and creating attacking opportunities between midfield and the forward line.

The role is not limited to traditional attacking midfielders. Many elite creators operate from deeper midfield positions while performing similar responsibilities. The objective is therefore to capture players whose primary contribution comes through progression, chance creation, and attacking involvement rather than defensive coverage.

This population includes player-seasons whose primary position falls within the following labels:

- Centre Midfield
- Left Midfield
- Right Midfield
- Centre Attacking Midfield
- Left Attacking Midfield
- Right Attacking Midfield

The selected metrics focus on chance creation, attacking involvement, ball progression, and a player's ability to generate dangerous actions in advanced areas.

The role is evaluated using:

- Touches In Box
- Open Play xG Assisted
- Shots per 90
- Non-Penalty xG per 90
- Non-Penalty xG per Shot
- Possession Adjusted Pressures
- Fouls Won
- Turnovers

## Evaluation Methodology

After assigning player-seasons to a role population, a minimum minutes threshold is applied to remove observations that are unlikely to provide a reliable representation of player performance.

The minimum minutes threshold serves a methodological purpose rather than a user-interface purpose. Players with limited playing time can produce extreme metric values that are driven by small samples rather than repeatable performance. Applying a minimum threshold improves the reliability of percentile comparisons by ensuring that player-seasons represent meaningful periods of play.

Percentile ranks are calculated separately within each role population. A percentile therefore represents performance relative to players performing comparable responsibilities rather than relative to the entire dataset.

The project intentionally avoids creating a composite player rating.

The selected metrics capture different dimensions of performance, and combining them into a single score would require assumptions about the relative value of progression, chance creation, defensive actions, and ball retention. Such assumptions are outside the scope of this project and would introduce subjective weighting decisions.

Instead, users evaluate player-seasons through individual metrics and interpret performance within the context of the role being examined.

The user workflow is:

1. Select a role population.
2. Select a minimum minutes threshold.
3. Select a performance metric.
4. View ranked player-seasons and percentile rankings.
5. Generate radar charts for selected player-seasons.

## Limitations

Position assignment in football is inherently imperfect. Players may perform responsibilities associated with multiple roles despite being assigned to a single comparison population.

The project relies exclusively on event data. Off-ball movement, positioning, spatial occupation, and other behaviours that require tracking data are not captured.

The analysis is restricted to a single competition and season. While this improves internal consistency and eliminates issues caused by incomplete public data coverage, it also means the results reflect the tactical environment of La Liga 2015/16. Findings should not be generalized to other competitions, seasons, or football contexts without additional validation.

Finally, player performance is highly dependent on team context. The project evaluates what a player produced within a specific tactical environment rather than attempting to estimate how those performances would translate to a different team or league.

## References

[StatsBomb Open Data](https://github.com/statsbomb/open-data)

[Hudl StatsBomb Radar Methodology Article](https://www.hudl.com/blog/new-statsbomb-radars-2023-update?utm_source=chatgpt.com)

[Hudl Event Data Glossary](https://support.hudl.com/s/article/event-data-glossary-player-metrics?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary)

[Soccermatics Scouting and Recruitment Resources](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html)
