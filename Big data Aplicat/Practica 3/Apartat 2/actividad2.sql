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

-- 2
SELECT title, imdbAverageRating, platform
FROM streaming.movies
WHERE type = 'series'
ORDER BY imdbAverageRating DESC
LIMIT 5;

-- 3
SELECT platform, SUM(imdbNumVotes) AS total_votes
FROM streaming.movies
WHERE genres LIKE '%Science Fiction%' 
   OR genres LIKE '%Sci-Fi%'
   AND type = 'tv'
GROUP BY platform
ORDER BY total_votes DESC;

-- 4
SELECT releaseYear, count(*) as num_movies
FROM streaming.movies
WHERE type = 'movie'
GROUP BY releaseYear
ORDER BY num_movies DESC
LIMIT 5;