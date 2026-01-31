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