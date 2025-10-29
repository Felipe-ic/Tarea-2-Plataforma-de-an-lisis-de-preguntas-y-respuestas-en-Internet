# ollama_client.py 
import csv
import random
import os
import ollama

# CONFIGURACIÓN DE CONEXIÓN LLM 

# ollama_client.py

OLLAMA_SERVER_HOST = "http://ollama:11434" 
OLLAMA_MODEL = "mistral"


# CARGA DE DATASET 
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "test.csv")

column_names = ["question_id", "question_text", "question_title", "best_answer_text"]

# Cargar dataset
with open(DATA_PATH, encoding="utf-8-sig") as f:
    # Ignoramos la primera línea si es el encabezado del CSV
    reader = csv.DictReader(f, fieldnames=column_names)
    dataset = list(reader)

def get_random_question():
    """
    Retorna una pregunta aleatoria del dataset.
    """
    row = random.choice(dataset)
    # Retorna ID, Question, y Expected Answer (para scoring)
    return row["question_id"], row["question_text"], row["best_answer_text"]

def ask_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """
    Envía un prompt al modelo local de Ollama, forzando la conexión al host de Docker.
    """
    try:
        response = ollama.chat(
            
            host=OLLAMA_SERVER_HOST, 
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        # Esto imprimirá el error real si no puede conectarse 
        return f"[Error Ollama capturado] {e}"

if __name__ == "__main__":
    # ejecutar este archivo directamente, intentara conectarse al host.docker.internal
    q_id, question, best_answer = get_random_question()

    print(f"\n🧩 Pregunta #{q_id}: {question}")
    print(f"📚 Respuesta original: {best_answer}\n")

    respuesta = ask_ollama(f"Responde esta pregunta de forma breve y clara:\n{question}")
    print(f"💬 Respuesta generada por Ollama:\n{respuesta}")