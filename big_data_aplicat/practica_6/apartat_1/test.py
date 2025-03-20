#!/usr/bin/env python3
import json
from datetime import datetime
from kafka import KafkaConsumer
from hdfs import InsecureClient
import traceback

# Configuración
KAFKA_TOPIC = 'sensor-data'
BOOTSTRAP_SERVERS = ['localhost:9092']
HDFS_URL = 'http://hadoopmaster:9870'
HDFS_USER = 'hadoop'
HDFS_FILE = '/user/hadoop/kafka/section1.csv'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

# Cliente HDFS
hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)

# Crear archivo si no existe
if not hdfs_client.status(HDFS_FILE, strict=False):
    with hdfs_client.write(HDFS_FILE, overwrite=True) as writer:
        writer.write(b'')
        print(f"Se ha creado el archivo HDFS: {HDFS_FILE}")

def safe_deserializer(raw_bytes):
    """
    Deserializador más robusto que maneja posibles errores en el formato JSON
    """
    try:
        # Primer intento: parseo JSON estándar
        text = raw_bytes.decode('utf-8')
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Error de decodificación JSON: {e}")
        
        # Depuración: Mostrar la parte problemática
        text = raw_bytes.decode('utf-8', errors='replace')
        error_context = text[max(0, e.pos-15):min(len(text), e.pos+15)]
        print(f"Problema cerca de: '{error_context}'")
        print(f"Posición del error: {e.pos}")
        
        # Alternativa: Intentar tomar solo el primer objeto JSON válido
        try:
            # Algunos mensajes Kafka pueden tener datos extra después del JSON válido
            valid_part = text[:e.pos]
            # Encontrar la última llave de cierre
            last_brace = valid_part.rfind('}')
            if last_brace > 0:
                return json.loads(valid_part[:last_brace+1])
        except Exception as inner_e:
            print(f"Error al intentar recuperar JSON parcial: {inner_e}")
            
        # Mostrar los bytes en bruto para depuración
        print(f"Mensaje en bruto (primeros 50 bytes): {raw_bytes[:50]}")
            
        # Devolver diccionario vacío si todo lo demás falla
        return {}

def process_message(msg):
    """
    Procesa un mensaje y lo escribe en HDFS
    """
    print('Mensaje recibido: ', msg)
    
    # Obtener payload con manejo seguro de tipos
    payload = msg.get('payload', '')
    
    # Verificar que payload sea una cadena
    if not isinstance(payload, str):
        print(f"Error: Payload no es una cadena: {type(payload)}")
        if isinstance(payload, dict):
            # Si payload es un diccionario, podríamos intentar extraer información
            print(f"Payload como diccionario: {payload}")
            return
        elif payload is None:
            print("Payload es None, saltando este mensaje")
            return
        
        # Intentar convertir a string si no es None
        try:
            payload = str(payload)
            print(f"Payload convertido a cadena: {payload}")
        except:
            return
    
    # Separar el payload por comas
    values = payload.split(',')
    
    # Verificar que tengamos suficientes elementos
    if len(values) < 5:
        print(f"Error: No hay suficientes valores en el payload: {payload}")
        return
    
    # Procesar fecha y hora
    datetime_str = f'{values[0]} {values[1]}'
    datatime_value = datetime.now().strftime(DATETIME_FORMAT)  # Valor por defecto
    
    try:
        datatime_value = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime(DATETIME_FORMAT)
    except ValueError as e:
        print(f'Error: Formato de fecha/hora inválido: {datetime_str}')
        print(f'Usando hora actual: {datatime_value}')
    
    # Construir línea CSV correctamente
    try:
        csv_line = f'{datatime_value},{values[2]},{values[3]},{values[4]}\n'.encode('utf-8')
        print(f"Línea CSV a escribir: {csv_line}")
        
        # Escribir en HDFS
        with hdfs_client.write(HDFS_FILE, append=True) as writer:
            writer.write(csv_line)
            
        print("Datos escritos en HDFS con éxito")
            
    except Exception as e:
        print(f"Error al procesar o escribir datos: {e}")
        traceback.print_exc()

def main():
    """
    Función principal para iniciar el consumidor Kafka
    """
    print("Iniciando consumidor Kafka...")
    
    try:
        # Primero intentamos con el deserializador seguro
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sensor-data-consumer',
            value_deserializer=safe_deserializer
        )
        
        print(f"Consumidor conectado, esperando mensajes en el tema '{KAFKA_TOPIC}'...")
        
        for message in consumer:
            try:
                process_message(message.value)
            except Exception as e:
                print(f"Error al procesar mensaje: {e}")
                traceback.print_exc()
                
    except KeyboardInterrupt:
        print("Consumidor detenido por el usuario")
    except Exception as e:
        print(f"Error al iniciar el consumidor: {e}")
        
        # Intentar iniciar con deserializador simple
        print("Intentando iniciar sin deserializador...")
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='sensor-data-consumer',
                value_deserializer=None  # Sin deserializador
            )
            
            print("Consumidor reiniciado sin deserializador...")
            
            for message in consumer:
                try:
                    # Mensaje en bytes brutos
                    raw_bytes = message.value
                    print(f"Mensaje en bruto: {raw_bytes[:100]}")
                    
                    # Intentar decodificar manualmente
                    try:
                        text = raw_bytes.decode('utf-8', errors='replace')
                        print(f"Mensaje decodificado: {text[:100]}")
                        
                        # Intentar parsear como JSON
                        data = json.loads(text)
                        process_message(data)
                    except json.JSONDecodeError as je:
                        print(f"Error decodificando JSON: {je}")
                        # Mostrar contexto del error
                        error_pos = je.pos
                        print(f"Contexto del error: '{text[max(0, error_pos-10):min(len(text), error_pos+10)]}'")
                except Exception as e:
                    print(f"Error procesando mensaje en bruto: {e}")
                    traceback.print_exc()
        except Exception as e2:
            print(f"Error en modo fallback: {e2}")
            traceback.print_exc()

if __name__ == "__main__":
    main()