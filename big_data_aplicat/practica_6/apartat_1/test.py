#!/usr/bin/env python3
import json
import uuid
from datetime import datetime
from kafka import KafkaConsumer
from hdfs import InsecureClient
import traceback
import os

# Configuración
KAFKA_TOPIC = 'sensor-data'
BOOTSTRAP_SERVERS = ['localhost:9092']
HDFS_URL = 'http://hadoopmaster:9870'
HDFS_USER = 'hadoop'
HDFS_DIR = '/user/hadoop/kafka'
HDFS_FILE_PREFIX = 'sensor_data_'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

# Cliente HDFS
hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)

# Asegurar que el directorio existe
try:
    if not hdfs_client.status(HDFS_DIR, strict=False):
        hdfs_client.makedirs(HDFS_DIR)
        print(f"Se ha creado el directorio HDFS: {HDFS_DIR}")
except Exception as e:
    print(f"Error al verificar/crear directorio: {e}")

def process_csv_message(raw_message):
    """
    Procesa un mensaje en formato CSV directo y lo escribe en un archivo único en HDFS
    """
    try:
        # Decodificar bytes a string
        if isinstance(raw_message, bytes):
            csv_data = raw_message.decode('utf-8', errors='replace')
        else:
            csv_data = str(raw_message)
            
        print(f"Procesando datos CSV: {csv_data}")
        
        # Separar el payload por comas
        values = csv_data.split(',')
        
        # Verificar que tengamos suficientes elementos
        if len(values) < 5:
            print(f"Error: No hay suficientes valores en los datos: {csv_data}")
            return
        
        # Procesar fecha y hora
        datetime_str = f'{values[0]} {values[1]}'
        
        try:
            # Intentar parsear la fecha/hora del mensaje
            parsed_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT)
            timestamp = parsed_datetime.strftime('%Y%m%d%H%M%S')
        except ValueError as e:
            print(f'Error: Formato de fecha/hora inválido: {datetime_str}')
            # Usar hora actual como respaldo
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generar un ID único para evitar colisiones
        unique_id = str(uuid.uuid4())[:8]
        
        # Construir nombre de archivo único para este mensaje
        # Formato: sensor_data_YYYYMMDDHHMMSS_uuid.csv
        filename = f"{HDFS_FILE_PREFIX}{timestamp}_{unique_id}.csv"
        hdfs_path = f"{HDFS_DIR}/{filename}"
        
        # Construir línea CSV correctamente
        csv_line = f'{values[0]},{values[1]},{values[2]},{values[3]},{values[4]}\n'.encode('utf-8')
        print(f"Línea CSV a escribir: {csv_line}")
        
        # Escribir en un archivo nuevo en HDFS (sin usar append)
        with hdfs_client.write(hdfs_path, overwrite=True) as writer:
            writer.write(csv_line)
            
        print(f"Datos escritos en HDFS con éxito: {hdfs_path}")
            
    except Exception as e:
        print(f"Error al procesar o escribir datos: {e}")
        traceback.print_exc()

def main():
    """
    Función principal para iniciar el consumidor Kafka
    """
    print("Iniciando consumidor Kafka...")
    
    try:
        # Configuramos el consumidor sin deserializador
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sensor-data-consumer'
            # Sin deserializador - recibimos bytes crudos
        )
        
        print(f"Consumidor conectado, esperando mensajes en el tema '{KAFKA_TOPIC}'...")
        
        for message in consumer:
            try:
                # Obtener datos en bruto
                raw_data = message.value
                print(f"Datos recibidos: {raw_data[:100]}")
                
                # Procesar directamente como CSV
                process_csv_message(raw_data)
                
            except Exception as e:
                print(f"Error al procesar mensaje: {e}")
                traceback.print_exc()
                
    except KeyboardInterrupt:
        print("Consumidor detenido por el usuario")
    except Exception as e:
        print(f"Error al iniciar el consumidor: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()