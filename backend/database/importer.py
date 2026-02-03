import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configurações do Banco (Iguais ao docker-compose)
DB_USER = "user_ans"
DB_PASS = "password_ans"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5432"
DB_NAME = "ans_database"

# String de Conexão (SQLAlchemy)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Caminhos dos CSVs processados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/processed")
FILE_OPERADORAS = os.path.join(DATA_DIR, "agregado_operadoras.csv") # Dados agregados
FILE_DETALHADA = os.path.join(DATA_DIR, "despesas_enriquecidas.csv") # Dados brutos

def create_tables(engine):
    print("🛠️  Criando tabelas no Banco de Dados...")
    
    # SQL DDL (Data Definition Language)
    # Criar tabelas separadas para normalizar os dados
    sql_create = """
    -- Tabela de Operadoras (Dimensão)
    CREATE TABLE IF NOT EXISTS operadoras (
        registro_ans TEXT PRIMARY KEY,
        cnpj TEXT,
        razao_social TEXT
    );

    -- Tabela de Despesas Detalhadas (Fatos)
    CREATE TABLE IF NOT EXISTS despesas_detalhadas (
        id SERIAL PRIMARY KEY,
        registro_ans TEXT REFERENCES operadoras(registro_ans),
        ano INT,
        trimestre INT,
        descricao TEXT,
        valor_despesa NUMERIC(15,2)
    );
    
    -- Tabela de Agregados (Para consultas rápidas/Dashboards)
    CREATE TABLE IF NOT EXISTS despesas_agregadas (
        id SERIAL PRIMARY KEY,
        razao_social TEXT,
        uf TEXT,
        total_despesas NUMERIC(15,2),
        media_trimestral NUMERIC(15,2),
        desvio_padrao NUMERIC(15,2)
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql_create))
        conn.commit()

def load_data():
    print("--- 🐘 Iniciando Carga no PostgreSQL ---")
    
    # 1. Conexão
    try:
        engine = create_engine(DATABASE_URL)
        create_tables(engine)
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        print("Dica: Verifique se o Docker está rodando (docker ps).")
        return

    # 2. Carregar Despesas Detalhadas (Aprox 170k linhas)
    if os.path.exists(FILE_DETALHADA):
        print("📖 Lendo CSV detalhado...")
        df_det = pd.read_csv(FILE_DETALHADA, sep=';', decimal=',')
        
        # A. Primeiro povoar a tabela de Operadoras (para não dar erro de chave estrangeira)
        print("📥 Inserindo Operadoras únicas...")
        df_ops = df_det[['RegistroANS', 'CNPJ', 'RazaoSocial']].drop_duplicates('RegistroANS')
        
        # Renomear colunas para bater com o banco
        df_ops.columns = ['registro_ans', 'cnpj', 'razao_social']
        
        # if_exists='append' adiciona, 'replace' apaga e recria. 
        # Usamos append mas precisamos garantir que não duplique (idealmente limparíamos antes)
        # Para o teste, vamos limpar as tabelas antes de inserir
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE operadoras, despesas_detalhadas, despesas_agregadas CASCADE;"))
            conn.commit()
            
        df_ops.to_sql('operadoras', engine, if_exists='append', index=False, chunksize=1000)
        
        # B. Inserir Despesas
        print("📥 Inserindo Despesas Detalhadas (pode demorar um pouco)...")
        df_insert = df_det[['RegistroANS', 'Ano', 'Trimestre', 'DESCRICAO', 'ValorDespesas']].copy()
        df_insert.columns = ['registro_ans', 'ano', 'trimestre', 'descricao', 'valor_despesa']
        
        df_insert.to_sql('despesas_detalhadas', engine, if_exists='append', index=False, chunksize=1000)
        print(f"   ✅ {len(df_insert)} despesas inseridas.")
        
    else:
        print("⚠️ Arquivo de despesas detalhadas não encontrado.")

    # 3. Carregar Agregados (Tarefa 2.3)
    if os.path.exists(FILE_OPERADORAS):
        print("📖 Lendo CSV agregado...")
        df_agg = pd.read_csv(FILE_OPERADORAS, sep=';', decimal=',')
        
        # Renomear colunas
        map_cols = {
            'RazaoSocial': 'razao_social',
            'UF': 'uf',
            'TotalDespesas': 'total_despesas',
            'MediaTrimestral': 'media_trimestral',
            'DesvioPadrao': 'desvio_padrao'
        }
        df_agg.rename(columns=map_cols, inplace=True)
        
        print("📥 Inserindo Tabela Agregada...")
        df_agg.to_sql('despesas_agregadas', engine, if_exists='append', index=False)
        print(f"   ✅ {len(df_agg)} registros agregados inseridos.")

    print("-" * 30)
    print("🏁 Sucesso! O banco de dados está populado.")

if __name__ == "__main__":
    load_data()

