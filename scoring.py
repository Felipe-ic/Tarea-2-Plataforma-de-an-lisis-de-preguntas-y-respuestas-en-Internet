# scoring.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk import jaccard_distance
from nltk.util import ngrams
import math # Necesario para la función min/max de len() si no usas type hints

def compute_score(reference: str, generated: str) -> float:
    """
    Calcula un score compuesto de calidad basado en Cosine Similarity, Jaccard Index, 
    y Length Ratio. Maneja respuestas nulas o vacías.
    """
    
    # CRÍTICO: 1. MANEJO DE VALORES NULOS O VACÍOS
    
    if not reference or not generated:
        print("[Scoring] Advertencia: Respuesta o Referencia es nula/vacía. Devolviendo score 0.")
        return 0.0
    
    # CRÍTICO: 2. MANEJO DE STRINGS VACÍOS O ESPACIOS (Evita errores de división por cero o TFIDF)
    # Si las cadenas son solo espacios o tienen longitud cero después del chequeo inicial
    reference = reference.strip()
    generated = generated.strip()
    if not reference or not generated:
         return 0.0

    try:
        # 1. TF-IDF + Cosine Similarity
        # fit() requiere una lista de strings
        vectorizer = TfidfVectorizer().fit([reference, generated])
        tfidf_matrix = vectorizer.transform([reference, generated])
        cosine_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        # 2. Jaccard Index (usando bigramas para mejor discriminación)
        ref_set = set(ngrams(reference.split(), 2))
        gen_set = set(ngrams(generated.split(), 2))
        
        # Jaccard solo está definido si al menos un conjunto no está vacío.
        if not ref_set and not gen_set:
            jaccard_score = 1.0 
        elif not ref_set or not gen_set:
            jaccard_score = 0.0 
        else:
            jaccard_score = 1 - jaccard_distance(ref_set, gen_set)
        
        # 3. Length ratio
        len_ref = len(reference)
        len_gen = len(generated)
        length_ratio = min(len_ref, len_gen) / max(len_ref, len_gen)

        # 4. Score compuesto (Promedio simple de las 3 métricas)
        final_score = (cosine_score + jaccard_score + length_ratio) / 3
        
        # Retorna el score real
        return final_score 
        
    except Exception as e:
        # Captura errores que puedan ocurrir durante tokenización o cálculo de n-gramas
        print(f"[Scoring] Error inesperado durante el cálculo del score: {e}")
        return 0.0