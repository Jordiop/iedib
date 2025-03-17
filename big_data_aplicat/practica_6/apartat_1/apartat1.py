from kafka import KafkaConsumer
import datetime
import subprocess
import tempfile
import os

# Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'sensor-data'
HDFS_OUTPUT_PATH = '/sensor_data.csv'

def convert_to_timestamp(date_str, time_str):
    date_format = "%d/%m/%Y %H:%M:%S"
    datetime_str = f"{date_str} {time_str}"
    dt_object = datetime.datetime.strptime(datetime_str, date_format)
    return int(dt_object.timestamp())

def ensure_hdfs_path():
    dir_path = os.path.dirname(HDFS_OUTPUT_PATH)
    subprocess.run(['hdfs', 'dfs', '-mkdir', '-p', dir_path], check=False)
    
    check_cmd = subprocess.run(['hdfs', 'dfs', '-test', '-e', HDFS_OUTPUT_PATH], check=False)
    if check_cmd.returncode != 0:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        subprocess.run(['hdfs', 'dfs', '-put', tmp.name, HDFS_OUTPUT_PATH], check=False)
        os.unlink(tmp.name)
        print(f"Created HDFS file: {HDFS_OUTPUT_PATH}")

def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        group_id='sensor-data-consumer'
    )
    
    ensure_hdfs_path()
    
    print(f"Connected to topic {KAFKA_TOPIC}. Waiting for messages...")
    
    try:
        for message in consumer:
            msg_value = message.value.decode('utf-8')
            parts = msg_value.strip().split(',')
            
            if len(parts) == 5:
                date_str, time_str, temp_str, humidity_str, pressure_str = parts
                
                unix_timestamp = convert_to_timestamp(date_str, time_str)
                temperature = float(temp_str)
                humidity = float(humidity_str)
                pressure = int(float(pressure_str))
                
                tmp = tempfile.NamedTemporaryFile(delete=False, mode='w')
                new_line = f"{unix_timestamp};{temperature};{pressure};{humidity}\n"
                tmp.write(new_line)
                tmp.close()
                
                subprocess.run([
                    'hdfs', 'dfs', '-appendToFile', tmp.name, HDFS_OUTPUT_PATH
                ], check=False)
                
                os.unlink(tmp.name)
                
                print(f"Processed and appended: {new_line.strip()}")
            else:
                print(f"Incorrect message format: {msg_value}")
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
        print("Consumer closed correctly")

if __name__ == "__main__":
    main()