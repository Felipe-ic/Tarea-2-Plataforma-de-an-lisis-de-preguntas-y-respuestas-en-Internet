# persistor_bdd.py

from kafka import KafkaConsumer, errors
import json
import time

from database import save_response, create_table 

# Constantes de Kafka
KAFKA_BROKER = 'kafka:9092' 
TOPIC_VALIDADOS = 'respuestas_validadas'

def run_persistor():
    """
    Consumidor resiliente que persiste las respuestas validadas por Flink en la BDD.
    """
    
    # 1. Inicializar la BDD (para asegurar que la tabla exista)
    create_table()
    
    # 2. Conexión Resiliente a Kafka (Manejo de NoBrokersAvailable)
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC_VALIDADOS,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='persistor-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print(f"[Persistor BDD] Conectado a Kafka exitosamente al tópico '{TOPIC_VALIDADOS}'.")
            
        except errors.NoBrokersAvailable:
            print("[Persistor BDD] Kafka no está disponible. Reintentando conexión en 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"[Persistor BDD] Error inesperado durante la conexión: {e}")
            time.sleep(5)

    # 3. Bucle principal de consumo
    for msg in consumer:
        data = msg.value
        question = data["question"]
        
        answer = data.get("generated_answer", data.get("answer")) 
        score = data["score"]
        retries = data["retries"]
        
        try:
           
            save_response(question, answer, score, retries)
            print(f"**[DB]** Pregunta #{data['id']} guardada/actualizada. Score: {score}")
        except Exception as e:
            print(f"[Storage Error] No se pudo guardar pregunta #{data['id']}: {e}")

if __name__ == "__main__":
    run_persistor()