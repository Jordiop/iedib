echo "Starting Kafka and Zookeeper"

echo "Starting Zookeeper"
$KAFKA_HOME/bin/zookeeper-server-start.sh config/zookeeper.properties
echo "Starting Kafka"
$KAFKA_HOME/bin/kafka-server-start.sh config/server.properties
echo "Starting Schema Registry"
$KAFKA_HOME/bin/connect-distributed.sh config/connect-distributed.properties

echo "Creating topics from connector"
curl -X POST -H "Content-Type: application/json" --data @bluesky-source.json http://localhost:8083/connectors

echo 'Enable the mysql connector'
curl -X POST -H "Content-Type: application/json" --data @mysql-sink.json http://localhost:8083/connectors

echo "Check the status of the connector"
echo "Status of Bluesky connector"
curl -x GET http://localhost:8083/connectors/bluesky-source/status
echo "Status of Mysql connector"
curl -x GET http://localhost:8083/connectors/mysql-sink/status


echo "Check the status of the connector"
$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bluesky --from-beginning

echo "Pause to wait the post in Bluesky"
read -p "Press enter to continue" 

echo "Check the table of mysql"
mysql -u root -p
use apartat2;
select * from ai;
exit;

