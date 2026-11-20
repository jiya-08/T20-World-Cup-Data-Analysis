# T20 Analytics Power BI Dashboard

## 1. Overview
This directory contains the **Power BI Analytics Dashboard (`T20 Analytics Dashboard.pbix`)** built to analyze the ICC Men's T20 World Cup 2022 dataset. It demonstrates business intelligence modeling, star-schema relational design, dynamic DAX measures, and interactive player evaluation.

---

## 2. Dashboard Architecture & Data Model

The data model follows an industry-standard **Star Schema** with bi-directional / one-to-many filtering:

```mermaid
graph TD
    subgraph Dimension Tables
        M[dim_match_summary]
        P[dim_players]
    end

    subgraph Fact Tables
        B[fact_bating_summary]
        W[fact_bowling_summary]
    end

    M -->|1:N (match_id)| B
    M -->|1:N (match_id)| W
    P -->|1:N (player_name)| B
    P -->|1:N (player_name)| W
```

- **Relationships**:
  - `dim_match_summary[match_id]` 1 -> * `fact_bating_summary[match_id]`
  - `dim_match_summary[match_id]` 1 -> * `fact_bowling_summary[match_id]`
  - `dim_players[name]` 1 -> * `fact_bating_summary[batsmanName]`
  - `dim_players[name]` 1 -> * `fact_bowling_summary[bowlerName]`

---

## 3. Key DAX Measures & Metrics

The dashboard features customized DAX measures across several analysis dimensions:

### Batting Measures
- **Total Runs**:
  ```dax
  Total Runs = SUM(fact_bating_summary[runs])
  ```
- **Total Balls Faced**:
  ```dax
  Total Balls = SUM(fact_bating_summary[balls])
  ```
- **Batting Average**:
  ```dax
  Batting Average = 
  DIVIDE(
      SUM(fact_bating_summary[runs]),
      CALCULATE(COUNTROWS(fact_bating_summary), fact_bating_summary[out/not_out] = "out"),
      0
  )
  ```
- **Batting Strike Rate**:
  ```dax
  Batting Strike Rate = 
  DIVIDE(
      SUM(fact_bating_summary[runs]) * 100,
      SUM(fact_bating_summary[balls]),
      0
  )
  ```
- **Boundary Runs %**:
  ```dax
  Boundary % = 
  DIVIDE(
      (SUM(fact_bating_summary[4s]) * 4) + (SUM(fact_bating_summary[6s]) * 6),
      SUM(fact_bating_summary[runs]),
      0
  )
  ```

### Bowling Measures
- **Total Wickets**:
  ```dax
  Total Wickets = SUM(fact_bowling_summary[wickets])
  ```
- **Bowling Economy**:
  ```dax
  Bowling Economy = 
  DIVIDE(
      SUM(fact_bowling_summary[runs]),
      SUM(fact_bowling_summary[overs]),
      0
  )
  ```
- **Dot Ball %**:
  ```dax
  Dot Ball % = 
  DIVIDE(
      SUM(fact_bowling_summary[0s]),
      SUM(fact_bowling_summary[overs]) * 6,
      0
  )
  ```

---

## 4. Dashboard Views & Visuals

1. **Tournament Overview**:
   - Total matches, total runs, total wickets, boundary percentage KPI cards.
   - Stage-by-stage tournament flow (First Round Qualifiers vs Super 12 vs Semi-Finals & Final).
2. **Best XI / Squad Selection**:
   - Criteria-based player filtering: Openers (high SR & average in powerplay), Middle Order, Anchors, Finishers, Bowling Allrounders, and Death Bowlers.
3. **Team Performance Matrix**:
   - Win % by match state (Defending vs Chasing), venue-wise win conversion.
4. **Player Profiling & Head-to-Head**:
   - Detailed radar/bar metrics comparing strike rates vs bowling economy.

---

## 5. How to View the Dashboard
1. Download or clone this repository.
2. Ensure [Microsoft Power BI Desktop](https://powerbi.microsoft.com/desktop/) is installed.
3. Open `dashboards/T20 Analytics Dashboard.pbix`.
4. Refresh data sources if connected to local `data/processed/` CSV files.
