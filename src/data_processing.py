"""
data_processing.py
------------------
Responsible for loading raw JSON datasets, flattening nested structures,
and establishing relational match mappings.
"""

import os
import json
import logging
from typing import Dict, List, Tuple
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_project_root() -> str:
    """Returns the absolute path to the project root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, ".."))


def load_raw_matches(raw_data_dir: str = None) -> pd.DataFrame:
    """Loads and returns the raw match summary data as a DataFrame."""
    if raw_data_dir is None:
        raw_data_dir = os.path.join(get_project_root(), "data", "raw")
    filepath = os.path.join(raw_data_dir, "t20_wc_match_results.json")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Match results file not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    df_matches = pd.DataFrame(data[0]["matchSummary"])
    logging.info(f"Loaded {len(df_matches)} raw match records from {filepath}")
    return df_matches


def build_match_id_mapping(df_matches: pd.DataFrame) -> Dict[str, str]:
    """
    Constructs a bidirectional lookup dictionary for match fixtures to match_id.
    Handles 'Team A Vs Team B' and 'Team B Vs Team A'.
    """
    id_col = "scorecard" if "scorecard" in df_matches.columns else "match_id"
    mapping = {}
    for _, row in df_matches.iterrows():
        fixture1 = f"{row['team1']} Vs {row['team2']}"
        fixture2 = f"{row['team2']} Vs {row['team1']}"
        m_id = row[id_col]
        mapping[fixture1] = m_id
        mapping[fixture2] = m_id
    logging.info(f"Built match_id lookup dictionary with {len(mapping)} fixture variations.")
    return mapping


def load_raw_batting(raw_data_dir: str = None) -> pd.DataFrame:
    """
    Loads raw batting JSON and flattens it, tracking innings order (1st vs 2nd innings).
    """
    if raw_data_dir is None:
        raw_data_dir = os.path.join(get_project_root(), "data", "raw")
    filepath = os.path.join(raw_data_dir, "t20_wc_batting_summary.json")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Batting summary file not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_records = []
    for match_entry in data:
        summary_list = match_entry.get("battingSummary", [])
        innings_seen = []
        for row in summary_list:
            team = row.get("teamInnings")
            if team not in innings_seen:
                innings_seen.append(team)
            row_copy = row.copy()
            # 1 for first batting, 2 for chasing
            row_copy["innings_order"] = innings_seen.index(team) + 1
            all_records.append(row_copy)

    df_batting = pd.DataFrame(all_records)
    logging.info(f"Loaded {len(df_batting)} raw batting innings from {filepath}")
    return df_batting


def load_raw_bowling(raw_data_dir: str = None) -> pd.DataFrame:
    """Loads raw bowling JSON and flattens it into a DataFrame."""
    if raw_data_dir is None:
        raw_data_dir = os.path.join(get_project_root(), "data", "raw")
    filepath = os.path.join(raw_data_dir, "t20_wc_bowling_summary.json")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Bowling summary file not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_records = []
    for match_entry in data:
        all_records.extend(match_entry.get("bowlingSummary", []))

    df_bowling = pd.DataFrame(all_records)
    logging.info(f"Loaded {len(df_bowling)} raw bowling spell records from {filepath}")
    return df_bowling


def load_raw_players(raw_data_dir: str = None) -> pd.DataFrame:
    """Loads raw player info JSON into a DataFrame."""
    if raw_data_dir is None:
        raw_data_dir = os.path.join(get_project_root(), "data", "raw")
    filepath = os.path.join(raw_data_dir, "t20_wc_player_info.json")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Player info file not found at: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    df_players = pd.DataFrame(data)
    logging.info(f"Loaded {len(df_players)} raw player profiles from {filepath}")
    return df_players


def load_all_raw_data(raw_data_dir: str = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Convenience function to load all 4 raw datasets at once."""
    df_matches = load_raw_matches(raw_data_dir)
    df_batting = load_raw_batting(raw_data_dir)
    df_bowling = load_raw_bowling(raw_data_dir)
    df_players = load_raw_players(raw_data_dir)
    return df_matches, df_batting, df_bowling, df_players


if __name__ == "__main__":
    matches, batting, bowling, players = load_all_raw_data()
    print("Match results shape:", matches.shape)
    print("Batting summary shape:", batting.shape)
    print("Bowling summary shape:", bowling.shape)
    print("Players shape:", players.shape)
