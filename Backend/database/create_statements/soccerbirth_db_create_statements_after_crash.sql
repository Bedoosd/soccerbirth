-- Pc is gecrashed op dinsdag 02/06
-- databank back up is steeds geupdate naar git
-- creatie ddl's spijtig genoeg niet.
-- 04-06: met samenraapsels die wel in lokale git stonden, wat samengevoegd
-- indien laptop na herstelling niet volledig gecleaned is, kan ik volwaardig .sql script opladen.


-- soccerbirth_dwh.fact_euro_stats
create table soccerbirth_dwh.fact_euro_stats as (
WITH all_teams AS (
    SELECT year, home_team AS team, round, match_date FROM soccerbirth_staging.euro_matches
   -- where year = 2024
    UNION ALL
    SELECT year, away_team AS team, round, match_date FROM soccerbirth_staging.euro_matches
  --  where year = 2024
),
final_match AS (
    SELECT 
        year,
        winner,
        CASE 
            WHEN winner = home_team THEN away_team
            WHEN winner = away_team THEN home_team
        END AS runner_up
    FROM soccerbirth_staging.euro_matches
    WHERE round = 'FINAL'
),
last_match_per_team AS (
    SELECT year, team, MAX(match_date) AS last_match_date
    FROM all_teams
    GROUP BY year, team
),
round_ranked AS (
    SELECT 
        at.year, 
        at.team, 
        at.round,
        CASE 
            WHEN at.team = fm.winner THEN 6  -- 1ste plaats
            WHEN at.team = fm.runner_up THEN 5  -- 2de plaats
            WHEN at.round = 'SEMIFINAL' THEN 4
            WHEN at.round = 'QUARTER_FINALS' THEN 3
            WHEN at.round = 'ROUND_OF_16' THEN 2
            WHEN at.round = 'GROUP_STANDINGS' THEN 1
            ELSE 0
        END AS round_rank
    FROM all_teams at
    LEFT JOIN final_match fm ON at.year = fm.year
),
team_goals AS (
    SELECT 
        year,
        home_team AS team,
        SUM(home_score_total) AS goals
    FROM soccerbirth_staging.euro_matches
    GROUP BY year, home_team
    UNION ALL
    SELECT 
        year,
        away_team AS team,
        SUM(away_score_total) AS goals
    FROM soccerbirth_staging.euro_matches
    GROUP BY year, away_team
),
goals_per_team AS (
    SELECT year, team, SUM(goals) AS total_goals
    FROM team_goals
    GROUP BY year, team
)
SELECT 
    rr.year, 
    dc.country_id as country_dim_id,
    MAX(rr.round_rank) AS round_codes_dim_id,
    gp.total_goals,
    lmp.last_match_date
FROM round_ranked rr
LEFT JOIN goals_per_team gp ON rr.year = gp.year AND rr.team = gp.team
LEFT JOIN last_match_per_team lmp ON rr.year = lmp.year AND rr.team = lmp.team
LEFT JOIN soccerbirth_dwh.dim_country dc on rr.team = dc.country_name 
GROUP BY rr.year, dc.country_id, gp.total_goals, lmp.last_match_date
ORDER BY rr.year, round_codes_dim_id desc
);

-- soccerbirth_dwh.fact_world_cup_stats
create table soccerbirth_dwh.fact_world_cup_stats as (
WITH all_teams AS (
    SELECT year, home_team AS team, host, round, match_date FROM soccerbirth_staging.world_cup_matches
   -- where year = 2024
    UNION ALL
    SELECT year, away_team AS team, host, round, match_date FROM soccerbirth_staging.world_cup_matches
  --  where year = 2024
),
final_match AS (
    SELECT 
        year,
        winner,
        CASE 
            WHEN winner = home_team THEN away_team
            WHEN winner = away_team THEN home_team
        END AS runner_up
    FROM soccerbirth_staging.world_cup_matches
    WHERE round = 'FINAL'
),
last_match_per_team AS (
    SELECT year, team, MAX(match_date) AS last_match_date
    FROM all_teams
    GROUP BY year, team
),
round_ranked AS (
    SELECT 
        at.year, 
        at.team, 
        at.round,
        CASE 
            WHEN at.team = fm.winner THEN 6  -- 1ste plaats
            WHEN at.team = fm.runner_up THEN 5  -- 2de plaats
            WHEN at.round = 'SEMIFINAL' THEN 4
            WHEN at.round = 'QUARTER_FINALS' THEN 3
            WHEN at.round = 'ROUND_OF_16' THEN 2
            WHEN at.round = 'GROUP_STANDINGS' THEN 1
            ELSE 0
        END AS round_rank
    FROM all_teams at
    LEFT JOIN final_match fm ON at.year = fm.year
),
team_goals AS (
    SELECT 
        year,
        home_team AS team,
        SUM(home_score_total) AS goals
    FROM soccerbirth_staging.world_cup_matches
    GROUP BY year, home_team
    UNION ALL
    SELECT 
        year,
        away_team AS team,
        SUM(away_score_total) AS goals
    FROM soccerbirth_staging.world_cup_matches
    GROUP BY year, away_team
),
goals_per_team AS (
    SELECT year, team, SUM(goals) AS total_goals
    FROM team_goals
    GROUP BY year, team
)
SELECT 
    rr.year, 
    rr.host,
    dc.country_id as country_dim_id,
    MAX(rr.round_rank) AS round_codes_dim_id,
    gp.total_goals,
    lmp.last_match_date
FROM round_ranked rr
LEFT JOIN goals_per_team gp ON rr.year = gp.year AND rr.team = gp.team
LEFT JOIN last_match_per_team lmp ON rr.year = lmp.year AND rr.team = lmp.team
LEFT JOIN soccerbirth_dwh.dim_country dc on rr.team = dc.country_name 
GROUP BY rr.year, rr.host, dc.country_id, gp.total_goals, lmp.last_match_date
ORDER BY rr.year, round_codes_dim_id desc
);

CREATE VIEW soccerbirth_dataproducts.dp_world_cup_stats_round AS
 SELECT fwcs.year,
    fwcs.host,
    dc.country_name,
    dc.iso_alpha3 AS iso_code,
    drc.description AS round_descr,
    drc.descr_short AS round_descr_short,
    fwcs.last_match_date AS date_match
   FROM ((soccerbirth_dwh.fact_world_cup_stats fwcs
     LEFT JOIN soccerbirth_dwh.dim_country dc ON ((fwcs.country_dim_id = dc.country_id)))
     LEFT JOIN soccerbirth_dwh.dim_round_codes drc ON ((fwcs.round_codes_dim_id = drc.dim_id)));
     
CREATE VIEW soccerbirth_dataproducts.dp_euro_stats_round AS
 SELECT fes.year,
    ehc.gastland AS host,
    dc.country_name,
    dc.iso_alpha3 AS iso_code,
    drc.description AS round_descr,
    drc.descr_short AS round_descr_short,
    fes.last_match_date AS date_match
   FROM (((soccerbirth_dwh.fact_euro_stats fes
     LEFT JOIN soccerbirth_dwh.dim_country dc ON ((fes.country_dim_id = dc.country_id)))
     LEFT JOIN soccerbirth_dwh.dim_round_codes drc ON ((fes.round_codes_dim_id = drc.dim_id)))
     LEFT JOIN soccerbirth_staging.euro_home_countries ehc ON ((fes.year = ehc.jaar)));