# Contested Calls Index — Sourcing Notes

Compiled 2026-07-17. Covers contested/controversial officiating moments in Argentina
World Cup matches, 1930 through the 2026 semi-final (the 2026 final vs Spain had not
been played at compile time). 26 incidents total.

## Sourcing standards

- **Every incident has at least one press citation** (`press_url`) that was surfaced
  and verified via live web search at compile time. No incident is included on memory
  alone; details (dates, minutes, referee names, what was called) were cross-checked
  against at least one independent account before being written.
- **Video links point only to existing public uploads on official channels.**
  Every YouTube link was verified via YouTube's public oEmbed endpoint to confirm the
  uploader is the official **FIFA** channel (`author_name: "FIFA"`). FIFA.com / FIFA+
  and FOX Sports `/watch/` clip pages are the platforms' own official players.
  No pirated full-match uploads are linked — the two full-match links (1998 R16, 1998 QF)
  are FIFA's *own* official uploads/replays.
- **If no legitimate public clip was found, `video_url` is blank** and the press
  citation carries the incident (8 of 26 rows).
- **Direction** is from Argentina's perspective: `favored_argentina` (17),
  `against_argentina` (6), `disputed` (3, where the grievance cuts both ways or is
  about overall match control rather than a single call).
- Minutes are left blank where sources did not state one precisely (e.g. 1990 USSR
  handball, 2018 Rojo handball, 2026 Jordan penalty) rather than guessed.

### Source-quality tiers
Most rows cite tier-1 outlets (ESPN, Sky Sports, Al Jazeera, Sports Illustrated,
Sky/beIN/TNT Sports, UEFA.com, Goal, Yahoo Sports, HuffPost, Gulf News). Four rows rely
on second-tier but incident-dedicated sources and should be upgraded if better links
surface:
- 1930 v France (historycollection.com — dedicated long-read on the early whistle)
- 1990 v USSR (mws.com Shirt Stories — the incident is also confirmed by Maradona's
  own published admission and Erik Fredriksson's biography)
- 2014 final Neuer/Higuaín (Sportskeeda — also covered by Bleacher Report and the
  match's Wikipedia entry with citations)
- 2026 v Austria Messi goal (football360.com.au — carries the Schmeichel quotes)

## Coverage assessment by era

| Era | Incidents | Coverage grade | Notes |
|---|---|---|---|
| 1930–1962 | 1 | **C** (thin) | Argentina withdrew or sent weakened squads for much of 1934–1962; the 1930 France early-whistle is the one well-documented officiating storm. Press sourcing exists but is retrospective; **no legitimate public footage found** (newsreel archives like British Pathé hold 1930 material but no verifiable public clip of this incident). |
| 1966–1990 | 6 | **B+** | The famous ones (Rattín, Hand of God, Codesal) are exhaustively documented. Video: FIFA has official uploads for 1966 (full match) and 1986 (official clip page); **no official upload found for the 1990 final or the 1990 USSR handball** — plenty of clips exist on YouTube but only on unofficial channels, so they are not linked. |
| 1994–2014 | 6 | **B+** | 1994 and 2006 produced no major officiating controversies in Argentina matches (1994's story was Maradona's doping ban — not an officiating call, so excluded). 1998, 2002, 2010 all have official FIFA video. 2014 Neuer incident has no official clip. |
| 2018–2022 | 6 | **A** | VAR era: every incident has same-day tier-1 analysis (ESPN's VAR review series) and official FIFA or FOX video for 5 of 6. |
| 2026 | 7 | **A** (ongoing) | Compiled from live coverage; comprehensive through the semi-final. The final vs Spain (2026-07-19) should be reviewed and appended after it is played. |

## Copyright note

This index **links only to existing public uploads** on official channels (FIFA's
YouTube channel, FIFA.com/FIFA+, FOX Sports official clip pages). It does not rehost,
embed-copy, download, rip, or mirror any footage, and it deliberately excludes
unofficial re-uploads even where they are the only available clip — in those cases the
`video_url` field is left blank and the press citation documents the incident. If a
linked video is later taken down or made private, remove the link rather than
substituting an unofficial copy.

## Incidents where sources disagree

1. **2026 R16 v Egypt, 59' disallowed goal** — Sky Sports' match report called the goal
   "rightly disallowed"; Al Jazeera, FOX Sports and several pundits argued the
   intervention (a shirt-tug ~20 seconds earlier, ~100 yards from goal) was beyond
   VAR's remit. The Egyptian FA filed an official complaint. Both readings are noted
   in the row.
2. **1986 Hand of God — who was to blame** — referee Ali Bin Nasser has said he was
   waiting for a signal from linesman Bogdan Dochev; Dochev (before his death) blamed
   Bin Nasser. Accounts agree on the facts of the goal, not on the culprit.
3. **1990 final penalty** — sources split between "soft but defensible" and "scandalous";
   Codesal himself has always maintained it was a penalty. Separately, SI and Time
   report the (unproven) Argentine claims about how Codesal came to be appointed.
4. **2014 final Neuer/Higuaín minute** — reported variously as the 55th, 56th and 58th
   minute; the CSV uses 56 (the most commonly cited).
5. **1998 Beckham red** — sources give the incident as 47' or 48'; the CSV uses 48 per
   the retrospectives cited. All sources agree Simeone exaggerated (he admitted it).
6. **2022 v Saudi Arabia offsides** — ESPN's VAR review judged all three disallowed
   goals technically correct via SAOT; fan-facing outlets (SportBible et al.) reported
   credible claims that the wrong defender was used for the Lautaro Martínez call.
   Listed as against_argentina with the dispute described.
7. **2022 final encroachment** — French claims that Messi's 108' goal should have been
   disallowed for substitute encroachment vs. referee Marciniak's counter-evidence of
   French players on the pitch during an Mbappé goal; IFAB's position (interference
   required) settled it officially.
8. **2026 SF v England** — fan and social-media accusations of referee bias
   (Elfath's 5-0 Messi record) vs. post-match analyses finding no major errors and no
   VAR interventions. No specific wrong call was established; the row is `disputed`
   and describes the scrutiny rather than asserting an error.
9. **2026 Jordan match date** — ESPN dates the match 27 June 2026; some secondary
   coverage says 28 June (likely timezone/publish-date artifacts). The CSV uses
   2026-06-27 per ESPN's match page.

## Known gaps / future work

- 1930 final v Uruguay ("two balls" story) excluded: it was a pre-agreed compromise,
  not a contested officiating call.
- 1966 group v West Germany (Albrecht sending-off) and other minor pre-1986 flashpoints
  excluded for lack of strong dedicated sourcing; add if good citations surface.
- Append the 2026 final after 2026-07-19.
