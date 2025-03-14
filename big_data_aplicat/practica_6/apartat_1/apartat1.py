from kafka import KafkaConsumer
from hdfs import InsecureClient
import time
import datetime
import io

# globals
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'sensor-data'
HDFS_URL = 'http://localhost:9870'  
HDFS_USER = 'hdfs'
HDFS_OUTPUT_FILE = '/sensor_data/readings.csv'

def convert_to_timestamp(date_str, time_str):
    """Convert date and time strings to Unix timestamp"""
    date_format = "%d/%m/%Y %H:%M:%S"
    datetime_str = f"{date_str} {time_str}"
    dt_object = datetime.datetime.strptime(datetime_str, date_format)
    return int(dt_object.timestamp())

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='sensor-data-consumer'
    )
    
    hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)
    buffer = io.StringIO()
    record_count = 0
    
    print(f"Conectat al tema {KAFKA_TOPIC}. Esperant missatges...")
    
    try:
        if not hdfs_client.status(HDFS_OUTPUT_FILE, strict=False):
            hdfs_client.write(HDFS_OUTPUT_FILE, data='', overwrite=True)
            print(f"Creat fitxer nou a HDFS: {HDFS_OUTPUT_FILE}")
        
        for message in consumer:
            msg_value = message.value.decode('utf-8')
            parts = msg_value.strip().split(',')
            
            if len(parts) == 5:
                date_str, time_str, temp_str, humidity_str, pressure_str = parts
                
                unix_timestamp = convert_to_timestamp(date_str, time_str)
                temperature = float(temp_str)
                humidity = float(humidity_str)
                pressure = int(float(pressure_str))
                
                new_line = f"{unix_timestamp};{temperature};{pressure};{humidity}\n"
                buffer.write(new_line)
                record_count += 1
                
                print(f"Processat registre: {new_line.strip()}")
                
                if record_count >= 10:
                    buffer.seek(0)
                    hdfs_client.write(HDFS_OUTPUT_FILE, data=buffer.getvalue(), append=True)
                    print(f"Escrits {record_count} registres a HDFS")
                    buffer = io.StringIO()
                    record_count = 0
            else:
                print(f"Format incorrecte del missatge: {msg_value}")
    
    except KeyboardInterrupt:
        print("Aturant el consumidor...")
    finally:
        if record_count > 0:
            buffer.seek(0)
            hdfs_client.write(HDFS_OUTPUT_FILE, data=buffer.getvalue(), append=True)
            print(f"Escrits {record_count} registres a HDFS")
        
        consumer.close()
        print("Consumidor tancat correctament")

if __name__ == "__main__":
    main()