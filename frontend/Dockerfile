# 1. Imagem base (Node.js 20)
FROM node:20-slim

# 2. Pasta de trabalho
WORKDIR /app

# 3. Copiar arquivos de dependências primeiro (cache layer)
COPY package*.json ./

# 4. Instalar dependências
RUN npm install

# 5. Copiar o resto do código
COPY . .

# 6. Expor a porta do Vite
EXPOSE 5173

# 7. Rodar em modo desenvolvimento
# O "-- --host" é fundamental para acessar do Windows
CMD ["npm", "run", "dev", "--", "--host"]

