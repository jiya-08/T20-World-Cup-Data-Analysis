"""
data_cleaning.py
----------------
Transforms raw T20 World Cup datasets into standardized, typed,
and deduplicated dimensional tables for analysis.
"""

import os
import sys
import re
import logging
from typing import Tuple, Dict, Any

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np

from src.data_processing import (
    load_all_raw_data,
    build_match_id_mapping,
    get_project_root
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def clean_player_name(raw_name: str) -> str:
    """
    Strips scraping artifacts, replacement chars (e.g. \ufffd, \xa0, \u2020),
    captain tags ((c)), and extraneous whitespace.
    """
    if not isinstance(raw_name, str):
        return ""
    # Remove unicode replacement character, non-breaking space, dagger
    cleaned = re.sub(r'[\ufffd\xa0†]', '', raw_name)
    # Remove captain annotations like '(c)' or '(C)'
    cleaned = re.sub(r'\s*\([cC]\)\s*', '', cleaned)
    # Collapse multiple spaces and strip ends
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def has_captain_tag(raw_name: str) -> int:
    """Returns 1 if the player name contains a captain tag '(c)', otherwise 0."""
    if not isinstance(raw_name, str):
        return 0
    return 1 if re.search(r'\([cC]\)', raw_name) else 0


def clean_matches_df(df_matches: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the match summary dimension table."""
    df = df_matches.copy()
    
    # Rename scorecard to match_id
    if "scorecard" in df.columns:
        df.rename(columns={"scorecard": "match_id"}, inplace=True)

    # Standardize match date
    df["match_date"] = pd.to_datetime(df["matchDate"], format="%b %d, %Y", errors="coerce").dt.strftime("%Y-%m-%d")
    df.drop(columns=["matchDate"], inplace=True, errors="ignore")

    # Classify match outcomes & margins
    def parse_margin(margin_str: str) -> Tuple[str, int, str]:
        if not isinstance(margin_str, str) or not margin_str.strip():
            return "no_result", 0, "No Result"
        
        m_lower = margin_str.lower().strip()
        if "run" in m_lower:
            val_match = re.search(r'\d+', m_lower)
            val = int(val_match.group()) if val_match else 0
            return "runs", val, "Defending (Bat 1st)"
        elif "wicket" in m_lower:
            val_match = re.search(r'\d+', m_lower)
            val = int(val_match.group()) if val_match else 0
            return "wickets", val, "Chasing (Bat 2nd)"
        else:
            return "no_result", 0, "No Result"

    margin_parsed = df["margin"].apply(parse_margin)
    df["margin_type"] = [item[0] for item in margin_parsed]
    df["margin_value"] = [item[1] for item in margin_parsed]
    df["win_type"] = [item[2] for item in margin_parsed]

    # Reorder columns
    cols = ["match_id", "team1", "team2", "winner", "win_type", "margin", "margin_type", "margin_value", "ground", "match_date"]
    df = df[cols]
    logging.info(f"Cleaned matches dataset: {len(df)} records.")
    return df


def clean_batting_df(df_batting: pd.DataFrame, match_mapping: Dict[str, str]) -> pd.DataFrame:
    """Cleans batting fact records with proper types and calculated metrics."""
    df = df_batting.copy()

    # Link match_id
    df["match_id"] = df["match"].map(match_mapping)

    # Clean player name
    df["player_name"] = df["batsmanName"].apply(clean_player_name)

    # Numeric conversions
    df["batting_pos"] = pd.to_numeric(df["battingPos"], errors="coerce").fillna(0).astype(int)
    df["runs"] = pd.to_numeric(df["runs"], errors="coerce").fillna(0).astype(int)
    df["balls"] = pd.to_numeric(df["balls"], errors="coerce").fillna(0).astype(int)
    df["fours"] = pd.to_numeric(df["4s"], errors="coerce").fillna(0).astype(int)
    df["sixes"] = pd.to_numeric(df["6s"], errors="coerce").fillna(0).astype(int)

    # Strike rate calculation (accurate recalculation)
    df["strike_rate"] = np.where(
        df["balls"] > 0,
        np.round((df["runs"] / df["balls"]) * 100, 2),
        0.0
    )

    # Dismissal indicator: 1 = out, 0 = not out
    df["is_out"] = df["dismissal"].apply(lambda x: 1 if str(x).strip() != "" and str(x).lower() != "not out" else 0)
    df["dismissal_status"] = df["is_out"].apply(lambda x: "out" if x == 1 else "not out")

    # Column renaming & ordering
    df.rename(columns={"teamInnings": "team_innings"}, inplace=True)
    cols = [
        "match_id", "match", "team_innings", "innings_order",
        "batting_pos", "player_name", "dismissal", "dismissal_status", "is_out",
        "runs", "balls", "fours", "sixes", "strike_rate"
    ]
    df = df[cols]
    logging.info(f"Cleaned batting dataset: {len(df)} innings records.")
    return df


def clean_bowling_df(df_bowling: pd.DataFrame, match_mapping: Dict[str, str]) -> pd.DataFrame:
    """Cleans bowling fact records with numerical typing and standard metrics."""
    df = df_bowling.copy()

    # Link match_id
    df["match_id"] = df["match"].map(match_mapping)

    # Clean player name
    df["player_name"] = df["bowlerName"].apply(clean_player_name)

    # Numeric fields
    df["overs"] = pd.to_numeric(df["overs"], errors="coerce").fillna(0.0)
    df["maiden"] = pd.to_numeric(df["maiden"], errors="coerce").fillna(0).astype(int)
    df["runs_conceded"] = pd.to_numeric(df["runs"], errors="coerce").fillna(0).astype(int)
    df["wickets"] = pd.to_numeric(df["wickets"], errors="coerce").fillna(0).astype(int)
    df["economy"] = pd.to_numeric(df["economy"], errors="coerce").fillna(0.0).round(2)
    df["dot_balls"] = pd.to_numeric(df["0s"], errors="coerce").fillna(0).astype(int)
    df["fours_conceded"] = pd.to_numeric(df["4s"], errors="coerce").fillna(0).astype(int)
    df["sixes_conceded"] = pd.to_numeric(df["6s"], errors="coerce").fillna(0).astype(int)
    df["wides"] = pd.to_numeric(df["wides"], errors="coerce").fillna(0).astype(int)
    df["no_balls"] = pd.to_numeric(df["noBalls"], errors="coerce").fillna(0).astype(int)

    # Standardize column names
    df.rename(columns={"bowlingTeam": "bowling_team"}, inplace=True)
    cols = [
        "match_id", "match", "bowling_team", "player_name",
        "overs", "maiden", "runs_conceded", "wickets",
        "economy", "dot_balls", "fours_conceded", "sixes_conceded",
        "wides", "no_balls"
    ]
    df = df[cols]
    logging.info(f"Cleaned bowling dataset: {len(df)} spell records.")
    return df


def clean_players_df(df_players: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans player dimension table: standardizes names, captures captaincy,
    and deduplicates records scraped both with and without captain tags.
    """
    df = df_players.copy()

    # Capture captaincy flag
    df["is_captain"] = df["name"].apply(has_captain_tag)
    df["player_name"] = df["name"].apply(clean_player_name)

    # Standardize column names
    df.rename(columns={
        "battingStyle": "batting_style",
        "bowlingStyle": "bowling_style",
        "playingRole": "playing_role"
    }, inplace=True)

    # Sort so captaincy and longer descriptions take precedence when dropping duplicates
    df.sort_values(by=["player_name", "is_captain", "description"], ascending=[True, False, False], inplace=True)
    df_dedup = df.drop_duplicates(subset=["player_name"], keep="first").copy()

    cols = ["player_name", "team", "batting_style", "bowling_style", "playing_role", "is_captain", "description"]
    df_dedup = df_dedup[cols].reset_index(drop=True)
    logging.info(f"Cleaned players master dimension: {len(df_dedup)} unique players (deduplicated from {len(df)}).")
    return df_dedup


def generate_team_summary(df_matches: pd.DataFrame, df_batting: pd.DataFrame, df_bowling: pd.DataFrame) -> pd.DataFrame:
    """Generates comprehensive aggregated team statistics across the tournament."""
    teams = sorted(list(set(df_matches["team1"]).union(set(df_matches["team2"]))))
    summary_records = []

    for team in teams:
        m_team = df_matches[(df_matches["team1"] == team) | (df_matches["team2"] == team)]
        total_matches = len(m_team)
        wins = len(df_matches[df_matches["winner"] == team])
        no_res = len(m_team[m_team["winner"].isin(["abandoned", "no result"])])
        losses = total_matches - wins - no_res
        win_pct = round((wins / (total_matches - no_res)) * 100, 2) if (total_matches - no_res) > 0 else 0.0

        wins_defending = len(df_matches[(df_matches["winner"] == team) & (df_matches["win_type"] == "Defending (Bat 1st)")])
        wins_chasing = len(df_matches[(df_matches["winner"] == team) & (df_matches["win_type"] == "Chasing (Bat 2nd)")])

        team_runs = df_batting[df_batting["team_innings"] == team]["runs"].sum()
        team_wickets = df_bowling[df_bowling["bowling_team"] == team]["wickets"].sum()

        summary_records.append({
            "team": team,
            "matches_played": total_matches,
            "wins": wins,
            "losses": losses,
            "no_results": no_res,
            "win_percentage": win_pct,
            "wins_defending": wins_defending,
            "wins_chasing": wins_chasing,
            "total_runs_scored": team_runs,
            "total_wickets_taken": team_wickets
        })

    df_summary = pd.DataFrame(summary_records).sort_values(by=["wins", "win_percentage"], ascending=False).reset_index(drop=True)
    logging.info(f"Generated team summary for {len(df_summary)} participating teams.")
    return df_summary


def run_data_cleaning_pipeline(raw_dir: str = None, processed_dir: str = None) -> Dict[str, pd.DataFrame]:
    """Runs the full data cleaning pipeline and saves output CSVs."""
    root = get_project_root()
    if raw_dir is None:
        raw_dir = os.path.join(root, "data", "raw")
    if processed_dir is None:
        processed_dir = os.path.join(root, "data", "processed")

    os.makedirs(processed_dir, exist_ok=True)

    # 1. Load raw datasets
    df_raw_matches, df_raw_batting, df_raw_bowling, df_raw_players = load_all_raw_data(raw_dir)

    # 2. Build mapping
    match_mapping = build_match_id_mapping(df_raw_matches)

    # 3. Clean datasets
    df_clean_matches = clean_matches_df(df_raw_matches)
    df_clean_batting = clean_batting_df(df_raw_batting, match_mapping)
    df_clean_bowling = clean_bowling_df(df_raw_bowling, match_mapping)
    df_clean_players = clean_players_df(df_raw_players)

    # 4. Generate team summary
    df_team_summary = generate_team_summary(df_clean_matches, df_clean_batting, df_clean_bowling)

    # 5. Export to data/processed/
    df_clean_matches.to_csv(os.path.join(processed_dir, "matches_cleaned.csv"), index=False)
    df_clean_batting.to_csv(os.path.join(processed_dir, "batting_summary_cleaned.csv"), index=False)
    df_clean_bowling.to_csv(os.path.join(processed_dir, "bowling_summary_cleaned.csv"), index=False)
    df_clean_players.to_csv(os.path.join(processed_dir, "players_cleaned.csv"), index=False)
    df_team_summary.to_csv(os.path.join(processed_dir, "team_performance_summary.csv"), index=False)

    logging.info(f"Pipeline executed successfully. Processed CSV files saved to: {processed_dir}")

    return {
        "matches": df_clean_matches,
        "batting": df_clean_batting,
        "bowling": df_clean_bowling,
        "players": df_clean_players,
        "team_summary": df_team_summary
    }


if __name__ == "__main__":
    result = run_data_cleaning_pipeline()
    for name, df in result.items():
        print(f"Dataset '{name}' shape: {df.shape}")
