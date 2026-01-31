import pandas as pd
import os

# Caminho do arquivo processado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "../../data/processed/consolidado_despesas.csv")

def validate_output():
    print("--- 🧐 VALIDANDO DADOS CONSOLIDADOS ---")
    
    if not os.path.exists(FILE_PATH):
        print("❌ Arquivo não encontrado!")
        return

    # Lê o arquivo usando o mesmo separador que usamos para salvar (;)
    df = pd.read_csv(FILE_PATH, sep=';', decimal=',')
    
    print(f"📊 Total de linhas: {len(df)}")
    print(f"🗂️ Colunas: {list(df.columns)}")
    print("-" * 50)
    
    # 1. Checagem de "Nulls" (Valores vazios)
    print("🔍 Checando valores nulos:")
    print(df.isnull().sum())
    print("-" * 50)

    # 2. Amostragem (Mostra 5 linhas aleatórias para vermos o conteúdo real)
    print("🎲 Amostra Aleatória (5 registros):")
    # Configura o pandas para mostrar o texto completo da descrição
    pd.set_option('display.max_colwidth', None) 
    print(df.sample(5)[['Ano', 'Trimestre', 'DESCRICAO', 'ValorDespesas']])
    
    print("-" * 50)
    # 3. Validação Lógica: Será que pegamos mesmo só Eventos/Sinistros?
    # Vamos ver se tem alguma descrição que NÃO parece despesa
    filtro_estranho = ~df['DESCRICAO'].str.contains('EVENTO|SINISTRO', case=False, na=False)
    estranhos = df[filtro_estranho]
    
    if not estranhos.empty:
        print(f"⚠️ AVISO: Encontramos {len(estranhos)} linhas que não citam Evento/Sinistro explicitamente.")
        print(estranhos.head(2))
    else:
        print("✅ Todas as descrições contêm 'Evento' ou 'Sinistro'.")

if __name__ == "__main__":
    validate_output()