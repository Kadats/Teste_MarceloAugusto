# 🏥 Monitor de Despesas - Dados Abertos ANS

> Teste Técnico para Engenharia de Dados / Full Stack - Intuitive Care

Este projeto é uma solução completa (End-to-End) para coleta, processamento, análise e visualização das despesas de Operadoras de Planos de Saúde, utilizando dados públicos da Agência Nacional de Saúde Suplementar (ANS).

---

## 🚀 Tecnologias Utilizadas

### Backend & Engenharia de Dados
* **Linguagem:** Python 3.12
* **Framework API:** FastAPI (Alta performance e documentação automática)
* **Banco de Dados:** PostgreSQL
* **ETL & Análise:** Pandas, SQLAlchemy, BeautifulSoup4
* **Infraestrutura:** Docker & Docker Compose

### Frontend
* **Framework:** Vue.js 3 (Composition API)
* **Build Tool:** Vite
* **Visualização:** Chart.js (Vue-Chartjs)
* **Cliente HTTP:** Axios

---

## 🛠️ Como Executar o Projeto

A maneira recomendada de executar a aplicação é utilizando **Docker**, garantindo que todo o ambiente (Banco, API e Interface) suba com um único comando, isolado do seu sistema operacional.

### Passo 1: Subir o Ambiente
No terminal, na raiz do projeto, execute:

```bash
docker compose up --build -d
```
*Aguarde alguns instantes para o build dos containers e inicialização do banco.*

### Passo 2: Popular o Banco de Dados (Pipeline ETL)
Como o banco de dados inicia vazio, é necessário rodar o orquestrador para baixar e processar os dados da ANS:

```bash
docker compose exec backend python main.py
```
*O sistema fará o download dos arquivos, correção de encoding, transformação e carga no PostgreSQL. Aguarde a mensagem "SUCESSO".*

### Passo 3: Acessar a Aplicação
* **Dashboard:** [http://localhost:5173](http://localhost:5173)
* **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)


---

## 🏗️ Arquitetura e Decisões Técnicas (Trade-offs)
Para cumprir o prazo de 7 dias com máxima eficiência e qualidade, as seguintes decisões arquiteturais foram tomadas:

### 1. Estratégia de Coleta (Scraper)
* **BeautifulSoup vs Selenium:** Optei pelo `BeautifulSoup` + `requests`. Como o diretório FTP da ANS é estático, o uso de Selenium seria um desperdício de recursos (overhead de memória). A solução atual é leve e extremamente rápida.

* **Armazenamento em Disco:** Os arquivos `.zip` são baixados para a pasta `/data` antes do processamento. Isso cria um checkpoint de segurança, evitando re-downloads em caso de falha no processamento, além de proteger a memória RAM contra estouros ao lidar com arquivos grandes.

### 2. Tratamento de Encoding (Desafio & Solução)
* **O Problema:** Identifiquei que os arquivos CSV da ANS utilizam codificação antiga (**ISO-8859-1/Latin-1**), enquanto o ambiente Python/Linux moderno opera em **UTF-8**. Isso causava erros de "mojibake" (ex: "MÉDICA" virava "MÃDICA").

* **A Solução:** Implementei uma leitura resiliente ("Fallback Strategy") no pipeline. O sistema tenta ler em **UTF-8**; se falhar, reprocessa automaticamente forçando Latin-1. Isso garante a integridade dos nomes das operadoras no Dashboard final.

### 3. API e Backend
* **FastAPI vs Flask:** Escolhi FastAPI pela validação nativa de dados (Pydantic), performance assíncrona (ASGI) e geração automática do Swagger, acelerando o desenvolvimento e a documentação.

* **Paginação:** Implementada via `Limit/Offset`. Para o volume atual de dados (~700 operadoras ativas), essa abordagem é simples e eficiente, evitando complexidade desnecessária no Frontend.

### 4. Interface Web (Frontend)
* **Vue.js 3:** Escolhido pela reatividade e performance.

* **Chart.js:** Utilizado para renderizar o gráfico das "Top 10 Despesas", oferecendo uma visualização clara para tomada de decisão executiva.

---

## 🔮 Melhorias Futuras (Next Steps)
Dado mais tempo para evolução do produto, os próximos passos seriam:

**1. Testes Automatizados:** Implementação de `pytest` para cobrir as regras de negócio do ETL (cálculo de média e desvio padrão) e Mocks para testar o Scraper sem depender da disponibilidade do site da ANS.

**2. Orquestração Profissional:** Migração do script `main.py` para Apache Airflow ou Prefect, permitindo agendamento diário e monitoramento visual de falhas no pipeline.

**3. CI/CD:** Configuração de GitHub Actions para linting e testes a cada Push.

---

## 👨‍💻 Autor
### Marcelo Augusto