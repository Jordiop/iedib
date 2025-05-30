## BIG DATA APLICAT
### Pràctica 6: Kafka
#### 1. Preparació i configuració per la tasca
Iniciar els serveis necesaris:
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```
```bash
bin/kafka-server-start.sh config/server.properties
```
```bash
bin/connect-distributed.sh config/connect-distributed.properties
```

Crear un topic: 
```bash
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic sensor-data
```


Connector:
```json
{
    "name": "sensor-data-source",
    "config": {
        "connector.class": "FileStreamSource",
        "tasks.max": "1",
        "file": "resultat.csv",
        "topic": "sensor-data",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.storage.StringConverter",
        "mode": "tail"
    }
}
```

Deploy connector:
```bash
curl -X POST -H "Content-Type: application/json" --data @sensor-connector.json http://localhost:8083/connectors
```

#### 2. Execució de la tasca
```bash
echo "23/02/2025,16:07:30,17.7,75.1,1012" >> fitxer.csv
echo "23/02/2025,16:08:30,17.8,74.9,1011" >> fitxer.csv
echo "23/02/2025,16:09:30,18.0,74.6,1011" >> fitxer.csv
echo "23/02/2025,16:10:30,18.2,74.3,1010" >> fitxer.csv
```

Verificar que les dades s'han enviat correctament:
```bash
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic sensor-data --from-beginning
```

Python consumer:

##### IMPORTANT

Després d'un debugging molt profund, posaré a disposició de l'activitat els problemes amb el append i la creació i modificació del arxiu de hdfs. La solució, després de mirar els fòrums, documentació, Stack Overflow, GitHub, ha estat demanar ajuda. Kudos a Carlos (@CharlyMech), amb el qual hem tengut converses sobre aquesta activitat. Al final, entre ell i un poc de Claude 3.7, he aconseguit fer un script que sí que em fa append però que sé que és overkill (buffers, pujar l'arxiu sencer cada vegada, etc)

En el proces, hi ha la cerca i creacio del reparador.sh, que és un cleaner de tot el de hadoop, sospitant que posiblement, el major dels problemes fos més el "cluster" que no tant el script. Inclus així, trob que és necessari donar el context i el perquè de tot.

```python
python hdfs_consumer.py
```

![alt text](images/image-3.png)

Checkear que les dades s'han guardat correctament:
```bash
hdfs dfs -cat /sensor_data/readings.csv
```

![alt text](images/image-4.png)

El log disponible qeu tenc el el server.log. El connect.log no existeix en cap part del sistema, imagin que perque a la server-config, es fica a una carpeta que no existeix

![alt text](images/image-5.png)

```bash
# Del server-properties
# A comma separated list of directories under which to store log files
log.dirs=/tmp/kafka-logs
```

Directori del kafka 
![alt text](images/image-6.png)