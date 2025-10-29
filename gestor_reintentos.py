# consumer_error.py (NUEVO)
from kafka import KafkaConsumer, KafkaProducer
import json, time, random

consumer = KafkaConsumer('errores_llm',
                         bootstrap_servers='kafka:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))
producer = KafkaProducer(bootstrap_servers='kafka:9092',
                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Limite para evitar reintentos infinitos por fallos del LLM
MAX_RETRY = 5 

for msg in consumer:
    data = msg.value
    reintentos = data.get("retries", 0)
    error_type = data.get("error", "Unknown")

    if reintentos < MAX_RETRY:
        # Estrategia de reintento: Retardo (simulando exponential backoff o espera por cuota)
        sleep_time = 0
        if "OVERLOAD" in error_type:
            # Backoff simple: 2s base + aleatorio, para sobrecarga
            sleep_time = 2 + (reintentos * random.uniform(0.5, 1.5)) 
        elif "QUOTA_LIMIT" in error_type:
            # Retardo más largo para cuota: 10s fijos, asumiendo que el límite se reinicia en X tiempo
            sleep_time = 10 
        else:
            sleep_time = 3

        print(f"[Consumer Error] Fallo '{error_type}' para {data['id']}. Reintentando en {sleep_time:.2f}s (Intento #{reintentos})")
        time.sleep(sleep_time)

        # Reinyectar al tópico 'preguntas' con el contador actualizado
        new_msg = {"id": data['id'], "question": data['question'], "retries": reintentos}
        producer.send('preguntas', new_msg)
    else:
        print(f"[Consumer Error] Fallo '{error_type}' para {data['id']}. Límite de reintentos ({MAX_RETRY}) alcanzado. Descartando.")

    producer.flush()