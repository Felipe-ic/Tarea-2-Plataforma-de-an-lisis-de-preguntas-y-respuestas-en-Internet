# consumidor_llm.py 
from kafka import KafkaConsumer, KafkaProducer
from ollama_client import ask_ollama
import json, time, random

# Inicialización de Kafka 

consumer = KafkaConsumer('preguntas',
                         bootstrap_servers='kafka:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))
producer = KafkaProducer(bootstrap_servers='kafka:9092',
                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for msg in consumer:
    data = msg.value
    reintentos = data.get("retries", 0)

    print(f"[Consumer LLM] Procesando pregunta {data['id']} (Reintento: {reintentos})")

    #  SIMULACIÓN DE ERRORES 
    question_lower = data['question'].lower()

    latencia_simulada = random.uniform(30, 60)
    print(f"[Consumer LLM] Simulación: LLM tardará {latencia_simulada:.2f} segundos...")
    time.sleep(latencia_simulada)
    
    error_type = None
    if "overload" in question_lower:
        error_type = "OVERLOAD"
    elif "quota" in question_lower:
        error_type = "QUOTA_LIMIT"
    

    if error_type:
        # Lógica de simulación de error de Ollama
        error_msg = {"id": data['id'], "question": data['question'], "error": error_type, "retries": reintentos + 1}
        producer.send('errores_llm', error_msg)
    else:
        try:
            
            # Si el LLM está caído, esta línea LANZARÁ una excepción
            respuesta = ask_ollama(data['question']) 
            
            out = {"id": data['id'], "question": data['question'], "answer": respuesta, "expected": data.get("expected")}
            producer.send('respuestas_exitosas', out)
            
        except Exception as e:
            # Captura cualquier fallo de conexión/LLM y lo envía al gestor de reintentos
            print(f"[Error LLM] FALLÓ CONEXIÓN/MODELO para {data['id']}: {e}")
            error_msg = {"id": data['id'], "question": data['question'], "error": "LLM_CONNECTION_FAILED", "retries": reintentos + 1}
            producer.send('errores_llm', error_msg)

    producer.flush()