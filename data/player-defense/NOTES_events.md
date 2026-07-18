# Fouls Before First Yellow — Event-Level Dataset (NOTES_events)

Built 2026-07-17 from StatsBomb Open Data (event-level). Files in this folder with the
`_events` suffix belong to this dataset; other files here are from separate work.

## Source

- StatsBomb Open Data, GitHub repo `statsbomb/open-data`, fetched via
  `raw.githubusercontent.com/statsbomb/open-data/master/data/...`
- Competition id 43 (FIFA World Cup), season id 3 (2018) and season id 106 (2022).
- Per match: the full events JSON (`data/events/<match_id>.json`) was downloaded and
  reduced to "Foul Committed" and "Bad Behaviour" events only.

## Method / definitions

- **Foul** = StatsBomb event type **"Foul Committed"** (an infringement penalised by the
  referee, attributed to the offending player). Offsides are a separate StatsBomb type and
  are NOT counted. "Foul Won" events are ignored (they are the other side of the same foul).
- **Yellow card** = a card of name "Yellow Card" **or** "Second Yellow" attached to either
  a "Foul Committed" event (`foul_committed.card`) or a "Bad Behaviour" event
  (`bad_behaviour.card`, e.g. dissent, time-wasting).
- **Ordering** uses the StatsBomb `index` field (sequential event order within the match,
  consistent with period + timestamp).
- **fouls_before_first_yellow** = number of the player's "Foul Committed" events with an
  index **strictly below** the index of his first yellow-type card event in that match.
  If the yellow was shown for the foul itself, that foul is not counted (it is not
  "before" the booking). If the first yellow came for bad behaviour, all fouls up to that
  moment count. Blank when the player was never booked in the match.
- **Row inclusion** (player file): every player-match with at least 1 foul committed or at
  least one card event. (In practice every included row has ≥1 foul or a yellow; no
  card-only-zero-foul rows occurred in these two tournaments.)
- Extra time is included. Penalty-shootout periods are also part of the event stream; a
  first yellow shown during a shootout (it happened once: Dumfries, NED–ARG 2022 QF)
  means all of that player's fouls in open play count as "before first yellow".

## Files

1. `fouls_before_yellow_events.csv` — 2,063 rows (one per qualifying player-match).
   Columns: `year,match_date,team,opponent,player,fouls_total,got_yellow,fouls_before_first_yellow`.
   `got_yellow` is yes/no; last column blank when no yellow. UTF-8 with BOM (Excel-safe).
2. `fouls_before_yellow_team.csv` — 64 rows (32 teams × 2 tournaments).
   Columns: `year,team,fouls_total,yellows_for_fouls,booked_player_matches,mean_fouls_before_first_yellow,fouls_per_booking`.
   - `yellows_for_fouls` = yellow-type cards shown **on foul events** (Yellow Card + Second Yellow).
   - `mean_fouls_before_first_yellow` = average of the player-file values over that team's
     booked player-matches (booking source can be foul or bad behaviour).
   - `fouls_per_booking` = `fouls_total / yellows_for_fouls`.

## Coverage check

- 2018: **64 of 64 matches** downloaded and parsed. 2022: **64 of 64 matches**. Exactly as expected.
- No foul/card events lacked player attribution (0 anomalies).
- Totals extracted: 2018 — 1,876 fouls, 207 player yellow-type cards (167 on fouls, 40 bad
  behaviour). 2022 — 1,775 fouls, 227 player yellow-type cards (183 on fouls, 44 bad behaviour).
- Caveat: StatsBomb events cover **on-pitch players only**; cards shown to bench/staff
  (e.g. some of the extra bookings in the record-setting NED–ARG 2022 QF) are absent, so
  card totals can sit slightly below official FIFA tallies.

## Argentina vs the field

Mean fouls-before-first-yellow across booked player-matches:

| Tournament | Argentina | Field (all other teams) | Difference |
|---|---|---|---|
| 2018 | 0.909 (n=11) | 1.057 (n=194) | −0.148 |
| 2022 | 0.882 (n=17) | 0.754 (n=207) | +0.129 |

**Question asked: did Argentina's players get MORE rope before a booking in 2022?**
Directionally yes (0.88 vs 0.75 fouls before the first yellow), but the difference is
**not statistically significant**. Monte Carlo permutation test on the difference of means
(200,000 resamples, seed 20260717): one-sided p = 0.340 (two-sided p = 0.678).
Mann-Whitney U: one-sided p = 0.151. With n=17 booked Argentina player-matches and small
integer values (0–3), there is no evidence of preferential treatment either way.
Team-level, Argentina ranks 9th of 32 in 2022 by mean rope (Netherlands 1st at 1.64).
In 2018 Argentina was slightly *below* the field (0.91 vs 1.06) — the pattern flips
between tournaments, which is what noise looks like.

Fouls per booking (team file): Argentina 2022 = 10.36 fouls per yellow-on-foul vs a
tournament-wide 9.70 (1775/183) — marginally above average. 2018: Argentina 8.86 vs
tournament-wide 11.23 — below average.

## 2026 availability (checked 2026-07-17)

- **StatsBomb Open Data does NOT include the 2026 World Cup.** Verified directly against
  `competitions.json` in the repo on 2026-07-17: competition 43 (FIFA World Cup) lists
  seasons 1958, 1962, 1970, 1974, 1986, 1990, 2018 and 2022 only — no 2026 season.
- A web search found no announcement of a 2026 open-data release. The 2026 tournament is
  still concluding at the time of writing; StatsBomb has historically pushed free World
  Cup event data to this repo during/after tournaments, so a later release is plausible
  but **not confirmed** — re-check `competitions.json` for a 2026 season under
  competition 43.
- No other legitimate **free event-level** source for 2026 was found. Free sites
  (FBref, Wikipedia, fixture APIs) publish card minutes and per-match foul *counts*, but
  not the foul-by-foul event stream needed to compute fouls-before-first-yellow.
  Commercial providers (Opta/Stats Perform, StatsBomb paid) hold such feeds but are not free.
- Nothing in this dataset is extrapolated to 2026; the two CSVs contain 2018 and 2022 only.

## Reproduction

Scripts (session scratchpad, not committed): `extract_events.py` (download + reduce
events) and `build_dataset.py` (aggregate to the two CSVs). Both are deterministic given
the source data; the permutation test seed is 20260717.
