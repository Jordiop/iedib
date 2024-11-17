## Apartat 2

```
data = LOAD 'prime.csv' USING PigStorage(',') 
    AS (url:chararray, title:chararray, type:chararray, genres:chararray, 
        releaseYear:int, imdbId:chararray, imdbAverageRating:float, 
        imdbNumVotes:int, availableCountries:chararray);
```

1. nombre total de files de dades excloent la capcalera
```
total_rows = FOREACH (GROUP filtered_data ALL) GENERATE COUNT(filtered_data) AS total;
DUMP total_rows;
```

2. Nombre de series
```
series = FILTER filtered_data BY type == 'Series';
total_series = FOREACH (GROUP series ALL) GENERATE COUNT(series) AS total;
DUMP total_series;
```
3. Mitjana de valoració IMDb per a pel·lícules de gènere únic "comèdia":
```
comedy_movies = FILTER filtered_data BY type == 'Movie' AND genres == 'Comedy';
average_rating_comedy = FOREACH (GROUP comedy_movies ALL) GENERATE AVG(comedy_movies.imdbAverageRating) AS avg_rating;
DUMP average_rating_comedy;
```
4. Nombre de pel·lícules disponibles a Espanya (ES):
```
movies_in_es = FILTER filtered_data BY type == 'Movie' AND availableCountries MATCHES '.*\\bES\\b.*';
total_movies_es = FOREACH (GROUP movies_in_es ALL) GENERATE COUNT(movies_in_es) AS total;
DUMP total_movies_es;
```
5. Total de vots IMDb de sèries del gènere "ciència-ficció":
```
-- Filtrar sèries que contenen "Science Fiction" en els gèneres
sci_fi_series = FILTER filtered_data BY type == 'Series' AND genres MATCHES '.*Science Fiction.*';
total_votes_sci_fi = FOREACH (GROUP sci_fi_series ALL) GENERATE SUM(sci_fi_series.imdbNumVotes) AS total_votes;
DUMP total_votes_sci_fi;
```
6. Valoració mitjana IMDb de pel·lícules i sèries del 2024 (per separat):
```
-- Pel·lícules del 2024
movies_2024 = FILTER filtered_data BY type == 'Movie' AND releaseYear == 2024;
avg_rating_movies_2024 = FOREACH (GROUP movies_2024 ALL) GENERATE AVG(movies_2024.imdbAverageRating) AS avg_rating;

-- Sèries del 2024
series_2024 = FILTER filtered_data BY type == 'Series' AND releaseYear == 2024;
avg_rating_series_2024 = FOREACH (GROUP series_2024 ALL) GENERATE AVG(series_2024.imdbAverageRating) AS avg_rating;

DUMP avg_rating_movies_2024;
DUMP avg_rating_series_2024;
```
7. Els 10 anys amb més pel·lícules (ordenats):
```
-- Filtrar només pel·lícules i agrupar per any
movies_by_year = FILTER filtered_data BY type == 'Movie';
grouped_movies = GROUP movies_by_year BY releaseYear;
count_movies_by_year = FOREACH grouped_movies GENERATE group AS year, COUNT(movies_by_year) AS total_movies;

-- Ordenar i seleccionar els 10 primers
ordered_movies_by_year = ORDER count_movies_by_year BY total_movies DESC;
top_10_years = LIMIT ordered_movies_by_year 10;
DUMP top_10_years;
```
8. Els 5 anys amb millor valoració mitjana IMDb per a sèries de drama:
```
-- Filtrar sèries de gènere "Drama"
drama_series = FILTER filtered_data BY type == 'Series' AND genres MATCHES '.*Drama.*';
grouped_drama_series = GROUP drama_series BY releaseYear;
avg_rating_drama = FOREACH grouped_drama_series GENERATE group AS year, AVG(drama_series.imdbAverageRating) AS avg_rating;

-- Ordenar i seleccionar els 5 primers
ordered_avg_drama = ORDER avg_rating_drama BY avg_rating DESC;
top_5_years_drama = LIMIT ordered_avg_drama 5;
DUMP top_5_years_drama;
```
9. Exportar sèries des del 2020 amb millor valoració:
```
-- Filtrar sèries des del 2020 i ordenar per valoració
series_since_2020 = FILTER filtered_data BY type == 'Series' AND releaseYear >= 2020;
ordered_series = ORDER series_since_2020 BY imdbAverageRating DESC;
top_10_series = LIMIT ordered_series 10;

-- Seleccionar els camps i exportar a un fitxer
export_series = FOREACH top_10_series GENERATE title, releaseYear, imdbAverageRating, imdbNumVotes;
STORE export_series INTO 'top_10_series.csv' USING PigStorage(',');
```
10. Total de vots IMDb de les sèries del fitxer exportat:
```
-- Carregar el fitxer exportat
exported_series = LOAD 'top_10_series.csv' USING PigStorage(',') 
    AS (title:chararray, releaseYear:int, imdbAverageRating:float, imdbNumVotes:int);

-- Calcular el total de vots
total_votes_exported = FOREACH (GROUP exported_series ALL) GENERATE SUM(exported_series.imdbNumVotes) AS total_votes;
DUMP total_votes_exported;
```