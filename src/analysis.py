"""
analysis.py
-----------
Comprehensive statistical analysis module for the T20 World Cup dataset.
Generates analytical summaries, KPI metrics, player rankings, and venue insights.
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_processed_data(processed_dir: str = None) -> Dict[str, pd.DataFrame]:
    """Loads all cleaned datasets from data/processed/."""
    if processed_dir is None:
        processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")

    matches = pd.read_csv(os.path.join(processed_dir, "matches_cleaned.csv"))
    batting = pd.read_csv(os.path.join(processed_dir, "batting_summary_cleaned.csv"))
    bowling = pd.read_csv(os.path.join(processed_dir, "bowling_summary_cleaned.csv"))
    players = pd.read_csv(os.path.join(processed_dir, "players_cleaned.csv"))
    team_summary = pd.read_csv(os.path.join(processed_dir, "team_performance_summary.csv"))

    return {
        "matches": matches,
        "batting": batting,
        "bowling": bowling,
        "players": players,
        "team_summary": team_summary
    }


def get_tournament_kpis(matches: pd.DataFrame, batting: pd.DataFrame, bowling: pd.DataFrame) -> Dict[str, Any]:
    """Calculates headline KPIs for the tournament overview."""
    total_matches = len(matches)
    completed_matches = len(matches[~matches["winner"].isin(["abandoned", "no result"])])
    abandoned_matches = total_matches - completed_matches

    all_teams = set(matches["team1"]).union(set(matches["team2"]))
    total_teams = len(all_teams)

    total_runs = int(batting["runs"].sum())
    total_balls = int(batting["balls"].sum())
    total_fours = int(batting["fours"].sum())
    total_sixes = int(batting["sixes"].sum())
    boundary_runs = (total_fours * 4) + (total_sixes * 6)
    boundary_run_pct = round((boundary_runs / total_runs) * 100, 2) if total_runs > 0 else 0.0

    total_wickets = int(bowling["wickets"].sum())
    total_maidens = int(bowling["maiden"].sum())
    total_dots = int(bowling["dot_balls"].sum())

    # Champion is winner of final match (T20I # 1879)
    champion = matches[matches["match_id"] == "T20I # 1879"]["winner"].values
    tournament_winner = champion[0] if len(champion) > 0 else "England"

    return {
        "total_matches_scheduled": total_matches,
        "completed_matches": completed_matches,
        "abandoned_or_no_result": abandoned_matches,
        "total_participating_teams": total_teams,
        "tournament_champion": tournament_winner,
        "total_runs_scored": total_runs,
        "total_balls_faced": total_balls,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "boundary_runs_percentage": boundary_run_pct,
        "total_wickets_taken": total_wickets,
        "total_maidens_bowled": total_maidens,
        "total_dot_balls": total_dots
    }


def get_batting_first_vs_chasing_analysis(matches: pd.DataFrame) -> Dict[str, Any]:
    """Evaluates the win distribution between teams batting first and chasing."""
    completed = matches[~matches["winner"].isin(["abandoned", "no result"])].copy()
    total_completed = len(completed)

    win_type_counts = completed["win_type"].value_counts().to_dict()
    defending_wins = win_type_counts.get("Defending (Bat 1st)", 0)
    chasing_wins = win_type_counts.get("Chasing (Bat 2nd)", 0)

    defending_pct = round((defending_wins / total_completed) * 100, 2) if total_completed > 0 else 0.0
    chasing_pct = round((chasing_wins / total_completed) * 100, 2) if total_completed > 0 else 0.0

    # Venue breakdown
    venue_breakdown = completed.groupby(["ground", "win_type"]).size().unstack(fill_value=0)
    venue_breakdown["Total"] = venue_breakdown.sum(axis=1)
    if "Defending (Bat 1st)" in venue_breakdown.columns:
        venue_breakdown["Defending_Win_Pct"] = round((venue_breakdown["Defending (Bat 1st)"] / venue_breakdown["Total"]) * 100, 1)

    return {
        "completed_matches": total_completed,
        "defending_wins": defending_wins,
        "chasing_wins": chasing_wins,
        "defending_win_percentage": defending_pct,
        "chasing_win_percentage": chasing_pct,
        "venue_win_breakdown": venue_breakdown.reset_index()
    }


def get_top_run_scorers(batting: pd.DataFrame, min_innings: int = 1, limit: int = 10) -> pd.DataFrame:
    """Aggregates and ranks the top batsmen of the tournament."""
    agg = batting.groupby(["player_name", "team_innings"]).agg(
        innings=("match_id", "nunique"),
        total_runs=("runs", "sum"),
        balls_faced=("balls", "sum"),
        dismissals=("is_out", "sum"),
        fours=("fours", "sum"),
        sixes=("sixes", "sum"),
        highest_score=("runs", "max"),
        fifties=("runs", lambda x: (x >= 50).sum() - (x >= 100).sum()),
        hundreds=("runs", lambda x: (x >= 100).sum())
    ).reset_index()

    agg = agg[agg["innings"] >= min_innings].copy()
    agg["batting_average"] = agg.apply(
        lambda r: round(r["total_runs"] / r["dismissals"], 2) if r["dismissals"] > 0 else float(r["total_runs"]),
        axis=1
    )
    agg["strike_rate"] = agg.apply(
        lambda r: round((r["total_runs"] / r["balls_faced"]) * 100, 2) if r["balls_faced"] > 0 else 0.0,
        axis=1
    )
    agg["boundary_runs"] = (agg["fours"] * 4) + (agg["sixes"] * 6)
    agg["boundary_run_pct"] = round((agg["boundary_runs"] / agg["total_runs"]) * 100, 2)

    top_scorers = agg.sort_values(by=["total_runs", "batting_average"], ascending=[False, False]).head(limit).reset_index(drop=True)
    return top_scorers


def get_top_wicket_takers(bowling: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Aggregates and ranks the leading wicket-takers of the tournament."""
    agg = bowling.groupby(["player_name", "bowling_team"]).agg(
        spells=("match_id", "nunique"),
        total_overs=("overs", "sum"),
        maidens=("maiden", "sum"),
        runs_conceded=("runs_conceded", "sum"),
        wickets=("wickets", "sum"),
        dot_balls=("dot_balls", "sum"),
        best_wickets=("wickets", "max"),
        four_wickets=("wickets", lambda x: (x == 4).sum()),
        five_wickets=("wickets", lambda x: (x >= 5).sum())
    ).reset_index()

    agg["bowling_average"] = agg.apply(
        lambda r: round(r["runs_conceded"] / r["wickets"], 2) if r["wickets"] > 0 else 0.0,
        axis=1
    )
    # Calculate approximate balls bowled from overs
    agg["approx_balls"] = agg["total_overs"].apply(lambda ov: int(ov) * 6 + int(round((ov % 1) * 10)))
    agg["bowling_strike_rate"] = agg.apply(
        lambda r: round(r["approx_balls"] / r["wickets"], 2) if r["wickets"] > 0 else 0.0,
        axis=1
    )
    agg["economy_rate"] = agg.apply(
        lambda r: round((r["runs_conceded"] / r["approx_balls"]) * 6, 2) if r["approx_balls"] > 0 else 0.0,
        axis=1
    )
    agg["dot_ball_pct"] = agg.apply(
        lambda r: round((r["dot_balls"] / r["approx_balls"]) * 100, 2) if r["approx_balls"] > 0 else 0.0,
        axis=1
    )

    top_bowlers = agg.sort_values(by=["wickets", "bowling_average"], ascending=[False, True]).head(limit).reset_index(drop=True)
    return top_bowlers


def get_best_bowling_figures(bowling: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Finds best match figures (e.g. 5/10 by Sam Curran)."""
    df = bowling.copy()
    df["figures"] = df.apply(lambda r: f"{r['wickets']}/{r['runs_conceded']} ({r['overs']} ov)", axis=1)
    best = df.sort_values(by=["wickets", "runs_conceded"], ascending=[False, True]).head(limit).reset_index(drop=True)
    cols = ["match_id", "player_name", "bowling_team", "figures", "wickets", "runs_conceded", "overs", "economy", "dot_balls"]
    return best[cols]


def get_highest_individual_scores(batting: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Finds the top individual batting innings in a single match."""
    df = batting.copy()
    top = df.sort_values(by=["runs", "strike_rate"], ascending=[False, False]).head(limit).reset_index(drop=True)
    cols = ["match_id", "player_name", "team_innings", "runs", "balls", "fours", "sixes", "strike_rate", "dismissal_status"]
    return top[cols]


def get_team_innings_totals(batting: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Computes total score and wickets lost for each team in each match innings."""
    totals = batting.groupby(["match_id", "team_innings", "innings_order"]).agg(
        total_runs=("runs", "sum"),
        wickets_lost=("is_out", "sum"),
        balls_faced=("balls", "sum")
    ).reset_index()

    totals = totals.merge(matches[["match_id", "ground", "winner", "match_date"]], on="match_id", how="left")
    totals["score_str"] = totals.apply(lambda r: f"{r['total_runs']}/{r['wickets_lost']}", axis=1)
    return totals


def get_venue_performance(matches: pd.DataFrame, batting: pd.DataFrame) -> pd.DataFrame:
    """Computes venue-level metrics: matches hosted, average 1st innings score, boundary rates."""
    innings_totals = get_team_innings_totals(batting, matches)
    first_inn = innings_totals[innings_totals["innings_order"] == 1]
    second_inn = innings_totals[innings_totals["innings_order"] == 2]

    venue_stats = matches.groupby("ground").agg(
        matches_played=("match_id", "count"),
        completed_matches=("winner", lambda x: sum(~x.isin(["abandoned", "no result"])))
    ).reset_index()

    avg_1st = first_inn.groupby("ground")["total_runs"].mean().round(1).reset_index(name="avg_first_innings_score")
    avg_2nd = second_inn.groupby("ground")["total_runs"].mean().round(1).reset_index(name="avg_second_innings_score")
    highest_score = innings_totals.groupby("ground")["total_runs"].max().reset_index(name="highest_score")

    venue_df = venue_stats.merge(avg_1st, on="ground", how="left").merge(avg_2nd, on="ground", how="left").merge(highest_score, on="ground", how="left")
    return venue_df.sort_values(by="matches_played", ascending=False).reset_index(drop=True)


def run_full_analysis() -> Dict[str, Any]:
    """Runs all analyses and returns structured dictionary."""
    data = load_processed_data()
    m, bat, bowl, p, team_sum = data["matches"], data["batting"], data["bowling"], data["players"], data["team_summary"]

    kpis = get_tournament_kpis(m, bat, bowl)
    defending_vs_chasing = get_batting_first_vs_chasing_analysis(m)
    top_scorers = get_top_run_scorers(bat, limit=10)
    top_bowlers = get_top_wicket_takers(bowl, limit=10)
    best_bowling_figures = get_best_bowling_figures(bowl, limit=10)
    highest_scores = get_highest_individual_scores(bat, limit=10)
    venue_analysis = get_venue_performance(m, bat)
    team_innings = get_team_innings_totals(bat, m)

    highest_team_totals = team_innings.sort_values(by="total_runs", ascending=False).head(5)
    lowest_team_totals = team_innings.sort_values(by="total_runs", ascending=True).head(5)

    logging.info("Completed full statistical analysis successfully.")

    return {
        "kpis": kpis,
        "defending_vs_chasing": defending_vs_chasing,
        "top_scorers": top_scorers,
        "top_bowlers": top_bowlers,
        "best_bowling_figures": best_bowling_figures,
        "highest_scores": highest_scores,
        "venue_analysis": venue_analysis,
        "highest_team_totals": highest_team_totals,
        "lowest_team_totals": lowest_team_totals,
        "team_summary": team_sum
    }


if __name__ == "__main__":
    results = run_full_analysis()
    print("--- TOURNAMENT KPIS ---")
    for k, v in results["kpis"].items():
        print(f"  {k}: {v}")
    print("\n--- TOP 5 BATSMEN ---")
    print(results["top_scorers"][["player_name", "team_innings", "total_runs", "batting_average", "strike_rate"]].head(5))
    print("\n--- TOP 5 BOWLERS ---")
    print(results["top_bowlers"][["player_name", "bowling_team", "wickets", "bowling_average", "economy_rate"]].head(5))
