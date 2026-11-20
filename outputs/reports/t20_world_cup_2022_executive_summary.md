# Executive Analytics Report: ICC Men's T20 World Cup 2022

**Project:** T20 World Cup Data Analysis & Strategic Insights  
**Domain:** Sports Analytics / Business Intelligence  
**Role:** Senior Data Analyst & Portfolio Project  
**Date:** November 2022  

---

## 1. Executive Summary

The ICC Men's T20 World Cup 2022 hosted in Australia presented a compelling environment for data analytics, characterized by larger Australian boundary dimensions, distinct pitch behaviors across 7 host cities, and high-stakes match scenarios.

This study analyzes **45 scheduled fixtures** (41 completed, 3 abandoned due to rain, 1 no-result), evaluating **11,169 runs scored**, **515 wickets taken**, **909 fours**, and **331 sixes** across **16 participating national teams** and **213 unique players**.

### Headline Tournament KPIs:
| Metric | Value | Analytical Interpretation |
| :--- | :--- | :--- |
| **Total Matches Scheduled** | **45** | 12 Round 1 Qualifiers + 30 Super 12s + 2 Semi-Finals + 1 Final |
| **Completed Matches** | **41** | 91.1% completion rate; rain impacted group fixtures in Melbourne |
| **Tournament Champion** | **England** | Defeated Pakistan by 5 wickets in the Final at the MCG |
| **Total Runs Scored** | **11,169** | Average first innings score: ~153.2 runs |
| **Total Wickets Taken** | **515** | 6.28 wickets per innings across the tournament |
| **Boundary Run Percentage** | **50.34%** | Over half of all runs scored originated from boundaries (4s & 6s) |
| **Total Dot Balls** | **3,822** | 40.1% of all legal deliveries bowled produced zero runs |
| **Defending Win Rate** | **56.10%** | 23 wins batting first vs 18 wins chasing |

---

## 2. Strategic Tournament Insights

### Insight 1: Defending Advantage (Batting First vs Chasing)
Contrary to conventional T20 franchise tournaments (where chasing often has a slight advantage due to dew and par-score pacing), the 2022 World Cup strongly favored **teams batting first**:
- **56.1% of completed matches (23 of 41)** were won by the team batting first.
- **Venue Variations**:
  - **Adelaide Oval**: 71.4% won defending (5 of 7). High-pressure venue where posting 160+ created insurmountable chase pressure.
  - **Sydney Cricket Ground (SCG)**: 71.4% won defending (5 of 7). Highest average 1st innings score (175.4 runs).
  - **Perth Stadium**: Faster, bouncier pitch where chasing teams won 60% of matches due to late-innings pitch stabilization.

### Insight 2: The Golden Bat - Anchor vs Power-Hitter Divergence
The tournament demonstrated two successful batting archetypes:
1. **The Elite Anchor - Virat Kohli (India)**:
   - **296 Runs** across 6 innings at an astronomical **average of 98.67** and **strike rate of 136.41**.
   - Low dismissal rate (dismissed only 3 times in 6 innings). Provided stabilization allowing middle order to attack.
2. **The 360-Degree Power Accelerator - Suryakumar Yadav (India)**:
   - **239 Runs** at an astounding **strike rate of 189.68** and **average of 59.75**.
   - Scored at nearly 11.4 runs per over without sacrificing wicket preservation.
3. **Leading Run Scorers Summary**:
   - Max O'Dowd (Netherlands): 242 runs (anchored Netherlands' successful campaign through Round 1 and Super 12).
   - Jos Buttler (England): 225 runs (led champion England from the front, including 80* in semi-final).
   - Kusal Mendis (Sri Lanka): 223 runs (dominated Round 1 qualifiers).

### Insight 3: Bowler Archetypes - Pace & Wrist Spin Dominance
Wickets were heavily driven by wrist spinners and left-arm seamers utilizing reverse swing and variations:
1. **Leading Wicket Takers**:
   - **Wanindu Hasaranga (Sri Lanka)**: 15 wickets (Economy 6.42, 74 dot balls). Led the tournament via deceptive googly variations.
   - **Sam Curran (England - Player of the Tournament & Player of the Final)**: 13 wickets (Economy 6.53, Average 11.38). Delivered best individual match figures: **5/10 against Afghanistan** at Perth.
   - **Bas de Leede (Netherlands)**: 13 wickets (crucial breakthroughs in middle and death overs).
   - **Blessing Muzarabani (Zimbabwe)**: 12 wickets (utilized extra bounce on Australian surfaces).
   - **Anrich Nortje (South Africa)**: 11 wickets at an elite **economy of 5.37** and average of **8.55**.

### Insight 4: The Currency of Dot Balls
Teams that suppressed boundary leakage while maximizing dot balls consistently advanced:
- 3,822 dot balls were bowled across the tournament (40.1% dot-ball ratio).
- Bowlers with dot ball ratios exceeding 50% (Anrich Nortje, Shaheen Afridi, Bhuvneshwar Kumar) conceded under 6.00 runs per over.

---

## 3. Recommended Best Tournament XI (Data-Driven Selection)

Based on quantitative metrics (Runs, Wickets, Strike Rate, Economy, and Impact under Pressure):

| Pos | Player Name | Team | Role | Primary Metric |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Alex Hales** | England | Right-Hand Opener | 212 Runs, SR 147.2, Semi-Final 86* |
| **2** | **Jos Buttler (c/wk)** | England | Opener / Captain / WK | 225 Runs, SR 144.2, 12 Dismissals |
| **3** | **Virat Kohli** | India | Top-Order Anchor | 296 Runs (Top Scorer), Avg 98.7 |
| **4** | **Suryakumar Yadav** | India | Middle-Order Accelerator | 239 Runs, SR 189.7 (Tournament Best) |
| **5** | **Glenn Phillips** | New Zealand | Middle-Order Finisher | 201 Runs, SR 158.3, Century (104) |
| **6** | **Sikandar Raza** | Zimbabwe | Batting All-Rounder | 219 Runs, 10 Wickets, Match-winning spells |
| **7** | **Shadab Khan** | Pakistan | Bowling All-Rounder (Leg-spin)| 11 Wickets (Econ 6.34), 98 Runs (SR 168.9) |
| **8** | **Sam Curran** | England | Left-Arm Pacer / Death Specialist | 13 Wickets, Avg 11.4, Player of Tournament |
| **9** | **Wanindu Hasaranga** | Sri Lanka | Specialist Wrist Spinner | 15 Wickets (Top Wicket-Taker), Econ 6.42 |
| **10**| **Shaheen Shah Afridi**| Pakistan | Left-Arm Opening Pacer | 11 Wickets, Powerplay strike force |
| **11**| **Anrich Nortje** | South Africa | Express Pacer | 11 Wickets, Econ 5.37, Avg 8.55 |

---

## 4. Technical Artifacts Delivered
1. **Cleaned Datasets (`data/processed/`)**: 5 relational CSV files with clean schema and typed columns.
2. **Python Modular Codebase (`src/`)**: Automated processing, cleaning, statistical engine, and chart generation.
3. **SQL Analytics Engine (`sql/`)**: 15+ comprehensive queries covering window functions, CTEs, and KPI aggregations.
4. **Visual Analytics Suite (`outputs/charts/`)**: 10 high-resolution publication-grade PNG visualizations.
5. **Interactive Power BI Dashboard (`dashboards/`)**: Complete `.pbix` model with star schema and DAX measures.
