# Pre-tournament Elo ratings — sources and verification notes

Companion notes for `elo_pre_tournament.csv`. All data fetched **2026-07-17**.

## What the CSV contains

One row per participating team per FIFA Men's World Cup, 1990-2026:

| Tournament | Teams | First match | rating_date used |
|---|---|---|---|
| 1990 | 24 | 1990-06-08 | 1990-06-07 |
| 1994 | 24 | 1994-06-17 | 1994-06-16 |
| 1998 | 32 | 1998-06-10 | 1998-06-09 |
| 2002 | 32 | 2002-05-31 | 2002-05-30 |
| 2006 | 32 | 2006-06-09 | 2006-06-08 |
| 2010 | 32 | 2010-06-11 | 2010-06-10 |
| 2014 | 32 | 2014-06-12 | 2014-06-11 |
| 2018 | 32 | 2018-06-14 | 2018-06-13 |
| 2022 | 32 | 2022-11-20 | 2022-11-19 |
| 2026 | 48 | 2026-06-11 | 2026-06-10 |

**Total: 320 rows.** Participant lists were derived from `data/worldcup-1930-2022/matches.csv`
(1990-2022) and `data/worldcup-2026/matches_2026.csv` (2026), and every eloratings.net team was
matched to those files' exact spellings. **No gaps** — a rating was found for all 320
team-tournament pairs.

## Primary source

**eloratings.net** (World Football Elo Ratings), via the tournament data files the site loads
under the hood:

```
https://www.eloratings.net/{YYYY}_World_Cup.tsv    (e.g. 1990_World_Cup.tsv)
```

Each row of those files gives a team's rating **at the end of the event** (column 4) and, in the
final two columns, the rank/rating **change during the event**. The pre-tournament ("start of
event") rating in the CSV is therefore:

```
pre_tournament_elo = end_of_event_rating - rating_change_during_event
```

This is the same "start of tournament" figure the eloratings.net tournament pages display; no
values were estimated or interpolated.

`rating_date` is the day before the tournament's opening match. Elo ratings only move when a team
plays, so each team's value on that date was actually set by its own final warm-up fixture
(e.g. Argentina's 2022 value of 2143 dates from their 2022-11-16 friendly vs UAE); the value in
force on `rating_date` is what the CSV records.

**2026 caveat:** the 2026 tournament was still in progress on the fetch date (final scheduled
2026-07-19), so `2026_World_Cup.tsv` reflects mid-event ratings — but the start-of-event value
(rating minus change-so-far) is unaffected by this, and it was independently verified (below).

## Team-name mapping

eloratings.net names matched the project's spellings exactly (including "West Germany",
"Soviet Union", "Czechoslovakia", "Yugoslavia", "Serbia and Montenegro", "Ivory Coast",
"South Korea", "United States", "Curaçao", "Turkey") except for two renames applied:

| eloratings.net | Project spelling |
|---|---|
| Ireland | Republic of Ireland (1990, 1994, 2002) |
| Czechia | Czech Republic (2006, 2026) |

Code-to-name mapping came from `https://www.eloratings.net/en.teams.tsv`.

## Verification

### 1. Second eloratings.net page type: per-team match histories (30/30 exact)

The site also serves per-team full match histories (`https://www.eloratings.net/Argentina.tsv`,
`.../Brazil.tsv`, `.../Germany.tsv`) listing every match with post-match ratings. For
**Argentina, Brazil and Germany in all 10 tournaments** (30 checks), the rating after the team's
last pre-tournament match was compared to the CSV value: **all 30 matched exactly**, confirming
the "end minus event change" arithmetic. Argentina examples: 1794 after 1990-05-22 friendly;
2143 after 2022-11-16 friendly; 2115 after 2026-06-09 friendly — all equal to the CSV rows.

### 2. Wayback Machine snapshot of eloratings.net, 2026-06-04 (7 days pre-tournament)

`https://web.archive.org/web/20260604022542/https://www.eloratings.net/World.tsv`
vs the CSV's 2026 values (as of 2026-06-10): 5 of 48 teams identical; the other 43 differ by
only ±1 to ±19 points, exactly the signature of the single send-off friendly nearly every squad
played in the June 4-10 window (e.g. Argentina 2113 → 2115; Spain 2165 → 2157; France 2081 → 2063).
No anomalies.

### 3. Contemporary archived snapshots (third source, three tournaments)

| Team | 2018: Wikipedia Elo table, archived 2018-06-08* | CSV (2018-06-13) |
|---|---|---|
| Brazil | 2136 | 2141 (won friendly 2018-06-10) |
| Germany | 2076 | 2076 |
| Argentina | 1986 | 1984 |
| France | 1995 | 1986 (drew friendly 2018-06-09) |
| Spain | 2042 | 2043 |

*`https://web.archive.org/web/20180608004955/https://en.wikipedia.org/wiki/World_Football_Elo_Ratings`
(Wikipedia mirrors eloratings.net). Agreement within 0-2 points once the two explained
post-snapshot friendlies are accounted for.

| Team | 2010: eloratings world.html "as of June 11 2010"** | CSV | 2014: world.html "as of June 2 2014"*** | CSV |
|---|---|---|---|---|
| Brazil | 2087 | 2109 | 2113 | 2138 |
| Argentina | 1899 | 1921 | 1989 | 2018 |
| Germany | 1929 | 1957 | 2046 | 2073 |
| Spain | 2085 | 2111 | 2086 | 2107 |

**`https://web.archive.org/web/20100611202750/http://www.eloratings.net/world.html`
***`https://web.archive.org/web/20140608092556/http://www.eloratings.net/world.html`

### Known discrepancy: retroactive revisions by eloratings.net

The 2010/2014 contemporary snapshots run systematically ~20-30 points **below** today's
eloratings.net figures for the same dates (part of the 2014 gap is also June 3-11 friendlies).
eloratings.net has since revised its historical match database/calculation, shifting past ratings;
the effect is large for 2010/2014, negligible (0-2 pts) by 2018, and zero for 2026. The CSV
deliberately uses the **current (revised) eloratings.net dataset for all ten tournaments**, so
values are internally consistent and comparable across eras. If you instead need the numbers *as
published at the time*, use the archived snapshots above (only available for some tournaments).

## Gaps

None. All 320 participating teams have a rating. (1991/1995/etc. rows in `matches.csv` are
Women's World Cups and are out of scope.)

---

# 1930-1986 extension (`elo_pre_tournament_1930_1986.csv`)

Backward extension covering the 13 tournaments 1930-1986, built **2026-07-17** with the **same
method** as the 1990-2026 file: fetch `https://www.eloratings.net/{YYYY}_World_Cup.tsv`, take each
team's end-of-event rating (column 4) and rating change during the event (final column), and
compute `pre_tournament_elo = end_of_event_rating - rating_change`. No values were estimated,
interpolated, or taken from any other source. (The site's numbers use the Unicode minus U+2212;
these were normalized before parsing.)

## Coverage and rating dates

`rating_date` is again the day before the tournament's opening match (opening dates from
`data/worldcup-1930-2022/matches.csv`):

| Tournament | Teams | First match | rating_date used |
|---|---|---|---|
| 1930 | 13 | 1930-07-13 | 1930-07-12 |
| 1934 | 16 | 1934-05-27 | 1934-05-26 |
| 1938 | 15 | 1938-06-04 | 1938-06-03 |
| 1950 | 13 | 1950-06-24 | 1950-06-23 |
| 1954 | 16 | 1954-06-16 | 1954-06-15 |
| 1958 | 16 | 1958-06-08 | 1958-06-07 |
| 1962 | 16 | 1962-05-30 | 1962-05-29 |
| 1966 | 16 | 1966-07-11 | 1966-07-10 |
| 1970 | 16 | 1970-05-31 | 1970-05-30 |
| 1974 | 16 | 1974-06-13 | 1974-06-12 |
| 1978 | 16 | 1978-06-01 | 1978-05-31 |
| 1982 | 24 | 1982-06-13 | 1982-06-12 |
| 1986 | 24 | 1986-05-31 | 1986-05-30 |

**Total: 217 rows.** Participant lists were derived from `matches.csv` (men's tournaments only)
and the join was validated programmatically: for every tournament, the set of eloratings.net
teams equals the set of `matches.csv` participants **exactly — 217/217 matched, no gaps and no
extras**. Every participating team is on eloratings.net; nothing had to be left out.

## Team-name mapping

Code-to-name mapping again came from `https://www.eloratings.net/en.teams.tsv`. Unlike 1990-2026
(which needed two renames), **zero renames were needed**: every eloratings.net primary name
already matches the fjelstul spelling, including the historical entities
"Dutch East Indies" (code DI, 1938), "Germany" (DE, 1934/1938), "West Germany" (WG, 1954-1986),
"East Germany" (DD, 1974), "Soviet Union" (SU), "Czechoslovakia" (CS), "Yugoslavia" (YU),
"Zaire" (ZR, 1974), "Northern Ireland" (EI), "Cuba" (CU, 1938), "Wales" (WA, 1958).

## Verification: per-team match histories (52/52 exact)

Same second-source check as before: the per-team full-history files
(`https://www.eloratings.net/Argentina.tsv`, `Brazil.tsv`, `Germany.tsv`, `Uruguay.tsv`,
`Italy.tsv`) list every match with post-match ratings. For each reference team and tournament,
the post-match rating of the team's **last match before the tournament opening** was compared to
the CSV value:

- Argentina — 9 editions entered (1930, 1934, 1958-1966, 1974-1986): **9/9 exact**
- Brazil — all 13 editions: **13/13 exact** (covers every tournament, incl. 1930 and 1950 where
  Germany was absent)
- Germany / West Germany — 11 editions (1934, 1938, 1954-1986; eloratings serves the pre-war DE
  and post-war WG eras on the single `Germany.tsv` page): **11/11 exact**
- Uruguay (host 1930) — 8 editions: **8/8 exact**
- Italy (host 1934) — 11 editions: **11/11 exact**

**52 checks, 52 exact matches, 0 discrepancies.** Every tournament is covered by at least two
independent per-team checks.

## Caveats specific to the early era

- **Stale ratings.** Elo ratings only move when a team plays, and pre-war sides sometimes went
  years between internationals. E.g. Brazil's 1930 value (1923) was set by their last match on
  **1925-12-25**, four and a half years before the tournament. The value is still the rating in
  force on `rating_date`; it is just based on old information.
- **Retroactive revisions.** As documented above for 1990-2026, these figures come from the
  *current* (revised) eloratings.net dataset, so they are internally consistent with the
  1990-2026 file but may differ from numbers eloratings.net published decades ago.
- **Withdrawn teams** (e.g. Austria 1938, India/Scotland/Turkey 1950) never played a match, are
  not in `matches.csv`, and are deliberately excluded.

## Gaps (1930-1986)

None. All 217 participating teams have a rating.
