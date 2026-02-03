# Teste Técnico - Intuitive Care

## Autor
**Nome:** Marcelo Augusto
**Status:** Em desenvolvimento

## Como Executar

### Pré-requisitos
- Python 3.12+
- Docker (Opcional)

### Instalação e Execução
1. Clone o repositório.
2. Acesse a pasta `backend` e configure o ambiente:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

## Decisões Técnicas (Trade-offs)

### 1. Coleta de Dados (Scraper)

* **Escolha da Biblioteca: `BeautifulSoup` vs `Selenium`**
    * **Decisão:** Utilizei `BeautifulSoup` + `requests`.
    * **Justificativa:** O site da ANS é estático (não depende de JavaScript para carregar os arquivos). O `BeautifulSoup` é muito mais leve e rápido, consumindo menos recursos da máquina do que abrir um navegador simulado com Selenium. Isso torna o processo de coleta mais eficiente.

* **Estratégia de Processamento: Disco vs Memória**
    * **Decisão:** Baixar os arquivos ZIP para o disco (`data/raw`) antes de processar.
    * **Justificativa:** Arquivos contábeis podem ser grandes. Tentar baixar, descompactar e ler tudo na memória RAM simultaneamente poderia travar o sistema (estouro de memória). Salvar em disco cria um *checkpoint*: se o processamento falhar, não precisamos baixar tudo novamente, garantindo maior resiliência.

### 2. Processamento e Consolidação (ETL)

* **Abordagem de Resiliência:**
    * Em vez de assumir nomes de arquivos fixos (ex: `1T2025.csv`), implementei uma inspeção automática do conteúdo dos arquivos ZIP.
    * O script abre os arquivos em memória, verifica as primeiras linhas e identifica as colunas chave (`DATA`, `DESCRICAO`, `VL_SALDO_FINAL`) para decidir qual arquivo processar.
    * Isso torna o sistema capaz de lidar com arquivos `.csv`, `.txt` ou `.xlsx` automaticamente.

* **Filtros Aplicados:**
    * Filtragem de linhas onde a coluna `DESCRICAO` contém os termos "EVENTO" ou "SINISTRO" (Case Insensitive), conforme solicitado no desafio.

* **⚠️ Inconsistência Detectada (Análise Crítica):**
    * **Problema:** Os arquivos de Demonstrações Contábeis da ANS (fonte 1.1) **não contêm** as colunas `CNPJ` ou `Razão Social`, apenas o código `REG_ANS`.
    * **Solução Adotada:** Para manter a integridade do teste, realizei a consolidação mantendo a coluna `RegistroANS`.
    * **Próximo Passo:** O enriquecimento com CNPJ e Razão Social será feito na etapa 2.2, através do cruzamento (Join) com a base de Dados Cadastrais das Operadoras.

### 3. Transformação e Enriquecimento de Dados

* **Estratégia de Join (Desafio Técnico):**
    * O PDF solicita o cruzamento por `CNPJ`. No entanto, como a fonte primária (Demonstrações Contábeis) não possui CNPJ, utilizei o `RegistroANS` (código único da operadora) como chave de ligação (`Join Key`).
    * Identifiquei e tratei divergências de tipagem (`int` vs `string`) e nomes de colunas dinâmicos (`REGISTRO_OPERADORA` vs `DATA_REGISTRO`) através de inspeção automática.

* **Validação e Tratamento de Qualidade (Data Quality):**
    * **Validação:** Implementei o algoritmo de *Módulo 11* para verificar a validade matemática dos CNPJs após o enriquecimento.
    * **Estratégia de "Quarentena" (Trade-off):**
        * *Decisão:* Ao invés de descartar registros com CNPJs inválidos ou sem correspondência no cadastro, optei por **separar os dados**.
        * *Fluxo:*
            * ✅ Dados Válidos -> `data/processed/despesas_enriquecidas.csv` (Seguem para análise).
            * ❌ Dados Inválidos -> `data/processed/inconsistencias.csv` (Seguem para auditoria).
        * *Justificativa:* Em um contexto financeiro, descartar despesas apenas por erro cadastral geraria relatórios contábeis imprecisos (falso positivo de lucro). A segregação permite a continuidade da análise sem perder o rastro das inconsistências.

### 4. Agregação e Análise Estatística

* **Granularidade:**
    * A agregação foi realizada em dois níveis: primeiro somando as despesas por trimestre (visão temporal), e posteriormente calculando a média e desvio padrão por operadora (visão consolidada).

* **Tratamento de Desvio Padrão (Trade-off Matemático):**
    * **Problema:** Operadoras que possuem registro em apenas um trimestre resultam em `NaN` (Not a Number) ao calcular o desvio padrão (pois não há variância com um único ponto de dados).
    * **Decisão:** Substituir esses valores `NaN` por `0.0`.
    * **Justificativa:** Para fins de exibição no Frontend e armazenamento no Banco de Dados, `0.0` representa corretamente que "não houve variação registrada", evitando erros de tipagem ou valores nulos que quebrariam a interface.

### 5. Banco de Dados e Persistência

* **Escolha do SGBD:**
    * **Tecnologia:** PostgreSQL 15 (via Docker).
    * **Justificativa:** O PostgreSQL é robusto, suporta nativamente tipos numéricos precisos (`NUMERIC`) para dados financeiros e possui excelente integração com Python/SQLAlchemy.
    * **Infraestrutura:** Utilizei o **Docker Compose** para orquestrar o banco. Isso garante que qualquer pessoa que clone o repositório consiga subir o ambiente com um único comando (`docker compose up`), sem precisar instalar o Postgres localmente no sistema operacional, mantendo o ambiente de desenvolvimento limpo.

* **Estratégia de Carga de Dados (Data Loading):**
    * **Trade-off: Full Refresh vs. Incremental:**
        * Optei pela estratégia de **Carga Total (Full Refresh)** com `TRUNCATE` antes da inserção.
        * **Justificativa:** Para o escopo deste teste, garantir a consistência e a idempotência (poder rodar o script várias vezes e ter o mesmo resultado) é prioritário. Uma carga incremental exigiria verificação linha a linha (Upsert), o que adicionaria complexidade de processamento desnecessária dado o volume de dados (~170k registros).

* **Modelagem:**
    * Criei três tabelas para atender aos requisitos:
        1.  `operadoras`: Tabela dimensional (Dados cadastrais únicos).
        2.  `despesas_detalhadas`: Tabela de fatos (Transações linha a linha).
        3.  `despesas_agregadas`: Tabela de performance (Pré-calculada para consultas rápidas de Dashboards).

### 6. Consultas Analíticas (SQL)

* **Abordagem:**
    * As consultas solicitadas na Tarefa 3.1 foram consolidadas no arquivo `backend/database/queries.sql`.
    * O arquivo contém queries que demonstram:
        1.  **JOINs:** Cruzamento entre fatos (despesas) e dimensões (operadoras).
        2.  **Agregações:** Uso de `SUM`, `AVG`, `COUNT` e `GROUP BY`.
        3.  **Performance:** Utilização da tabela pré-calculada `despesas_agregadas` para análises geográficas (UF), reduzindo a carga de processamento no banco.

