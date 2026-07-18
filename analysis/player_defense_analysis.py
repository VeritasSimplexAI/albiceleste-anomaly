"""The whistle study: fouls per tackle-won and cards per foul, player level,
WC 2018/2022/2026 + Copa América 2019/2021/2024.

Exposure = tackles_won (the only tackle stat published for all six tournaments).
Confound control = cross-organizer comparison of the SAME players/teams.
Outputs -> processed/{whistle_team,whistle_players,whistle_pairs}.csv
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import sys
import pandas as pd
import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
ROOT = rf"{_ROOT}"
P = rf"{ROOT}\data\processed"

pdd = pd.read_csv(rf"{ROOT}\data\player-defense\player_defense.csv", encoding="utf-8-sig")
pdd["comp"] = np.where(pdd.competition.str.contains("Copa"), "Copa", "WC")
pdd["cards"] = pdd.yellow_cards.fillna(0) + pdd.red_cards.fillna(0)

# ---------- 1) team level ----------
rows = []
for (comp, yr), g in pdd.groupby(["comp", "year"]):
    t = g.groupby("team").agg(tklw=("tackles_won", "sum"), fouls=("fouls_committed", "sum"),
                              cards=("cards", "sum")).reset_index()
    a = t[t.team == "Argentina"]
    f = t[t.team != "Argentina"]
    if a.empty: continue
    a = a.iloc[0]
    # fouls called per tackle-won: exact test conditioning on total fouls, exposure = tackles won
    p_fpt = stats.binomtest(int(a.fouls), int(a.fouls + f.fouls.sum()),
                            a.tklw / (a.tklw + f.tklw.sum())).pvalue
    p_cpf = stats.binomtest(int(a.cards), int(a.cards + f.cards.sum()),
                            a.fouls / (a.fouls + f.fouls.sum())).pvalue
    rows.append(dict(comp=comp, year=int(yr),
                     arg_fpt=round(a.fouls / a.tklw, 3), field_fpt=round(f.fouls.sum() / f.tklw.sum(), 3),
                     fpt_ratio=round((a.fouls / a.tklw) / (f.fouls.sum() / f.tklw.sum()), 2), p_fpt=round(p_fpt, 3),
                     arg_cpf=round(a.cards / a.fouls, 3), field_cpf=round(f.cards.sum() / f.fouls.sum(), 3),
                     cpf_ratio=round((a.cards / a.fouls) / (f.cards.sum() / f.fouls.sum()), 2), p_cpf=round(p_cpf, 3)))
team = pd.DataFrame(rows).sort_values(["year"])
team.to_csv(rf"{P}\whistle_team.csv", index=False)
print("=== Team level: fouls per tackle-won (fpt) and cards per foul (cpf), Argentina vs field ===")
print(team.to_string(index=False))

# ---------- 2) player level (min 180 minutes) ----------
pl = pdd[(pdd.minutes >= 180) & (pdd.tackles_won >= 3)].copy()
pl["fpt"] = (pl.fouls_committed / pl.tackles_won).round(2)
pl["cpf"] = np.where(pl.fouls_committed > 0, (pl.cards / pl.fouls_committed).round(2), np.nan)
pl["pos"] = pl.position.astype(str).str[:2].str.replace(",", "", regex=False)
keep = ["competition", "year", "player", "team", "pos", "minutes", "tackles_won",
        "fouls_committed", "fouls_drawn", "cards", "fpt", "cpf"]
pl[keep].to_csv(rf"{P}\whistle_players.csv", index=False)
print(f"\nplayers with >=180 min & >=3 tackles won: {len(pl)}")

# position medians (context for the site)
posmed = pl.groupby("pos")[["fpt", "cpf"]].median().round(2)
print("\nposition medians:"); print(posmed.to_string())

# ---------- 3) cross-organizer pairs: same player, WC vs Copa (post-2021 era) ----------
wc = pl[(pl.comp == "WC") & (pl.year >= 2022)].groupby(["player", "team"]).agg(
    wc_tklw=("tackles_won", "sum"), wc_fouls=("fouls_committed", "sum"), wc_cards=("cards", "sum"))
cp = pl[(pl.comp == "Copa") & (pl.year >= 2021)].groupby(["player", "team"]).agg(
    cp_tklw=("tackles_won", "sum"), cp_fouls=("fouls_committed", "sum"), cp_cards=("cards", "sum"))
both = wc.join(cp, how="inner").reset_index()
both["wc_fpt"] = (both.wc_fouls / both.wc_tklw).round(2)
both["cp_fpt"] = (both.cp_fouls / both.cp_tklw).round(2)
both["is_arg"] = both.team == "Argentina"
both.to_csv(rf"{P}\whistle_pairs.csv", index=False)
n_arg = int(both.is_arg.sum())
print(f"\ncross-org players (>=180min both, 2021+): {len(both)} ({n_arg} Argentina)")
for grp, g in both.groupby("is_arg"):
    lbl = "ARGENTINA" if grp else "other CONMEBOL/joint"
    print(f"{lbl}: WC fouls/TklW {g.wc_fouls.sum()/g.wc_tklw.sum():.3f} vs Copa {g.cp_fouls.sum()/g.cp_tklw.sum():.3f} "
          f"| WC cards/foul {g.wc_cards.sum()/g.wc_fouls.sum():.3f} vs Copa {g.cp_cards.sum()/g.cp_fouls.sum():.3f}")
arg_pairs = both[both.is_arg].sort_values("wc_tklw", ascending=False)
print("\nArgentina cross-org players:")
print(arg_pairs[["player", "wc_tklw", "wc_fpt", "cp_tklw", "cp_fpt", "wc_cards", "cp_cards"]].head(12).to_string(index=False))
