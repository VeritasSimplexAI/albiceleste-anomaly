# Data sources, licenses, and attribution

This project stands on the shoulders of open data. Every compiled CSV carries per-row
`source_url` columns or a folder-level NOTES/SOURCES file; this document covers licensing
and required attribution.

## Upstream datasets

| Source | Used for | License / terms |
|---|---|---|
| [fjelstul/worldcup](https://github.com/jfjelstul/worldcup) | matches, goals, bookings, penalty kicks, referees, standings 1930–2022 | CC-BY-4.0 — © Joshua C. Fjelstul. One correction applied and documented (1958/1962 referee misattribution; see data/referee-teams/NOTES_1930_1986.md) |
| [martj42/international_results](https://github.com/martj42/international_results) | all international results 1872–2026 | CC0 |
| [StatsBomb Open Data](https://github.com/statsbomb/open-data) | foul-by-foul event data, World Cups 2018 & 2022 | StatsBomb non-commercial license; data © StatsBomb. **Attribution:** this project uses StatsBomb Open Data and gratefully credits StatsBomb. |
| [eloratings.net](https://www.eloratings.net) | pre-tournament Elo ratings 1930–2026 | World Football Elo Ratings, cited as source; ratings are published facts |
| [RSSSF](https://www.rsssf.org) | historical match detail, penalties, referees, linesmen | cited per RSSSF's citation policy; used as factual reference |
| FBref / Opta (via Wayback Machine snapshots) | squad & player discipline stats 2014–2026, Copa América | facts cited with per-row archived source URLs; Opta is the underlying provider |
| Wikipedia | match reports, officials lists, seedings, draw articles | CC-BY-SA; used for facts with per-row citations |
| ESPN / REFSIX / press trackers | VAR overturns and confirmed reviews 2018–2026 | cited per incident; journalistic compilations |
| Linguasport, planetworldcup, soccernostalgia, and others | cross-checks on historical penalties and crews | cited in folder NOTES where used |

## Compiled datasets authored here (CC-BY-4.0)

The per-incident penalty ledger 1930–2010, the full officiating-crew compilation 1930–2026,
the VAR overturn/confirmed-review ledgers, the 2026 tournament compilation, the contested-calls
index, and all files in `data/processed/` are original compilations by this project, released
under CC-BY-4.0. If you use them, credit "The Albiceleste Anomaly project" with a link to this
repository — and please carry forward the upstream attributions above.

## Video links

The contested-calls index links only to existing public uploads on official channels
(FIFA, broadcasters). No match footage is hosted or redistributed in this repository.
