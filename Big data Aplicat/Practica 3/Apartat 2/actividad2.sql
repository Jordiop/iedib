CREATE DATABASE streaming;
USE streaming;

-- Crear les taules per colocar les dades

CREATE TABLE streaming.movies (
    title STRING,
    type STRING,
    genres STRING,
    releaseYear FLOAT,
    imdbId STRING,
    imdbAverageRating FLOAT,
    imdbNumVotes INT,
    availableCountries STRING
)
PARTITIONED BY(platform STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Carregar les dades a les taules

-- 1
SELECT platform, count(*) as num_movies
FROM streaming.movies
WHERE type = 'movie'
GROUP BY platform
ORDER BY num_movies DESC
LIMIT 1;
-- amazon	59244	

-- 2
SELECT title, imdbAverageRating, platform
FROM streaming.movies
WHERE type = 'tv'
ORDER BY imdbAverageRating DESC
LIMIT 5;
/* Benjamin Cello	9.5	amazon	
Breaking Bad	9.5	netflix	
Band of Brothers	9.3999996185302734	netflix	
Getting Dirty in Japan	9.3999996185302734	amazon	
Life After	9.3999996185302734	amazon	 */

-- 3
SELECT platform, SUM(imdbNumVotes) AS total_votes
FROM streaming.movies
WHERE genres LIKE '%Science Fiction%' 
   OR genres LIKE '%Sci-Fi%'
   AND type = 'tv'
GROUP BY platform
ORDER BY total_votes DESC;
/* amazon	3403767	
apple	2375367	
netflix	1665835	
hulu	1551810	
hbo	745275	 */

-- 4
SELECT releaseYear, count(*) as num_movies
FROM streaming.movies
WHERE type = 'movie'
GROUP BY releaseYear
ORDER BY num_movies DESC
LIMIT 5;
/* 2022	6068	
2019	6045	
2018	5711	
2021	5522	
2017	5209	 */
