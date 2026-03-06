# In analyse_f1_correlation.py ergänzen

import pandas as pd
import matplotlib.pyplot as plt

df_events = pd.read_csv("data/ticketmaster_events.csv")
df_final = pd.read_csv("data/final_dataset.csv")

# Listeners-Quartile zuweisen
df_final["quartile"] = pd.qcut(df_final["listeners"], q=4, labels=[
    "Q1 (niedrig)", "Q2", "Q3", "Q4 (hoch)"
])

# Events mit Quartil-Info joinen
df_events = df_events.merge(
    df_final[["artist_name", "quartile"]],
    on="artist_name", how="inner"
)

# Monat extrahieren
df_events["month"] = pd.to_datetime(df_events["event_date"]).dt.to_period("M")

# Events pro Monat pro Quartil
monthly = (
    df_events.groupby(["month", "quartile"])
    .size()
    .reset_index(name="event_count")
)
monthly["month"] = monthly["month"].dt.to_timestamp()

# ── Plot: Linien pro Quartil über Zeit ────────────────
fig, ax = plt.subplots(figsize=(14, 6))

colors = {
    "Q1 (niedrig)": "#d4e6f1",
    "Q2": "#7fb3d3",
    "Q3": "#2e86c1",
    "Q4 (hoch)": "#1a5276"
}

for quartile, group in monthly.groupby("quartile"):
    ax.plot(
        group["month"],
        group["event_count"],
        label=quartile,
        color=colors[quartile],
        linewidth=2,
        marker="o", markersize=4
    )

ax.set_xlabel("Monat", fontsize=11)
ax.set_ylabel("Anzahl Events", fontsize=11)
ax.set_title(
    "Tour-Aktivität über Zeit — aufgeteilt nach Listener-Quartil\n"
    "Q4 = Artists mit meisten Listeners, Q1 = wenigsten",
    fontsize=12
)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("data/plots/f1_timeline.png", dpi=150)
plt.show()
