FROM python:3.12-slim

WORKDIR /app

# 1. Copiar los requisitos
COPY requirements.txt .

# 2. INSTALAR LIBRERÍAS DE PYTHON
# ESTA LÍNEA DEBE IR PRIMERO: Instala nltk, kafka-python, etc.
RUN pip install --no-cache-dir -r requirements.txt

# 3. DESCARGAR RECURSOS DE NLTK
# Esta línea solo funcionará porque nltk ya está instalado en el paso anterior.
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# 4. Copiar el resto del código
COPY . .