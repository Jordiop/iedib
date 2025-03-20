import json
from datetime import datetime
from kafka import KafkaConsumer
from hdfs import InsecureClient

HDFS_FILE = '/user/hadoop/kafka/section1.csv'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S' 
hdfs_client = InsecureClient('http://hadoopmaster:9870', user='hadoop')

if not hdfs_client.status(HDFS_FILE, strict=False):
	with hdfs_client.write(HDFS_FILE, overwrite=True) as writer:
		writer.write(b'') 

consumer = KafkaConsumer('sensor-data',
	bootstrap_servers=['localhost:9092'],
	auto_offset_reset='earliest',
	enable_auto_commit=True,
	group_id='sensor-data-consumer',
	value_deserializer=lambda x: json.loads(x.decode('utf-8'))  
)

for message in consumer:
    msg = message.value
    print('Message: ', msg)
    payload = msg.get('payload', '')
    
    if isinstance(payload, str):
        values = payload.split(',')
        if len(values) >= 5:  
            datetime_str = f'{values[0]} {values[1]}'
            datatime_value = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            try:
                datatime_value = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime('%d/%m/%Y %H:%M:%S')
            except ValueError:
                print(f'Error: Invalid datetime format: {datetime_str}\nLeaving datetime as current time: {datatime_value}')
            
            csv_line = f'{datatime_value},{values[2]},{values[3]},{values[4]}\n'.encode('utf-8')
            print(csv_line)
            with hdfs_client.write(HDFS_FILE, append=True) as writer:
                writer.write(csv_line)
        else:
            print(f"Error: Not enough values in payload: {payload}")
    else:
        print(f"Error: Payload is not a string: {payload}")