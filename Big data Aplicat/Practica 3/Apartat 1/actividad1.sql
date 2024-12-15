CREATE DATABASE soccer;
USE soccer;

-- Crear les taules per colocar les dades

CREATE TABLE soccer.results (
    date DATE,
    home_team STRING,
    away_team STRING,
    home_score INT,
    away_score INT,
    tournament STRING,
    city STRING,
    country STRING,
    neutral BOOLEAN
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY '\t'
TBLPROPERTIES ("skip.header.line.count"="1");


CREATE TABLE soccer.goalscorers (
    date STRING,
    home_team STRING,
    away_team STRING,
    team STRING,
    scorer STRING,
    minute INT,
    own_goal BOOLEAN,
    penalty BOOLEAN
)
ROW FORMAT DELIMITED  
FIELDS TERMINATED BY '\t' 
TBLPROPERTIES ("skip.header.line.count"="1");

-- Carregar les dades a les taules
LOAD DATA LOCAL INPATH "/home/cloudera/Desktop/goalscorers.csv" INTO TABLE soccer.goalscorers;

LOAD DATA LOCAL INPATH "/home/cloudera/Desktop/results.csv" INTO TABLE soccer.results;

-- Consultes
--1
SELECT count(*) FROM soccer.goalscorers WHERE scorer = 'Lionel Messi' AND own_goal = FALSE;

--2
SELECT * FROM soccer.results
WHERE home_team = 'Spain' OR away_team = 'Spain'
ORDER BY date DESC
LIMIT 5;

--3
SELECT SUM
(CASE WHEN home_team = 'Spain' THEN home_score ELSE 0 END + 
CASE WHEN away_team = 'Spain' THEN away_score ELSE 0 END)
FROM soccer.results;

--4
SELECT scorer, count(*) as goals
FROM soccer.goalscorers
WHERE team = 'Spain' AND own_goal = FALSE
GROUP BY scorer
ORDER BY goals DESC
LIMIT 5;

--5
SELECT scorer
FROM soccer.goalscorers
INNER JOIN soccer.results ON goalscorers.date = results.date
WHERE team = 'Spain' AND penalty = TRUE AND tournament = 'UEFA Euro'
GROUP BY scorer
ORDER BY scorer;

--6
SELECT scorer, count(*) as goals
FROM soccer.goalscorers
INNER JOIN soccer.results ON goalscorers.date = results.date
WHERE competition LIKE '%FIFA World Cup%' AND own_goal = FALSE
GROUP BY scorer
ORDER BY goals DESC
LIMIT 5;
