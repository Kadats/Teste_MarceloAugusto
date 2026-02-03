import axios from 'axios';

// Cria uma instância do Axios configurada para bater no seu Backend
const api = axios.create({
    baseURL: 'http://localhost:8000', // Porta onde o FastAPI está rodando
});

export default api;