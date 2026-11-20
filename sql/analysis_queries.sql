-- ==============================================================================
-- ICC MEN'S T20 WORLD CUP 2022 - COMPREHENSIVE SQL ANALYTICS SUITE
-- Compatible with SQLite, PostgreSQL, MySQL, and DuckDB
-- ==============================================================================
-- Description:
-- Production-ready analytical queries demonstrating relational schema modeling,
-- Common Table Expressions (CTEs), Window Functions (DENSE_RANK, ROW_NUMBER),
-- Aggregations, and Business Intelligence insights.
-- ==============================================================================


-- ==============================================================================
-- SECTION 1: SCHEMA DEFINITIONS (DDL)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS dim_match_summary (
    match_id        VARCHAR(20) PRIMARY KEY,
    team1           VARCHAR(50) NOT NULL,
    team2           VARCHAR(50) NOT NULL,
    winner          VARCHAR(50) NOT NULL,
    win_type        VARCHAR(30) NOT NULL,
    margin          VARCHAR(30),
    margin_type     VARCHAR(20),
    margin_value    INTEGER,
    ground          VARCHAR(50) NOT NULL,
    match_date      DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_players (
    player_name     VARCHAR(100) PRIMARY KEY,
    team            VARCHAR(50) NOT NULL,
    batting_style   VARCHAR(50),
    bowling_style   VARCHAR(50),
    playing_role    VARCHAR(50),
    is_captain      INTEGER DEFAULT 0,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS fact_bating_summary (
    match_id            VARCHAR(20) NOT NULL,
    match               VARCHAR(100) NOT NULL,
    team_innings        VARCHAR(50) NOT NULL,
    innings_order       INTEGER NOT NULL,
    batting_pos         INTEGER NOT NULL,
    player_name         VARCHAR(100) NOT NULL,
    dismissal           VARCHAR(100),
    dismissal_status    VARCHAR(20),
    is_out              INTEGER NOT NULL,
    runs                INTEGER NOT NULL,
    balls               INTEGER NOT NULL,
    fours               INTEGER NOT NULL,
    sixes               INTEGER NOT NULL,
    strike_rate         REAL NOT NULL,
    FOREIGN KEY (match_id) REFERENCES dim_match_summary(match_id),
    FOREIGN KEY (player_name) REFERENCES dim_players(player_name)
);

CREATE TABLE IF NOT EXISTS fact_bowling_summary (
    match_id            VARCHAR(20) NOT NULL,
    match               VARCHAR(100) NOT NULL,
    bowling_team        VARCHAR(50) NOT NULL,
    player_name         VARCHAR(100) NOT NULL,
    overs               REAL NOT NULL,
    maiden              INTEGER NOT NULL,
    runs_conceded       INTEGER NOT NULL,
    wickets             INTEGER NOT NULL,
    economy             REAL NOT NULL,
    dot_balls           INTEGER NOT NULL,
    fours_conceded      INTEGER NOT NULL,
    sixes_conceded      INTEGER NOT NULL,
    wides               INTEGER NOT NULL,
    no_balls            INTEGER NOT NULL,
    FOREIGN KEY (match_id) REFERENCES dim_match_summary(match_id),
    FOREIGN KEY (player_name) REFERENCES dim_players(player_name)
);


-- ==============================================================================
-- SECTION 2: TOURNAMENT OVERVIEW & MATCH METRICS
-- ==============================================================================

-- Query 1: Headline Tournament Metrics
-- Provides an executive summary of matches, completions, runs, and wickets.
SELECT 
    COUNT(DISTINCT m.match_id) AS total_matches_scheduled,
    SUM(CASE WHEN m.winner NOT IN ('abandoned', 'no result') THEN 1 ELSE 0 END) AS completed_matches,
    SUM(CASE WHEN m.winner IN ('abandoned', 'no result') THEN 1 ELSE 0 END) AS abandoned_matches,
    COUNT(DISTINCT p.player_name) AS total_players_registered,
    (SELECT SUM(runs) FROM fact_bating_summary) AS total_tournament_runs,
    (SELECT SUM(wickets) FROM fact_bowling_summary) AS total_tournament_wickets,
    (SELECT SUM(fours) FROM fact_bating_summary) AS total_fours,
    (SELECT SUM(sixes) FROM fact_bating_summary) AS total_sixes
FROM dim_match_summary m
LEFT JOIN dim_players p ON 1=1;


-- Query 2: Team Tournament Standings & Win Conversion
-- Computes matches played, wins, losses, win %, and split between defending & chasing.
WITH team_matches AS (
    SELECT team1 AS team, match_id, winner, win_type FROM dim_match_summary
    UNION ALL
    SELECT team2 AS team, match_id, winner, win_type FROM dim_match_summary
)
SELECT 
    team,
    COUNT(match_id) AS matches_played,
    SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN winner != team AND winner NOT IN ('abandoned', 'no result') THEN 1 ELSE 0 END) AS losses,
    SUM(CASE WHEN winner IN ('abandoned', 'no result') THEN 1 ELSE 0 END) AS no_results,
    ROUND(
        100.0 * SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(match_id) - SUM(CASE WHEN winner IN ('abandoned', 'no result') THEN 1 ELSE 0 END), 0), 
        2
    ) AS win_percentage,
    SUM(CASE WHEN winner = team AND win_type = 'Defending (Bat 1st)' THEN 1 ELSE 0 END) AS wins_defending,
    SUM(CASE WHEN winner = team AND win_type = 'Chasing (Bat 2nd)' THEN 1 ELSE 0 END) AS wins_chasing
FROM team_matches
GROUP BY team
ORDER BY wins DESC, win_percentage DESC;


-- ==============================================================================
-- SECTION 3: BATTING FIRST VS CHASING DYNAMICS
-- ==============================================================================

-- Query 3: Overall Win Distribution: Batting First (Defending) vs Chasing
SELECT 
    win_type,
    COUNT(*) AS total_victories,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dim_match_summary WHERE winner NOT IN ('abandoned', 'no result')), 2) AS win_percentage
FROM dim_match_summary
WHERE winner NOT IN ('abandoned', 'no result')
GROUP BY win_type
ORDER BY total_victories DESC;


-- Query 4: Venue-Wise Batting Advantage
-- Determines whether specific Australian venues favored teams batting first or chasing.
SELECT 
    ground,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN win_type = 'Defending (Bat 1st)' THEN 1 ELSE 0 END) AS defending_wins,
    SUM(CASE WHEN win_type = 'Chasing (Bat 2nd)' THEN 1 ELSE 0 END) AS chasing_wins,
    ROUND(100.0 * SUM(CASE WHEN win_type = 'Defending (Bat 1st)' THEN 1 ELSE 0 END) / COUNT(*), 1) AS defending_win_pct,
    ROUND(100.0 * SUM(CASE WHEN win_type = 'Chasing (Bat 2nd)' THEN 1 ELSE 0 END) / COUNT(*), 1) AS chasing_win_pct
FROM dim_match_summary
WHERE winner NOT IN ('abandoned', 'no result')
GROUP BY ground
ORDER BY total_matches DESC;


-- ==============================================================================
-- SECTION 4: BATTING LEADERBOARDS & ADVANCED METRICS
-- ==============================================================================

-- Query 5: Top 10 Run-Scorers with Average, Strike Rate, and Boundary Contribution
WITH player_batting AS (
    SELECT 
        player_name,
        team_innings AS team,
        COUNT(DISTINCT match_id) AS innings_batted,
        SUM(runs) AS total_runs,
        SUM(balls) AS total_balls,
        SUM(is_out) AS total_dismissals,
        SUM(fours) AS total_fours,
        SUM(sixes) AS total_sixes,
        MAX(runs) AS highest_score,
        SUM(CASE WHEN runs >= 50 AND runs < 100 THEN 1 ELSE 0 END) AS fifties,
        SUM(CASE WHEN runs >= 100 THEN 1 ELSE 0 END) AS hundreds
    FROM fact_bating_summary
    GROUP BY player_name, team_innings
)
SELECT 
    DENSE_RANK() OVER (ORDER BY total_runs DESC) AS tournament_rank,
    player_name,
    team,
    innings_batted,
    total_runs,
    total_balls,
    highest_score,
    CASE 
        WHEN total_dismissals = 0 THEN total_runs
        ELSE ROUND(1.0 * total_runs / total_dismissals, 2)
    END AS batting_average,
    CASE 
        WHEN total_balls = 0 THEN 0.0
        ELSE ROUND(100.0 * total_runs / total_balls, 2)
    END AS strike_rate,
    total_fours,
    total_sixes,
    ROUND(100.0 * ((total_fours * 4) + (total_sixes * 6)) / NULLIF(total_runs, 0), 2) AS boundary_runs_pct,
    fifties,
    hundreds
FROM player_batting
ORDER BY total_runs DESC
LIMIT 10;


-- Query 6: Top 10 Highest Individual Match Innings
SELECT 
    b.player_name,
    b.team_innings,
    b.runs,
    b.balls,
    b.strike_rate,
    b.fours,
    b.sixes,
    b.dismissal_status,
    m.ground,
    m.match_date,
    b.match
FROM fact_bating_summary b
JOIN dim_match_summary m ON b.match_id = m.match_id
ORDER BY b.runs DESC, b.strike_rate DESC
LIMIT 10;


-- Query 7: Power Hitters - Best Strike Rates (Minimum 75 Runs Scored)
SELECT 
    player_name,
    team_innings AS team,
    SUM(runs) AS total_runs,
    SUM(balls) AS total_balls,
    ROUND(100.0 * SUM(runs) / SUM(balls), 2) AS tournament_strike_rate,
    SUM(sixes) AS total_sixes,
    ROUND(1.0 * SUM(balls) / NULLIF(SUM(sixes), 0), 1) AS balls_per_six
FROM fact_bating_summary
GROUP BY player_name, team_innings
HAVING SUM(runs) >= 75
ORDER BY tournament_strike_rate DESC
LIMIT 10;


-- Query 8: Batting Order Run Distribution
-- Evaluates which positions (Top order, Middle order, Lower order) generated the most runs.
SELECT 
    CASE 
        WHEN batting_pos IN (1, 2) THEN 'Openers (1-2)'
        WHEN batting_pos = 3 THEN 'Top Order Anchor (3)'
        WHEN batting_pos IN (4, 5) THEN 'Middle Order (4-5)'
        WHEN batting_pos IN (6, 7) THEN 'Finishers (6-7)'
        ELSE 'Tailenders (8-11)'
    END AS batting_segment,
    COUNT(*) AS innings_count,
    SUM(runs) AS segment_runs,
    ROUND(AVG(runs), 1) AS avg_runs_per_innings,
    ROUND(100.0 * SUM(runs) / (SELECT SUM(runs) FROM fact_bating_summary), 2) AS pct_of_tournament_runs,
    ROUND(100.0 * SUM(runs) / NULLIF(SUM(balls), 0), 2) AS segment_strike_rate
FROM fact_bating_summary
GROUP BY batting_segment
ORDER BY segment_runs DESC;


-- ==============================================================================
-- SECTION 5: BOWLING LEADERBOARDS & ADVANCED METRICS
-- ==============================================================================

-- Query 9: Top 10 Wicket Takers of the Tournament
WITH bowler_stats AS (
    SELECT 
        player_name,
        bowling_team,
        COUNT(DISTINCT match_id) AS matches_bowled,
        SUM(overs) AS total_overs,
        SUM(maiden) AS maidens,
        SUM(runs_conceded) AS runs_conceded,
        SUM(wickets) AS total_wickets,
        SUM(dot_balls) AS dot_balls,
        MAX(wickets) AS best_wickets_in_match
    FROM fact_bowling_summary
    GROUP BY player_name, bowling_team
)
SELECT 
    DENSE_RANK() OVER (ORDER BY total_wickets DESC, (1.0 * runs_conceded / NULLIF(total_wickets, 0)) ASC) AS bowling_rank,
    player_name,
    bowling_team,
    matches_bowled,
    total_overs,
    total_wickets,
    runs_conceded,
    CASE 
        WHEN total_wickets = 0 THEN 0.0
        ELSE ROUND(1.0 * runs_conceded / total_wickets, 2)
    END AS bowling_average,
    CASE 
        WHEN total_overs = 0 THEN 0.0
        ELSE ROUND(1.0 * runs_conceded / total_overs, 2)
    END AS economy_rate,
    maidens,
    dot_balls,
    best_wickets_in_match
FROM bowler_stats
ORDER BY total_wickets DESC, bowling_average ASC
LIMIT 10;


-- Query 10: Top 10 Best Bowling Figures in a Single Match
SELECT 
    ROW_NUMBER() OVER (ORDER BY b.wickets DESC, b.runs_conceded ASC) AS rank,
    b.player_name,
    b.bowling_team,
    b.wickets || '/' || b.runs_conceded || ' (' || b.overs || ' ov)' AS bowling_figures,
    b.wickets,
    b.runs_conceded,
    b.overs,
    b.economy,
    b.dot_balls,
    m.ground,
    m.match_date,
    b.match
FROM fact_bowling_summary b
JOIN dim_match_summary m ON b.match_id = m.match_id
ORDER BY b.wickets DESC, b.runs_conceded ASC
LIMIT 10;


-- Query 11: Most Economical Bowlers (Minimum 15 Overs Bowled)
SELECT 
    player_name,
    bowling_team,
    SUM(overs) AS total_overs,
    SUM(runs_conceded) AS total_runs_conceded,
    SUM(wickets) AS total_wickets,
    ROUND(1.0 * SUM(runs_conceded) / SUM(overs), 2) AS tournament_economy,
    SUM(dot_balls) AS total_dots,
    ROUND(100.0 * SUM(dot_balls) / (SUM(overs) * 6), 1) AS dot_ball_pct
FROM fact_bowling_summary
GROUP BY player_name, bowling_team
HAVING SUM(overs) >= 15.0
ORDER BY tournament_economy ASC
LIMIT 10;


-- ==============================================================================
-- SECTION 6: VENUE SCORING PATTERNS & INNINGS TOTALS
-- ==============================================================================

-- Query 12: Venue Scoring Comparison (1st vs 2nd Innings Averages)
WITH innings_totals AS (
    SELECT 
        match_id,
        team_innings,
        innings_order,
        SUM(runs) AS team_score,
        SUM(is_out) AS wickets_down
    FROM fact_bating_summary
    GROUP BY match_id, team_innings, innings_order
)
SELECT 
    m.ground,
    COUNT(DISTINCT m.match_id) AS matches_hosted,
    ROUND(AVG(CASE WHEN it.innings_order = 1 THEN it.team_score END), 1) AS avg_1st_innings_score,
    ROUND(AVG(CASE WHEN it.innings_order = 2 THEN it.team_score END), 1) AS avg_2nd_innings_score,
    MAX(it.team_score) AS highest_venue_score,
    MIN(it.team_score) AS lowest_venue_score
FROM dim_match_summary m
JOIN innings_totals it ON m.match_id = it.match_id
WHERE m.winner NOT IN ('abandoned', 'no result')
GROUP BY m.ground
ORDER BY matches_hosted DESC;


-- Query 13: Top 10 Highest Team Innings Scores
SELECT 
    b.team_innings,
    b.match_id,
    m.ground,
    m.match_date,
    SUM(b.runs) AS total_runs,
    SUM(b.is_out) AS wickets_lost,
    b.innings_order,
    m.winner
FROM fact_bating_summary b
JOIN dim_match_summary m ON b.match_id = m.match_id
GROUP BY b.team_innings, b.match_id, m.ground, m.match_date, b.innings_order, m.winner
ORDER BY total_runs DESC
LIMIT 10;


-- ==============================================================================
-- SECTION 7: SQUAD VALUATION & ALL-ROUNDER MVP RANKINGS
-- ==============================================================================

-- Query 14: Squad Breakdown by Playing Role & Demographics
SELECT 
    COALESCE(NULLIF(playing_role, ''), 'Specialist Batter') AS role,
    COUNT(*) AS player_count,
    SUM(is_captain) AS captains_count,
    SUM(CASE WHEN batting_style LIKE '%Left%' THEN 1 ELSE 0 END) AS left_hand_batters,
    SUM(CASE WHEN batting_style LIKE '%Right%' THEN 1 ELSE 0 END) AS right_hand_batters
FROM dim_players
GROUP BY role
ORDER BY player_count DESC;


-- Query 15: Tournament MVP All-Rounders
-- Identifies players who made significant contributions with BOTH bat and ball.
WITH bat_contrib AS (
    SELECT 
        player_name,
        SUM(runs) AS runs_scored,
        ROUND(100.0 * SUM(runs) / NULLIF(SUM(balls), 0), 2) AS bat_strike_rate
    FROM fact_bating_summary
    GROUP BY player_name
),
bowl_contrib AS (
    SELECT 
        player_name,
        SUM(wickets) AS wickets_taken,
        ROUND(1.0 * SUM(runs_conceded) / NULLIF(SUM(overs), 0), 2) AS bowl_economy
    FROM fact_bowling_summary
    GROUP BY player_name
)
SELECT 
    p.player_name,
    p.team,
    p.playing_role,
    COALESCE(b.runs_scored, 0) AS total_runs,
    COALESCE(b.bat_strike_rate, 0.0) AS bat_sr,
    COALESCE(w.wickets_taken, 0) AS total_wickets,
    COALESCE(w.bowl_economy, 0.0) AS bowling_economy
FROM dim_players p
JOIN bat_contrib b ON p.player_name = b.player_name
JOIN bowl_contrib w ON p.player_name = w.player_name
WHERE COALESCE(b.runs_scored, 0) >= 50 AND COALESCE(w.wickets_taken, 0) >= 5
ORDER BY total_wickets DESC, total_runs DESC;
