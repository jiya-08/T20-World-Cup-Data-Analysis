"""
visualization.py
----------------
Generates professional, publication-quality visualizations for the
T20 World Cup Data Analysis portfolio project.
"""

import os
import sys
import logging
from typing import Dict, Any
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch, Rectangle
import seaborn as sns
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.analysis import load_processed_data, run_full_analysis, get_team_innings_totals

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Set standard design theme
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "grid.color": "#E5E5E5",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.titlesize": 16,
    "figure.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10
})

CHARTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)


def plot_tournament_kpis(kpis: Dict[str, Any], save_path: str = None):
    """Creates a KPI summary card graphic."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "01_tournament_overview_kpis.png")

    fig, ax = plt.subplots(figsize=(12, 6), facecolor="#F8FAFC")
    ax.axis("off")

    cards = [
        {"title": "Total Matches", "value": f"{kpis['total_matches_scheduled']}", "sub": "41 Completed | 4 Abandoned", "color": "#1E3A8A"},
        {"title": "Participating Teams", "value": f"{kpis['total_participating_teams']}", "sub": "Champion: England", "color": "#0D9488"},
        {"title": "Total Runs Scored", "value": f"{kpis['total_runs_scored']:,}", "sub": "Avg ~140 runs/innings", "color": "#D97706"},
        {"title": "Total Wickets Taken", "value": f"{kpis['total_wickets_taken']}", "sub": "515 Wickets across 82 Inn", "color": "#DC2626"},
        {"title": "Boundary Run %", "value": f"{kpis['boundary_runs_percentage']}%", "sub": f"{kpis['total_fours']} Fours | {kpis['total_sixes']} Sixes", "color": "#7C3AED"},
        {"title": "Total Dot Balls", "value": f"{kpis['total_dot_balls']:,}", "sub": "40.1% Dot Ball Ratio", "color": "#2563EB"},
    ]

    fig.text(0.5, 0.92, "ICC Men's T20 World Cup 2022 - Headline Tournament KPIs",
             ha="center", fontsize=18, fontweight="bold", color="#0F172A")
    fig.text(0.5, 0.86, "Australia | October 16 - November 13, 2022 | Source: ESPNcricinfo Match Scorecards",
             ha="center", fontsize=11, color="#64748B")

    # Render 2 rows x 3 columns of metric cards
    x_coords = [0.08, 0.38, 0.68]
    y_coords = [0.48, 0.12]

    idx = 0
    for r in range(2):
        for c in range(3):
            card = cards[idx]
            x, y = x_coords[c], y_coords[r]
            w, h = 0.25, 0.30

            rect = FancyBboxPatch((x, y), w, h, transform=fig.transFigure,
                                  facecolor="#FFFFFF", edgecolor="#E2E8F0",
                                  linewidth=1.5, boxstyle="round,pad=0.015")
            fig.patches.append(rect)

            # Left accent bar
            bar = Rectangle((x, y), 0.008, h, transform=fig.transFigure,
                            facecolor=card["color"], edgecolor=card["color"])
            fig.patches.append(bar)

            fig.text(x + 0.02, y + 0.22, card["title"], fontsize=11, color="#64748B", fontweight="semibold")
            fig.text(x + 0.02, y + 0.10, card["value"], fontsize=22, color=card["color"], fontweight="bold")
            fig.text(x + 0.02, y + 0.03, card["sub"], fontsize=9, color="#94A3B8")
            idx += 1

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_top_run_scorers(top_scorers: pd.DataFrame, save_path: str = None):
    """Horizontal bar chart for top 10 tournament run-scorers."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "02_top_run_scorers.png")

    fig, ax = plt.subplots(figsize=(11, 7), facecolor="#FFFFFF")
    df = top_scorers.sort_values(by="total_runs", ascending=True).copy()

    colors = ["#3B82F6" if p != "Virat Kohli" else "#F59E0B" for p in df["player_name"]]
    bars = ax.barh(df["player_name"], df["total_runs"], color=colors, height=0.65, edgecolor="#1E293B", linewidth=0.5)

    ax.set_title("Top 10 Run-Scorers of T20 World Cup 2022", pad=15)
    ax.set_xlabel("Total Runs Scored")
    ax.set_ylabel("")
    ax.set_xlim(0, max(df["total_runs"]) + 45)

    for bar, (_, row) in zip(bars, df.iterrows()):
        w = bar.get_width()
        label = f"{int(w)} runs (Avg: {row['batting_average']:.1f} | SR: {row['strike_rate']:.1f}) - {row['team_innings']}"
        ax.text(w + 4, bar.get_y() + bar.get_height() / 2, label,
                ha="left", va="center", fontsize=9.5, color="#1E293B", fontweight="medium")

    # Add subtitle
    plt.suptitle("Leading Tournament Batsmen | Virat Kohli secured Golden Bat (296 Runs, Avg 98.7)",
                 fontsize=10.5, color="#64748B", y=0.92)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_top_wicket_takers(top_bowlers: pd.DataFrame, save_path: str = None):
    """Bar chart for top 10 tournament wicket-takers."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "03_top_wicket_takers.png")

    fig, ax = plt.subplots(figsize=(11, 7), facecolor="#FFFFFF")
    df = top_bowlers.sort_values(by="wickets", ascending=True).copy()

    colors = ["#10B981" if p != "Wanindu Hasaranga de Silva" and p != "Sam Curran" else "#047857" for p in df["player_name"]]
    bars = ax.barh(df["player_name"], df["wickets"], color=colors, height=0.65, edgecolor="#064E3B", linewidth=0.5)

    ax.set_title("Top 10 Wicket-Takers of T20 World Cup 2022", pad=15)
    ax.set_xlabel("Total Wickets Taken")
    ax.set_ylabel("")
    ax.set_xlim(0, max(df["wickets"]) + 3)

    for bar, (_, row) in zip(bars, df.iterrows()):
        w = bar.get_width()
        label = f"{int(w)} wkts (Econ: {row['economy_rate']:.2f} | Avg: {row['bowling_average']:.1f}) - {row['bowling_team']}"
        ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, label,
                ha="left", va="center", fontsize=9.5, color="#1E293B", fontweight="medium")

    plt.suptitle("Leading Tournament Bowlers | Hasaranga (15 wkts) & Player of Tournament Sam Curran (13 wkts)",
                 fontsize=10.5, color="#64748B", y=0.92)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_batting_first_vs_chasing(matches: pd.DataFrame, save_path: str = None):
    """Donut chart and venue comparison for Defending vs Chasing."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "04_batting_first_vs_chasing.png")

    completed = matches[~matches["winner"].isin(["abandoned", "no result"])].copy()
    win_counts = completed["win_type"].value_counts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor="#FFFFFF")

    # 1. Donut chart
    labels = win_counts.index
    sizes = win_counts.values
    colors = ["#3B82F6", "#10B981"]
    explode = (0.05, 0)

    wedges, texts, autotexts = ax1.pie(
        sizes, explode=explode, labels=labels, autopct="%1.1f%%",
        startangle=140, colors=colors, textprops=dict(color="#0F172A", fontsize=11, fontweight="semibold"),
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(12)
        at.set_color("white")
        at.set_weight("bold")

    ax1.set_title("Overall Tournament Win Distribution\n(41 Completed Matches)", pad=15)

    # 2. Venue-wise breakdown
    venue_df = completed.groupby(["ground", "win_type"]).size().unstack(fill_value=0)
    venue_df["Total"] = venue_df.sum(axis=1)
    venue_df.sort_values(by="Total", ascending=True, inplace=True)
    venue_plot = venue_df[["Defending (Bat 1st)", "Chasing (Bat 2nd)"]]

    venue_plot.plot(kind="barh", stacked=True, color=["#3B82F6", "#10B981"], ax=ax2, width=0.6, edgecolor="#1E293B", linewidth=0.4)
    ax2.set_title("Venue-Wise Match Outcomes (Defending vs Chasing)", pad=15)
    ax2.set_xlabel("Number of Matches Won")
    ax2.set_ylabel("")
    ax2.legend(title="Outcome", frameon=True, facecolor="#F8FAFC")

    plt.suptitle("Batting First vs Chasing Analysis: Teams batting first won 56.1% of completed matches",
                 fontsize=14, fontweight="bold", y=0.98)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_venue_performance(venue_df: pd.DataFrame, save_path: str = None):
    """Grouped bar chart of average 1st vs 2nd innings scores by venue."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "05_venue_wise_performance.png")

    fig, ax = plt.subplots(figsize=(11, 6), facecolor="#FFFFFF")
    df = venue_df.sort_values(by="avg_first_innings_score", ascending=False).copy()

    x = np.arange(len(df))
    width = 0.35

    rects1 = ax.bar(x - width/2, df["avg_first_innings_score"], width, label="1st Innings Average", color="#2563EB", edgecolor="#1E3A8A")
    rects2 = ax.bar(x + width/2, df["avg_second_innings_score"], width, label="2nd Innings Average", color="#93C5FD", edgecolor="#1E3A8A")

    ax.set_title("Venue Scoring Patterns: Average 1st vs 2nd Innings Score by Australian Ground", pad=15)
    ax.set_ylabel("Average Score (Runs)")
    ax.set_xticks(x)
    ax.set_xticklabels(df["ground"])
    ax.set_ylim(0, 190)
    ax.legend(frameon=True, facecolor="#F8FAFC")

    # Add score labels on bars
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{int(h)}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{int(h)}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_winning_margins(matches: pd.DataFrame, save_path: str = None):
    """Plots the distribution of winning margins in runs and wickets."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "06_team_win_margins_distribution.png")

    completed = matches[~matches["winner"].isin(["abandoned", "no result"])].copy()
    run_wins = completed[completed["margin_type"] == "runs"]["margin_value"]
    wicket_wins = completed[completed["margin_type"] == "wickets"]["margin_value"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), facecolor="#FFFFFF")

    # 1. Run victory margins
    sns.histplot(run_wins, bins=8, kde=True, color="#3B82F6", ax=ax1, edgecolor="#1E3A8A")
    ax1.set_title(f"Defending Victories by Runs (n={len(run_wins)})\nMedian Margin: {int(run_wins.median())} Runs", pad=12)
    ax1.set_xlabel("Margin of Victory (Runs)")
    ax1.set_ylabel("Match Frequency")

    # 2. Wicket victory margins
    wicket_counts = wicket_wins.value_counts().sort_index()
    sns.barplot(x=wicket_counts.index, y=wicket_counts.values, ax=ax2, palette="Blues_d", edgecolor="#1E3A8A")
    ax2.set_title(f"Chasing Victories by Wickets (n={len(wicket_wins)})\nMedian Margin: {int(wicket_wins.median())} Wickets in Hand", pad=12)
    ax2.set_xlabel("Wickets Remaining in Hand")
    ax2.set_ylabel("Match Frequency")

    plt.suptitle("Tournament Competitiveness: Winning Margin Distributions", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_boundary_and_strike_rate(batting: pd.DataFrame, save_path: str = None):
    """Scatter plot of Batting Strike Rate vs Batting Average (Min 75 runs)."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "07_boundary_strike_rate_analysis.png")

    agg = batting.groupby("player_name").agg(
        runs=("runs", "sum"),
        balls=("balls", "sum"),
        dismissals=("is_out", "sum"),
        fours=("fours", "sum"),
        sixes=("sixes", "sum")
    ).reset_index()

    df = agg[agg["runs"] >= 75].copy()
    df["batting_average"] = df.apply(lambda r: round(r["runs"] / r["dismissals"], 2) if r["dismissals"] > 0 else float(r["runs"]), axis=1)
    df["strike_rate"] = df.apply(lambda r: round((r["runs"] / r["balls"]) * 100, 2) if r["balls"] > 0 else 0.0, axis=1)

    fig, ax = plt.subplots(figsize=(11, 7), facecolor="#FFFFFF")
    scatter = ax.scatter(df["batting_average"], df["strike_rate"],
                         s=df["runs"] * 2.2, alpha=0.7, c=df["strike_rate"],
                         cmap="viridis", edgecolors="#1E293B", linewidth=0.8)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Strike Rate", rotation=270, labelpad=15)

    ax.set_title("Batsmen Efficiency Quadrant: Strike Rate vs Batting Average (Min 75 Runs)", pad=15)
    ax.set_xlabel("Batting Average")
    ax.set_ylabel("Batting Strike Rate")
    ax.axhline(130, color="#EF4444", linestyle="--", alpha=0.6, label="Benchmark SR (130)")
    ax.axvline(30, color="#6B7280", linestyle="--", alpha=0.6, label="Benchmark Avg (30)")

    # Label standout players
    standouts = ["Virat Kohli", "Suryakumar Yadav", "Jos Buttler", "Glenn Phillips", "Marcus Stoinis", "Rilee Rossouw", "Alex Hales", "Shadab Khan"]
    for _, row in df.iterrows():
        if row["player_name"] in standouts:
            ax.annotate(row["player_name"],
                        (row["batting_average"], row["strike_rate"]),
                        xytext=(5, 5), textcoords="offset points",
                        fontsize=9.5, fontweight="bold", color="#0F172A")

    ax.legend(loc="upper left", frameon=True, facecolor="#F8FAFC")
    plt.suptitle("Bubble size reflects total tournament runs scored", fontsize=10, color="#64748B", y=0.92)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_best_bowling_figures(best_bowling: pd.DataFrame, save_path: str = None):
    """Bar chart of best bowling match figures."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "08_best_bowling_figures.png")

    fig, ax = plt.subplots(figsize=(11, 6), facecolor="#FFFFFF")
    df = best_bowling.sort_values(by=["wickets", "runs_conceded"], ascending=[True, False]).copy()

    y_labels = [f"{r['player_name']} ({r['bowling_team']})" for _, r in df.iterrows()]
    bars = ax.barh(y_labels, df["wickets"], color="#0D9488", height=0.6, edgecolor="#134E4A")

    ax.set_title("Top 10 Individual Bowling Performances in a Match", pad=15)
    ax.set_xlabel("Wickets Taken in Match")
    ax.set_xlim(0, 6)

    for bar, (_, row) in zip(bars, df.iterrows()):
        w = bar.get_width()
        txt = f" {row['figures']} | Econ: {row['economy']:.1f} | Dots: {row['dot_balls']}"
        ax.text(w + 0.1, bar.get_y() + bar.get_height()/2, txt, va="center", fontsize=9.5, color="#0F172A")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_player_roles_distribution(players: pd.DataFrame, save_path: str = None):
    """Visualizes squad composition across playing roles."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "09_player_roles_distribution.png")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), facecolor="#FFFFFF")

    # Clean roles
    role_counts = players["playing_role"].replace("", "Specialist Batter").value_counts()
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#6B7280"]

    # Donut chart
    ax1.pie(role_counts.values, labels=role_counts.index, autopct="%1.1f%%",
            startangle=140, colors=colors[:len(role_counts)],
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
    ax1.set_title("Tournament Player Composition by Role\n(213 Unique Registered Players)", pad=15)

    # Batting style breakdown
    bat_style = players["batting_style"].value_counts()
    sns.barplot(x=bat_style.values, y=bat_style.index, ax=ax2, palette="Blues_r", edgecolor="#1E3A8A")
    ax2.set_title("Batting Hand Distribution", pad=15)
    ax2.set_xlabel("Number of Players")
    for i, v in enumerate(bat_style.values):
        ax2.text(v + 1, i, f"{v} ({v/len(players)*100:.1f}%)", va="center", fontsize=10, fontweight="bold")

    plt.suptitle("Player Profile Demographics & Squad Archetypes", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def plot_highest_team_totals(team_innings: pd.DataFrame, save_path: str = None):
    """Bar chart of the top 10 highest team match scores in the tournament."""
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "10_highest_team_totals.png")

    fig, ax = plt.subplots(figsize=(11, 6), facecolor="#FFFFFF")
    top_scores = team_innings.sort_values(by="total_runs", ascending=False).head(10).copy()
    top_scores.sort_values(by="total_runs", ascending=True, inplace=True)

    y_labels = [f"{r['team_innings']} ({r['score_str']}) vs {r['ground']}" for _, r in top_scores.iterrows()]
    bars = ax.barh(y_labels, top_scores["total_runs"], color="#6366F1", height=0.6, edgecolor="#312E81")

    ax.set_title("Top 10 Highest Team Innings Totals in T20 World Cup 2022", pad=15)
    ax.set_xlabel("Total Runs Scored")
    ax.set_xlim(0, 230)

    for bar, (_, row) in zip(bars, top_scores.iterrows()):
        w = bar.get_width()
        ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"{row['score_str']} (Inn {row['innings_order']})",
                va="center", fontsize=9.5, color="#1E293B", fontweight="bold")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info(f"Saved: {save_path}")


def generate_all_charts():
    """Generates and exports all 10 portfolio charts."""
    logging.info("Starting automated chart generation pipeline...")
    data = load_processed_data()
    m, bat, bowl, p, team_sum = data["matches"], data["batting"], data["bowling"], data["players"], data["team_summary"]
    analysis_res = run_full_analysis()

    plot_tournament_kpis(analysis_res["kpis"])
    plot_top_run_scorers(analysis_res["top_scorers"])
    plot_top_wicket_takers(analysis_res["top_bowlers"])
    plot_batting_first_vs_chasing(m)
    plot_venue_performance(analysis_res["venue_analysis"])
    plot_winning_margins(m)
    plot_boundary_and_strike_rate(bat)
    plot_best_bowling_figures(analysis_res["best_bowling_figures"])
    plot_player_roles_distribution(p)
    plot_highest_team_totals(get_team_innings_totals(bat, m))

    logging.info(f"Successfully generated all 10 charts in: {CHARTS_DIR}")


if __name__ == "__main__":
    generate_all_charts()
