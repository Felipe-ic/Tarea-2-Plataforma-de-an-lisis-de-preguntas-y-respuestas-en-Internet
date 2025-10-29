# procesador_flink.py

from kafka import KafkaConsumer, KafkaProducer, errors # Importar errores
import json
from scoring import compute_score 
import time # Necesario para la espera

# Constantes de Kafka
KAFKA_BROKER = 'kafka:9092'
TOPIC_EXITOSAS = 'respuestas_exitosas'
TOPIC_PREGUNTAS = 'preguntas'
TOPIC_VALIDADAS = 'respuestas_validadas'

UMBRAL_SCORE = 0.7 
MAX_REINJECTION = 2 

def run_flink_processor():
    """
    Simulación de Flink: Consume respuestas, calcula score y decide si persistir o reinyectar.
    """
    
    # 1. Conexión Resiliente (Consumidor)
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC_EXITOSAS,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='flink-processor-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print(f"[Procesador Flink] Conectado a Kafka exitosamente al tópico '{TOPIC_EXITOSAS}'.")
        except errors.NoBrokersAvailable:
            print("[Procesador Flink] Kafka no está disponible. Reintentando conexión en 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"[Procesador Flink] Error inesperado durante la conexión: {e}")
            time.sleep(5)

    # 2. Conexión Resiliente (Productor)
    
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # 3. Bucle principal de procesamiento (Feedback Loop)
    for msg in consumer:
        data = msg.value
        reference_answer = data["expected"]
        generated_answer = data["answer"]
        reintentos = data.get("retries", 0)
        
        
        score = compute_score(reference_answer, generated_answer) 
        print(f"[Procesador Flink] Calculando score para #{data['id']} (Retries: {reintentos}): {score:.3f}")

        # Decisión del Flujo 
        if score >= UMBRAL_SCORE:
            # 5a. Persistencia (Score )
            data['score'] = score 
            producer.send(TOPIC_VALIDADAS, data) 
            print(f"[Procesador Flink] Score {score:.3f} >= {UMBRAL_SCORE} (Umbral). Enviando a persistencia.")
        
        elif reintentos < MAX_REINJECTION:
            # 5b. Regeneración (Score bajo y reintentos restantes)
            new_msg = data.copy()
            new_msg["retries"] = reintentos + 1
            producer.send(TOPIC_PREGUNTAS, new_msg)
            print(f"[Procesador Flink] Score {score:.3f} < {UMBRAL_SCORE}. Reinyectando pregunta (Reintento #{reintentos + 1}).")
        
        else:
            # Límite de reintentos alcanzado (Prevención de ciclos)
            print(f"[Procesador Flink] Pregunta #{data['id']} ha superado el límite de reintentos ({MAX_REINJECTION}). Descartando.")

        producer.flush()

if __name__ == "__main__":
    run_flink_processor()