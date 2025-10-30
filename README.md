# Tarea-2-Plataforma-de-an-lisis-de-preguntas-y-respuestas-en-Internet

#Limpiar Volúmenes y Detener Contenedores (si estaban corriendo):
#docker compose down -v


#Construir las Imágenes e Iniciar el Sistema: Este comando reconstruye las imágenes Python 
# (necesario si se modificó el código) y levanta todos los servicios definidos en docker-compose.yml
#
#docker compose up --build -d
#
#
#Una vez que el contenedor ollama esté activo, debes descargar el modelo de lenguaje que utilizará el sistema (asumimos mistral).
#docker exec -it ollama bash
#
#
#Descargar el modelo (Mistral):
#ollama pull mistral
#
#
#Para observar todos los mensajes (Generación, Reintentos, Scoring, Persistencia):
#docker compose logs -f

#Para detener todos los servicios y eliminar la red asociada:
#docker compose down
