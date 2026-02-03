import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configurações do Banco
# IMPORTANTE: No Docker, o host é 'db'. Localmente, é 'localhost'.
DB_USER = os.getenv("DB_USER", "user_ans")
DB_PASS = os.getenv("DB_PASS", "password_ans")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ans_database")

# String de Conexão
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/processed")
FILE_OPERADORAS = os.path.join(DATA_DIR, "agregado_operadoras.csv")
FILE_DETALHADA = os.path.join(DATA_DIR, "despesas_enriquecidas.csv")

def get_engine():
    try:
        return create_engine(DATABASE_URL)
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return None

def create_tables(engine):
    print("🛠️  Verificando/Criando tabelas...")
    sql_create = """
    CREATE TABLE IF NOT EXISTS operadoras (
        registro_ans TEXT PRIMARY KEY,
        cnpj TEXT,
        razao_social TEXT
    );
    CREATE TABLE IF NOT EXISTS despesas_detalhadas (
        id SERIAL PRIMARY KEY,
        registro_ans TEXT REFERENCES operadoras(registro_ans),
        ano INT,
        trimestre INT,
        descricao TEXT,
        valor_despesa NUMERIC(15,2)
    );
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

def load_data(full_refresh=True):
    """
    Carrega dados para o banco.
    :param full_refresh: Se True, limpa as tabelas antes de inserir.
    """
    print(f"--- 🐘 Iniciando Carga (Modo Full Refresh: {full_refresh}) ---")
    
    engine = get_engine()
    if not engine: return

    create_tables(engine)

    # Limpeza (Truncate)
    if full_refresh:
        print("🧹 Limpando tabelas antigas...")
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE operadoras, despesas_detalhadas, despesas_agregadas CASCADE;"))
            conn.commit()

    # 1. Carga de Operadoras e Despesas
    if os.path.exists(FILE_DETALHADA):
        print("📥 Carregando Despesas Detalhadas...")
        # Lendo com encoding UTF-8 (padrão do Python ao salvar)
        df_det = pd.read_csv(FILE_DETALHADA, sep=';', decimal=',')
        
        # A. Operadoras
        df_ops = df_det[['RegistroANS', 'CNPJ', 'RazaoSocial']].drop_duplicates('RegistroANS').copy()
        df_ops.columns = ['registro_ans', 'cnpj', 'razao_social']
        try:
            df_ops.to_sql('operadoras', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        except Exception:
            pass # Se já existe, ignora (em full_refresh não deve acontecer)

        # B. Despesas
        df_desp = df_det[['RegistroANS', 'Ano', 'Trimestre', 'DESCRICAO', 'ValorDespesas']].copy()
        df_desp.columns = ['registro_ans', 'ano', 'trimestre', 'descricao', 'valor_despesa']
        df_desp.to_sql('despesas_detalhadas', engine, if_exists='append', index=False, chunksize=1000)
    
    # 2. Carga de Agregados
    if os.path.exists(FILE_OPERADORAS):
        print("📥 Carregando Dados Agregados...")
        df_agg = pd.read_csv(FILE_OPERADORAS, sep=';', decimal=',')
        df_agg.columns = ['razao_social', 'uf', 'total_despesas', 'media_trimestral', 'desvio_padrao']
        df_agg.to_sql('despesas_agregadas', engine, if_exists='append', index=False)

    print("🏁 Carga concluída com sucesso.")

if __name__ == "__main__":
    load_data(full_refresh=True)

