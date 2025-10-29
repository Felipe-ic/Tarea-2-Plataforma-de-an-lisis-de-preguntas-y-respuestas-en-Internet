# database.py

import sqlite3

DATABASE_NAME = 'results.db'

def create_table():
    # Función que crea la tabla (necesaria para el primer arranque)
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_questions (
            question TEXT PRIMARY KEY,
            score REAL,
            llm_response TEXT,
            retries INTEGER
        )
    """)
    conn.commit()
    conn.close()

def check_if_processed(question):
    # Función clave para el generador de tráfico 
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT llm_response, score FROM processed_questions WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    return result is not None # Retorna True si la pregunta ya tiene un score 
    
def save_response(question, llm_response, score, retries):
    """Guarda la respuesta final validada por Flink en la base de datos."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    

