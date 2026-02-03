<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>💰 Monitor de Despesas ANS</h1>
      <p>Análise financeira das Operadoras de Saúde</p>
    </header>

    <div class="search-section">
      <input 
        v-model="termoBusca" 
        @input="buscarOperadoras"
        type="text" 
        placeholder="🔍 Digite o nome da operadora..." 
        class="search-input"
      />
    </div>

    <div class="content-grid">
      
      <div class="card table-card">
        <h2>Listagem Geral</h2>
        <div v-if="loading" class="loading">Carregando dados...</div>
        
        <table v-else>
          <thead>
            <tr>
              <th>Operadora</th>
              <th>UF</th>
              <th class="text-right">Total Despesas</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="op in listaOperadoras" :key="op.razao_social">
              <td>{{ op.razao_social }}</td>
              <td><span class="badge">{{ op.uf }}</span></td>
              <td class="text-right">{{ formatarMoeda(op.total_despesas) }}</td>
            </tr>
            <tr v-if="listaOperadoras.length === 0">
              <td colspan="3" class="text-center">Nenhuma operadora encontrada.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card chart-card">
        <h2>🏆 Top 10 Maiores Despesas</h2>
        <div class="chart-container">
          <Bar v-if="chartData.labels" :data="chartData" :options="chartOptions" />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api'; // Nossa conexão com o Python
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';
import { Bar } from 'vue-chartjs';

// Registra os componentes do gráfico
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// --- ESTADO (Variáveis Reativas) ---
const listaOperadoras = ref([]);
const termoBusca = ref("");
const loading = ref(false);
const chartData = ref({});
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false } // Esconde a legenda pois só tem uma cor
  }
});

// --- FUNÇÕES ---

// Formata número para Real (R$)
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

// Busca a lista (Tabela)
const buscarOperadoras = async () => {
  // Pequeno delay para não chamar a API a cada letra digitada (Debounce simples)
  loading.value = true;
  try {
    const response = await api.get('/operadoras', {
      params: { busca: termoBusca.value }
    });
    listaOperadoras.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar operadoras:", error);
  } finally {
    loading.value = false;
  }
};

// Busca o Top 10 (Gráfico)
const carregarGrafico = async () => {
  try {
    const response = await api.get('/dashboard/top-10');
    const dados = response.data;

    // Prepara os dados para o Chart.js
    chartData.value = {
      labels: dados.map(d => d.razao_social.substring(0, 15) + '...'), // Abrevia nomes longos
      datasets: [{
        label: 'Total de Despesas (R$)',
        backgroundColor: '#3b82f6', // Azul bonito
        data: dados.map(d => d.total_despesas)
      }]
    };
  } catch (error) {
    console.error("Erro ao carregar gráfico:", error);
  }
};

// Ao iniciar a tela
onMounted(() => {
  buscarOperadoras(); // Carrega tabela inicial
  carregarGrafico();  // Carrega gráfico
});
</script>

<style scoped>
/* --- ESTILO CSS (Simples e Limpo) --- */
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 { color: #1e3a8a; margin-bottom: 5px; }
.header p { color: #64748b; margin-top: 0; }

/* Barra de Busca */
.search-section {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.search-input {
  width: 100%;
  max-width: 500px;
  padding: 12px 20px;
  border: 1px solid #cbd5e1;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: box-shadow 0.3s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

/* Grid Layout */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Duas colunas iguais */
  gap: 20px;
}

/* Cards (Caixas brancas) */
.card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.card h2 {
  font-size: 18px;
  color: #475569;
  margin-top: 0;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

/* Tabela */
table { width: 100%; border-collapse: collapse; }
th { text-align: left; color: #64748b; font-weight: 600; padding: 10px; }
td { padding: 12px 10px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
.text-right { text-align: right; }
.text-center { text-align: center; color: #94a3b8; }

.badge {
  background: #eff6ff;
  color: #3b82f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

/* Gráfico */
.chart-container {
  height: 300px; /* Altura fixa para o gráfico */
}

/* Responsividade (Celular) */
@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; } /* Vira uma coluna só */
}
</style>