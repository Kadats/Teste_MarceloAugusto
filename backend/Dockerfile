# 1. Imagem base (Python leve)
FROM python:3.12-slim

# 2. Pasta de trabalho dentro do container
WORKDIR /app

# 3. Instalar dependências do sistema (necessário para psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# 4. Copiar e instalar bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo o código do backend
COPY . .

# 6. Comando para rodar a API
# --host 0.0.0.0 libera o acesso externo ao container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

