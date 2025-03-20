## Apartat 2

```sql
CREATE TABLE bluesky_posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uri VARCHAR(255) NOT NULL,
  cid VARCHAR(255) NOT NULL,
  text TEXT,
  createdAt TIMESTAMP,
  handle VARCHAR(255),
  displayName VARCHAR(255),
  avatar VARCHAR(512),
  UNIQUE KEY unique_post (uri, cid)
);
```

```
bootstrap.servers=localhost:9092
group.id=bluesky-connect-cluster
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=true

offset.storage.topic=connect-offsets
offset.storage.replication.factor=1
config.storage.topic=connect-configs
config.storage.replication.factor=1
status.storage.topic=connect-status
status.storage.replication.factor=1

plugin.path=/usr/share/java,/usr/local/share/kafka/plugins

rest.port=8083
rest.advertised.host.name=localhost
```


```bash
#!/bin/bash

# Carregar variables d'entorn
export BLUESKY_IDENTIFIER="tu-compte@bsky.social"
export BLUESKY_PASSWORD="tu-contrasenya"
export MYSQL_HOST="localhost"
export MYSQL_PORT="3306"
export MYSQL_DATABASE="bluesky_db"
export MYSQL_USER="usuari"
export MYSQL_PASSWORD="contrasenya"

# Iniciar Kafka Connect en mode distribuït
echo "Iniciant Kafka Connect en mode distribuït..."
$KAFKA_HOME/bin/connect-distributed.sh $KAFKA_HOME/config/connect-distributed.properties &

# Esperar que el servei estigui disponible
echo "Esperant que Kafka Connect estigui disponible..."
sleep 10

# Registrar el connector Bluesky Source
echo "Configurant el connector Bluesky Source..."
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @bluesky-source-connector.json

# Registrar el connector MySQL Sink
echo "Configurant el connector MySQL Sink..."
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @mysql-sink-connector.json

echo "Sistema configurat correctament!"
```