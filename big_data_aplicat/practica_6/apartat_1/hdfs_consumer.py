#!/usr/bin/env python3
import json
from datetime import datetime
import os
import time
import socket
import traceback
import subprocess
from kafka import KafkaConsumer
import uuid

# Configuración
KAFKA_TOPIC = 'sensor-data'
BOOTSTRAP_SERVERS = ['localhost:9092']
HDFS_FILE = '/user/hadoop/kafka/kafka_data.csv'
LOCAL_BUFFER_FILE = f"/tmp/kafka_hdfs_buffer_{uuid.uuid4().hex}.csv"
LOCAL_MASTER_FILE = f"/tmp/kafka_hdfs_master_{uuid.uuid4().hex}.csv"
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'
BUFFER_FLUSH_INTERVAL = 10  # segundos
BUFFER_FLUSH_SIZE = 10  # líneas

buffer_last_flush = time.time()
buffer_line_count = 0
total_records_processed = 0

def setup_environment():
    """
    Entorn de configuracio per al consumidor
    """
    print("🚀 Iniciando configuración del entorno...")
    
    try:
        with open(LOCAL_BUFFER_FILE, 'w') as f:
            pass 
        
        with open(LOCAL_MASTER_FILE, 'w') as f:
            pass 
            
        print(f"✅ Buffers locales creados")
    except Exception as e:
        print(f"❌ Error al crear buffers locales: {e}")
        raise
    
    # Verificar que el directorio HDFS exista
    parent_dir = os.path.dirname(HDFS_FILE)
    try:
        check_cmd = f"hdfs dfs -test -d {parent_dir} || hdfs dfs -mkdir -p {parent_dir}"
        subprocess.run(check_cmd, shell=True, check=True)
        print(f"✅ Directorio HDFS verificado: {parent_dir}")
    except subprocess.CalledProcessError:
        try:
            mkdir_cmd = f"hdfs dfs -mkdir -p {parent_dir}"
            subprocess.run(mkdir_cmd, shell=True, check=True)
            print(f"✅ Directorio HDFS creado: {parent_dir}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al crear directorio HDFS: {e}")
            raise
    
    return True

def safe_deserializer(raw_bytes):
    """
    Deserializador robust
    """
    try:
        text = raw_bytes.decode('utf-8')
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️ Error de decodificación JSON: {e}")
        
        text = raw_bytes.decode('utf-8', errors='replace')
        error_context = text[max(0, e.pos-15):min(len(text), e.pos+15)]
        print(f"Problema cerca de: '{error_context}'")
        
        try:
            valid_part = text[:e.pos]
            last_brace = valid_part.rfind('}')
            if last_brace > 0:
                return json.loads(valid_part[:last_brace+1])
        except Exception as inner_e:
            print(f"Error al intentar recuperar JSON parcial: {inner_e}")
        return {}

def append_to_local_buffer(csv_line):
    """
    Disclaimer: Aixo es una funcio desenvolupada per Claude
    """
    global buffer_line_count, total_records_processed
    
    try:
        # Escribir en el buffer temporal
        with open(LOCAL_BUFFER_FILE, 'ab') as f:
            f.write(csv_line)
        
        # También escribir en el archivo master que mantiene todos los datos
        with open(LOCAL_MASTER_FILE, 'ab') as f:
            f.write(csv_line)
            
        buffer_line_count += 1
        total_records_processed += 1
        return True
    except Exception as e:
        print(f"❌ Error al escribir en buffer local: {e}")
        return False

def flush_buffer_to_hdfs(force=False):
    """
    Disclaimer: Aixo es una funcio desenvolupada per Claude
    """
    global buffer_last_flush, buffer_line_count
    
    current_time = time.time()
    time_since_last_flush = current_time - buffer_last_flush
    
    # Verificar si debemos hacer flush
    should_flush = (
        force or 
        buffer_line_count >= BUFFER_FLUSH_SIZE or 
        time_since_last_flush >= BUFFER_FLUSH_INTERVAL
    )
    
    if not should_flush or buffer_line_count == 0:
        return True
    
    print(f"🔄 Enviando buffer a HDFS ({buffer_line_count} líneas)...")
    
    try:
        # En lugar de intentar append, vamos a subir todo el archivo master de una vez
        # Esta estrategia evita problemas de append y lease
        put_cmd = f"hdfs dfs -put -f {LOCAL_MASTER_FILE} {HDFS_FILE}"
        subprocess.run(put_cmd, shell=True, check=True)
        
        # Reiniciar buffer local (pero no el master)
        with open(LOCAL_BUFFER_FILE, 'w') as f:
            pass  # Vaciar archivo
        
        buffer_last_flush = current_time
        buffer_line_count = 0
        print(f"✅ Datos enviados a HDFS correctamente ({total_records_processed} registros en total)")
        return True
    except Exception as e:
        print(f"❌ Error al enviar datos a HDFS: {e}")
        traceback.print_exc()
        
        # Intentar método alternativo con -moveFromLocal
        try:
            print("⚠️ Intentando método alternativo...")
            # Crear una copia temporal del archivo master
            temp_file = f"{LOCAL_MASTER_FILE}.copy"
            copy_cmd = f"cp {LOCAL_MASTER_FILE} {temp_file}"
            subprocess.run(copy_cmd, shell=True, check=True)
            
            # Intentar con moveFromLocal
            move_cmd = f"hdfs dfs -put -f {temp_file} {HDFS_FILE}"
            subprocess.run(move_cmd, shell=True, check=True)
            
            # Limpiar
            os.remove(temp_file)
            
            buffer_last_flush = current_time
            buffer_line_count = 0
            print(f"✅ Datos enviados a HDFS con método alternativo")
            return True
        except Exception as e2:
            print(f"❌ Error con método alternativo: {e2}")
            return False

def process_message(msg):
    """
    Aquesta funcio emplea la meva antiga logica i la emplea per processar els missatges
    """
    print('📨 Mensaje recibido: ', msg)
    
    payload = msg.get('payload', '')
    
    if not isinstance(payload, str):
        print(f"⚠️ Error: Payload no es una cadena: {type(payload)}")
        if isinstance(payload, dict):
            print(f"Payload como diccionario: {payload}")
            return
        elif payload is None:
            print("Payload es None, saltando este mensaje")
            return
        
        try:
            payload = str(payload)
            print(f"Payload convertido a cadena: {payload}")
        except:
            return
    
    values = payload.split(',')

    if len(values) < 5:
        print(f"⚠️ Error: No hay suficientes valores en el payload: {payload}")
        return
    
    datetime_str = f'{values[0]} {values[1]}'
    datatime_value = datetime.now().strftime(DATETIME_FORMAT)  # Valor por defecto
    
    try:
        datatime_value = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime(DATETIME_FORMAT)
    except ValueError as e:
        print(f'⚠️ Error: Formato de fecha/hora inválido: {datetime_str}')
        print(f'Usando hora actual: {datatime_value}')
    
    try:
        csv_line = f'{datatime_value},{values[2]},{values[3]},{values[4]}\n'.encode('utf-8')
        print(f"📝 Línea CSV: {csv_line}")
        
        if append_to_local_buffer(csv_line):
            print("✅ Datos añadidos al buffer local")
            flush_buffer_to_hdfs()
        else:
            print("❌ Error al añadir datos al buffer")
            
    except Exception as e:
        print(f"❌ Error al procesar datos: {e}")
        traceback.print_exc()

def main():
    """
    Función principal para iniciar el consumidor Kafka
    """
    global buffer_last_flush
    
    try:
        if not setup_environment():
            raise Exception("Error al configurar el entorno")
        
        buffer_last_flush = time.time()
        
        print("🚀 Iniciando consumidor Kafka...")
        
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='sensor-data-consumer',
            value_deserializer=safe_deserializer
        )
        
        print(f"✅ Consumidor conectado, esperando mensajes en el tema '{KAFKA_TOPIC}'...")
        
        # Configurar timer para flush periódico incluso sin mensajes
        last_check_time = time.time()
        check_interval = min(BUFFER_FLUSH_INTERVAL, 5) 
        
        try:
            for message in consumer:
                try:
                    process_message(message.value)
                except Exception as e:
                    print(f"❌ Error al procesar mensaje: {e}")
                    traceback.print_exc()
                
                # Verificar si debemos hacer un flush periódico
                current_time = time.time()
                if current_time - last_check_time > check_interval:
                    flush_buffer_to_hdfs()
                    last_check_time = current_time
                    
        except KeyboardInterrupt:
            print("⛔ Consumidor detenido por el usuario")
        finally:
            # Asegurar que se envíe cualquier dato pendiente
            flush_buffer_to_hdfs(force=True)
            
            # Limpiar archivos temporales
            try:
                os.remove(LOCAL_BUFFER_FILE)
                os.remove(LOCAL_MASTER_FILE)
                print(f"✅ Archivos temporales eliminados")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        traceback.print_exc()
        
        # Intentar modo de respaldo sin deserializador
        try:
            print("⚠️ Intentando modo de respaldo...")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='sensor-data-consumer-fallback'
            )
            
            print("✅ Consumidor de respaldo iniciado...")
            
            for message in consumer:
                try:
                    # Procesar mensaje en bruto
                    raw_bytes = message.value
                    text = raw_bytes.decode('utf-8', errors='replace')
                    
                    try:
                        data = json.loads(text)
                        process_message(data)
                    except json.JSONDecodeError:
                        print(f"⚠️ Error decodificando JSON de respaldo")
                except Exception as e:
                    print(f"❌ Error en modo de respaldo: {e}")
                    
        except Exception as e2:
            print(f"❌ Error en modo de respaldo: {e2}")
            
        finally:
            # Asegurar que se envíe cualquier dato pendiente
            flush_buffer_to_hdfs(force=True)
            
            # Limpiar buffer local
            try:
                os.remove(LOCAL_BUFFER_FILE)
                os.remove(LOCAL_MASTER_FILE)
            except:
                pass

if __name__ == "__main__":
    main()