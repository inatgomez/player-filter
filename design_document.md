# Player Recruitment Filter - Position Design Document

## Problem

The goal of this project is to identify player-seasons in StatsBomb open data that match the requirements of a team built around an attacking and possession-oriented style of play.

The project is not intended to produce a universal player rating or determine who the "best" player is in a given position. Instead, it aims to create role-specific comparison populations and rank player-seasons according to metrics that capture responsibilities associated with those roles.

The central question is:

_Which player-seasons show the strongest statistical profile for a specific tactical role within an attacking, positional style of football?_

The output is a recruitment filter that allows users to explore player-seasons through individual performance metrics rather than a single overall score.

## Dataset and Scope

The analysis uses StatsBomb open data from La Liga between the 2017/18 and 2020/21 seasons.

The decision to focus on a single competition is intentional. Player performance is heavily influenced by league context, tactical trends, and overall competition strength. Combining multiple leagues would introduce additional variables and require assumptions about how performance translates between competitions. Restricting the dataset to La Liga creates a more consistent comparison environment and allows the project to focus on role identification rather than cross-league translation.

The unit of analysis is the player-season.

Each player-season is treated as an independent observation. A player's profile can change substantially across multiple years due to tactical role changes, aging, injuries, managerial changes, or team context. Aggregating multiple seasons into a single profile would create a representation that may never have existed in practice. By preserving season-level observations, the project evaluates players within the specific context in which their performances occurred.

As a result, rankings, percentile calculations, and radar charts are generated at the player-season level rather than the player level.

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

The dataset is restricted to La Liga between 2017/18 and 2020/21. Results should not be interpreted as representative of other competitions without additional validation.

Finally, player performance is highly dependent on team context. The project evaluates what a player produced within a specific tactical environment rather than attempting to estimate how those performances would translate to a different team or league.

## References

[StatsBomb Open Data](https://github.com/statsbomb/open-data)

[Hudl StatsBomb Radar Methodology Article](https://www.hudl.com/blog/new-statsbomb-radars-2023-update?utm_source=chatgpt.com)

[Hudl Event Data Glossary](https://support.hudl.com/s/article/event-data-glossary-player-metrics?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary)

[Soccermatics Scouting and Recruitment Resources](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html)
