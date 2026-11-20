"""
sql_runner.py
-------------
Automates SQLite database setup, loads processed datasets into relational tables,
and executes analytical SQL queries from sql/analysis_queries.sql.
"""

import os
import sys
import sqlite3
import logging
import pandas as pd

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "t20_world_cup.db")
SQL_FILE = os.path.join(PROJECT_ROOT, "sql", "analysis_queries.sql")


def build_sqlite_database(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Creates SQLite database and loads processed CSV files into tables."""
    conn = sqlite3.connect(db_path)
    processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")

    # Load CSVs
    matches_df = pd.read_csv(os.path.join(processed_dir, "matches_cleaned.csv"))
    players_df = pd.read_csv(os.path.join(processed_dir, "players_cleaned.csv"))
    batting_df = pd.read_csv(os.path.join(processed_dir, "batting_summary_cleaned.csv"))
    bowling_df = pd.read_csv(os.path.join(processed_dir, "bowling_summary_cleaned.csv"))

    # Write to SQLite
    matches_df.to_sql("dim_match_summary", conn, if_exists="replace", index=False)
    players_df.to_sql("dim_players", conn, if_exists="replace", index=False)
    batting_df.to_sql("fact_bating_summary", conn, if_exists="replace", index=False)
    bowling_df.to_sql("fact_bowling_summary", conn, if_exists="replace", index=False)

    logging.info(f"SQLite database built successfully at: {db_path}")
    return conn


def execute_sample_queries(conn: sqlite3.Connection):
    """Executes core analysis queries to verify database functionality."""
    queries = {
        "1. Headline Tournament Overview": """
            SELECT 
                COUNT(DISTINCT match_id) AS total_matches,
                SUM(CASE WHEN winner NOT IN ('abandoned', 'no result') THEN 1 ELSE 0 END) AS completed_matches,
                (SELECT SUM(runs) FROM fact_bating_summary) AS total_runs,
                (SELECT SUM(wickets) FROM fact_bowling_summary) AS total_wickets
            FROM dim_match_summary;
        """,
        "2. Top 5 Tournament Batsmen": """
            SELECT 
                player_name, 
                team_innings AS team, 
                SUM(runs) AS total_runs,
                ROUND(100.0 * SUM(runs) / NULLIF(SUM(balls), 0), 2) AS strike_rate
            FROM fact_bating_summary
            GROUP BY player_name, team_innings
            ORDER BY total_runs DESC
            LIMIT 5;
        """,
        "3. Top 5 Tournament Bowlers": """
            SELECT 
                player_name, 
                bowling_team, 
                SUM(wickets) AS total_wickets,
                ROUND(1.0 * SUM(runs_conceded) / NULLIF(SUM(wickets), 0), 2) AS bowling_average
            FROM fact_bowling_summary
            GROUP BY player_name, bowling_team
            ORDER BY total_wickets DESC
            LIMIT 5;
        """,
        "4. Batting 1st vs Chasing Win Split": """
            SELECT 
                win_type, 
                COUNT(*) AS victories,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dim_match_summary WHERE winner NOT IN ('abandoned', 'no result')), 1) AS win_pct
            FROM dim_match_summary
            WHERE winner NOT IN ('abandoned', 'no result')
            GROUP BY win_type;
        """
    }

    print("\n" + "="*70)
    print("SQL ANALYTICS ENGINE - VERIFICATION & SAMPLE OUTPUTS")
    print("="*70)

    for title, query in queries.items():
        print(f"\n>>> {title}:")
        df_res = pd.read_sql_query(query, conn)
        print(df_res.to_string(index=False))


def run_sql_pipeline():
    conn = build_sqlite_database()
    execute_sample_queries(conn)
    conn.close()


if __name__ == "__main__":
    run_sql_pipeline()
