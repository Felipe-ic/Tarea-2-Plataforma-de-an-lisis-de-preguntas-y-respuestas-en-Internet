# generador_trafico.py

from kafka import KafkaProducer
import json
import time
import random 
import csv
import os 
from database import check_if_processed, create_table 

#  CONSTANTES DE CONFIGURACIÓN 

KAFKA_BROKER = 'kafka:9092'  
TOPIC_PREGUNTAS = 'preguntas'
CSV_FILE = 'test.csv'

# FUNCIÓN DE LECTURA DE DATOS (Necesaria para cargar test.csv)
def load_questions():
    """Carga todas las preguntas del CSV y asigna IDs."""
    questions_list = []
    
    try:
        # Abre el archivo en el directorio de trabajo (/app en Docker)
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                questions_list.append({
                    "id": i + 1,
                    "question": row.get('question', f"PREGUNTA_{i+1}"), 
                    "expected": row.get('best_answer', "RESPUESTA_ESPERADA")
                })
    except FileNotFoundError:
        print(f"❌ ERROR: Archivo '{CSV_FILE}' no encontrado en {os.getcwd()}")
        return [{"id": 0, "question": "Pregunta de prueba (Fallback)", "expected": "Respuesta de prueba"}]
        
    return questions_list

def get_random_question(questions_data):
    """Selecciona una pregunta aleatoria de la lista cargada."""
    return random.choice(questions_data)


def run_traffic_generator():
    """
    Genera tráfico continuo, consultando el almacenamiento (Paso 2) antes de 
    enviar a Kafka (Paso 3).
    """
    
    # 1. Inicialización y Carga de Datos
    print(f"[Generador de Tráfico] Cargando preguntas de {CSV_FILE}...")
    questions_data = load_questions()
    if not questions_data:
        print("❌ [Generador de Tráfico] No hay preguntas para generar tráfico. Deteniendo.")
        return
        
    print(f"[Generador de Tráfico] {len(questions_data)} preguntas cargadas.")
    
    
    create_table() 
    
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # 2. Bucle de generación de tráfico
    while True:
        try:
            # Selecciona una pregunta base
            data = get_random_question(questions_data)
            q_id = data["id"]
            question_base = data["question"]
            best_answer = data["expected"]
            
           
            
            # Consultamos la BDD con la pregunta LIMPIA (asumiendo que la BDD guarda la versión limpia)
            if check_if_processed(question_base):
                print(f"✅ [Generador de Tráfico] Pregunta #{q_id} ya procesada. Omitiendo pipeline.")
                time.sleep(0.5)
                continue
            
            # Lógica de forzar errores y bajo score 
            
            question_kafka = question_base
            tipo = "NORMAL"
            
            # Forzar bajo score (para que Flink reinyecte)
            if q_id % 5 == 0:
                question_kafka = f"[BAJA_CALIDAD] {question_base}"
                tipo = "BAJA_CALIDAD"
            
            # Forzar error de LLM (para que Gestor_Reintentos actúe)
            elif q_id % 7 == 0:
                question_kafka = f"[ERROR_OVERLOAD] {question_base}"
                tipo = "ERROR_OVERLOAD"
            
            # PASO 3: Enviar a Kafka 
            
            msg = {
                "id": q_id, 
                "question": question_kafka, 
                "expected": best_answer, 
                "retries": 0,
                "max_flink_retries": 2 
            } 
            
            producer.send(TOPIC_PREGUNTAS, msg)
            producer.flush()

            print(f"➡️ [Generador de Tráfico] Pregunta #{q_id} NUEVA. Tipo: {tipo}. Enviada a Kafka.")
            time.sleep(1 + random.uniform(0.5, 1.5))

        except Exception as e:
            # Captura errores de conexión 
            print(f"❌ [Generador de Tráfico] Error de conexión/envío: {e}. Reintentando en 5s...") 
            time.sleep(5)

if __name__ == "__main__":
    run_traffic_generator()