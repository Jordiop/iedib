
# Practica 4

## Creacio de les taules

El primer que he fet ha estat investigar un poc els dos fitxers CSV per saber que havia de crear per a que les dades s'importessin correctament. 

```sql
CREATE EXTERNAL TABLE raw_titles (
    index INT,
    id STRING,
    title STRING,
    type STRING,
    release_year STRING,
    age_certification STRING,
    runtime STRING,
    genres STRING,
    production_countries STRING,
    seasons DOUBLE,
    imdb_id STRING,
    imdb_score STRING,
    imdb_votes STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE raw_credits (
    index INT,
    person_id STRING,
    id STRING,
    name STRING,
    character STRING,
    `role` STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');
```
##### Vaig cometre un error i vaig asignar tots els numeros com strings, aixi que he hagut de parsejar strings com floats

## Importar les dades
Per importar les dades he fet servir hdfs dfs -put per a pujar els fitxers a HDFS i despres he fet servir la seguent comanda per a importar les dades a les taules:
`hadoop fs -put /home/cloudera/Desktop/raw_titles.csv /user/cloudera/`
`hadoop fs -put /home/cloudera/Desktop/raw_credits.csv /user/cloudera/`

```sql
LOAD DATA INPATH '/user/cloudera/raw_titles.csv' 
OVERWRITE INTO TABLE raw_titles;

LOAD DATA INPATH '/user/cloudera/raw_credits.csv'
OVERWRITE INTO TABLE raw_credits;
```

I per finalitzar la importacio invalido les taules per a que es refresquin les dades:
```sql
INVALIDATE METADATA raw_titles;
INVALIDATE METADATA raw_credits;
```

Despres simplement he fet un SELECT * per a comprovar que les dades s'havien importat correctament.

## Consultes

## Apartat 1: Movies / TV Shows

### 1. Llistat dels 10 programes de TV amb més d'una temporada que tenen millor valoració, ordenats per valoració en ordre decreixent.
```sql
SELECT 
    title,
    seasons,
    imdb_score
FROM raw_titles
WHERE type = 'SHOW' 
    AND seasons > 1
    AND imdb_score != ''
ORDER BY CAST(imdb_score AS FLOAT) DESC
LIMIT 10;
```
![alt text](image.png)

### 2. Llistat dels 10 anys en què els seus programes de TV (segons l'any de llançament) han tengut més vots, ordenats per nombre de vots, en ordre decreixent.
```sql
Vaig cometre un error i vaig possar tot els numeros com string, aixi que com consequencia he hagut de parsear strings com floats :)
SELECT 
    release_year,
    SUM(CAST(imdb_votes AS FLOAT)) as total_votes
FROM raw_titles
WHERE type = 'SHOW' 
    AND imdb_votes != ''
GROUP BY release_year
ORDER BY total_votes DESC
LIMIT 10;
```
![alt text](image-1.png)

### 3. Llistat dels 10 directors amb més pel·lícules, ordenats per nombre de pel·lícules en ordre decreixent.
```sql
SELECT 
    c.name,
    COUNT(*) as movie_count
FROM raw_credits c
JOIN raw_titles t ON c.id = t.id
WHERE c.`role` = 'DIRECTOR'
    AND t.type = 'MOVIE'
GROUP BY c.name
ORDER BY movie_count DESC
LIMIT 10;
```
![alt text](image-2.png)

### 4. Llistat dels 10 actors amb millor valoració mitjana de les seves pel·lícules, ordentats per valoració mitjana en ordre decreixent.

En aquesta consulta he hagut de fer servir un HAVING COUNT(*) >= 5 per a que nomes es mostrin els actors que han participat en 5 o mes pel·lícules. Igualment he fet una altra consulta sense el HAVING COUNT(*) >= 5 per a comparar els resultats.

```sql
SELECT 
    c.name,
    AVG(CAST(t.imdb_score AS FLOAT)) as avg_rating,
    COUNT(*) as movie_count
FROM raw_credits c
JOIN raw_titles t ON c.id = t.id
WHERE c.`role` = 'ACTOR'
    AND t.type = 'MOVIE'
    AND t.imdb_score != ''
GROUP BY c.name
HAVING COUNT(*) >= 5 
ORDER BY avg_rating DESC
LIMIT 10;
```
![alt text](image-3.png)

```sql
SELECT 
    c.name,
    AVG(CAST(t.imdb_score AS FLOAT)) as avg_rating,
    COUNT(*) as movie_count
FROM raw_credits c
JOIN raw_titles t ON c.id = t.id
WHERE c.`role` = 'ACTOR'
    AND t.type = 'MOVIE'
    AND t.imdb_score != ''
GROUP BY c.name 
ORDER BY avg_rating DESC
LIMIT 10;
```
![alt text](image-4.png)


## Apartat 2: Biblioteques 

Tenim les següents dades sobre llibres i biblioteques:
```json
ID 	Info_Llibre 	Temes 	Exemplars_Biblioteca
1 	{"Títol": "1984", "Autor": "George Orwell", "Any": 1949} 	["Ficció", "Distopia", "Societat"] 	{"Centre": 5, "Llevant": 2}
2 	{"Títol": "Sapiens", "Autor": "Yuval Noah Harari", "Any": 2011} 	["Assaig", "Història", "Antropologia", "Societat"] 	{"Llevant": 4, "Ponent": 3}
3 	{"Títol": "Dune", "Autor": "Frank Herbert", "Any": 1965} 	["Ficció", "Aventura", "Ciència-ficció"] 	{"Centre": 7, "Ponent": 2}
4 	{"Títol": "El Senyor dels anells", "Autor": "J.R.R. Tolkien", "Any": 1954} 	["Ficció", "Aventura", "Fantasia"] 	{"Centre": 8, "Llevant": 3}
5 	{"Títol": "Història de dues ciutats", "Autor": "Charles Dickens", "Any": 1859} 	["Ficció", "Història", "Drama"] 	{"Llevant": 2}
```

Cada llibre té una informació (títol, autor i any de publicació) un llistat de temes i una informació sobre els exemplars disponibles a cada una de les tres biblioteques de la ciutat (Centre, Llevant i Ponent).

Crea una taula en el magatzem de dades de Hive, emprant els tipus complexos STRUCT, ARRAY i MAP. Carrega-hi les dades executant sentències INSERT. Executa les següents consultes en Hive (amb HiveQL) i Impala (amb SQL):

```sql
CREATE TABLE llibres (
  id INT,
  info_llibre STRUCT<titol:STRING, autor:STRING, any:INT>,
  temes ARRAY<STRING>,
  exemplars_biblioteca MAP<STRING,INT>
)
STORED AS PARQUET;
```

Insertam les dades donades adalt
```sql
-- Primer llibre
INSERT INTO llibres
SELECT 1, 
       NAMED_STRUCT('titol','1984','autor','George Orwell','any',1949),
       ARRAY('Ficció','Distopia','Societat'),
       MAP('Centre',5,'Llevant',2)
FROM (SELECT 1) dummy;

-- Segon llibre
INSERT INTO llibres
SELECT 2,
       NAMED_STRUCT('titol','Sapiens','autor','Yuval Noah Harari','any',2011),
       ARRAY('Assaig','Història','Antropologia','Societat'),
       MAP('Llevant',4,'Ponent',3)
FROM (SELECT 1) dummy;

-- Tercer llibre
INSERT INTO llibres
SELECT 3,
       NAMED_STRUCT('titol','Dune','autor','Frank Herbert','any',1965),
       ARRAY('Ficció','Aventura','Ciència-ficció'),
       MAP('Centre',7,'Ponent',2)
FROM (SELECT 1) dummy;

-- Quart llibre
INSERT INTO llibres
SELECT 4,
       NAMED_STRUCT('titol','El Senyor dels anells','autor','J.R.R. Tolkien','any',1954),
       ARRAY('Ficció','Aventura','Fantasia'),
       MAP('Centre',8,'Llevant',3)
FROM (SELECT 1) dummy;

-- Cinquè llibre
INSERT INTO llibres
SELECT 5,
       NAMED_STRUCT('titol','Història de dues ciutats','autor','Charles Dickens','any',1859),
       ARRAY('Ficció','Història','Drama'),
       MAP('Llevant',2)
FROM (SELECT 1) dummy;
```

### 1. Recupera el títol de tots els llibres publicats al segle XX.
#### Hive
```sql
SELECT info_llibre.titol
FROM llibres
WHERE info_llibre.any >= 1900 AND info_llibre.any < 2000;
```
![alt text](image-5.png)
#### Impala
```sql
SELECT info_llibre.titol
FROM llibres
WHERE info_llibre.any BETWEEN 1900 AND 1999;
```
![alt text](image-9.png)

### 2. Recupera el títol dels llibres del tema "Història".
#### Hive
```sql
SELECT info_llibre.titol
FROM llibres
WHERE array_contains(temes, 'Història');
```
![alt text](image-6.png)
#### Impala
```sql
SELECT info_llibre.titol
FROM llibres
WHERE temes[0] = 'Història' 
   OR temes[1] = 'Història'
   OR temes[2] = 'Història'
   OR temes[3] = 'Història';
```

### 3. Recupera el total d'exemplars disponibles a la biblioteca de Llevant.
#### Hive
```sql
SELECT SUM(exemplars_biblioteca['Llevant']) as total_llevant
FROM llibres;
```
![alt text](image-7.png)
#### Impala
```sql
SELECT SUM(exemplars_biblioteca['Llevant']) as total_llevant
FROM llibres;
```

### 4. Recupera el títol dels llibres de Ficció disponibles a la biblioteca del Centre.
#### Hive
```sql
SELECT info_llibre.titol
FROM llibres
WHERE array_contains(temes, 'Ficció')
AND exemplars_biblioteca['Centre'] > 0;
```
![alt text](image-8.png)
#### Impala
```sql
SELECT info_llibre.titol
FROM llibres
WHERE EXISTS (
  SELECT 1 
  FROM UNNEST(temes) t 
  WHERE t = 'Ficció'
)
AND exemplars_biblioteca['Centre'] > 0;
```


Les principals diferències entre HiveQL i Impala SQL en aquestes consultes són:
1. La forma de treballar amb arrays: HiveQL utilitza la funció `array_contains()` mentre que Impala utilitza `UNNEST` amb `EXISTS`
2. La sintaxi per intervals: tot i que ambdós accepten BETWEEN, en HiveQL és més comú veure AND
3. La resta de funcionalitats (accés a structs amb punt, accés a maps amb claus, agregacions) funcionen igual en ambdós motors