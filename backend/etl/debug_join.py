import pandas as pd
import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DESPESAS = os.path.join(BASE_DIR, "../../data/processed/consolidado_despesas.csv")
FILE_CADOP = os.path.join(BASE_DIR, "../../data/raw/Relatorio_cadop.csv") # Nome que baixou no seu print

def debug_keys():
    print("--- 🕵️ INVESTIGAÇÃO DO JOIN (RAIO-X) ---")
    
    # 1. Analisa Despesas (Lado Esquerdo do Join)
    print(f"\n1. ARQUIVO DESPESAS ({FILE_DESPESAS})")
    try:
        df_desp = pd.read_csv(FILE_DESPESAS, sep=';', decimal=',')
        print(f"   Colunas encontradas: {list(df_desp.columns)}")
        if 'RegistroANS' in df_desp.columns:
            exemplo = df_desp['RegistroANS'].iloc[0]
            print(f"   Amostra (Valor Puro): '{exemplo}'")
            print(f"   Tipo do Dado (dtype): {df_desp['RegistroANS'].dtype}")
        else:
            print("   ❌ ERRO: Coluna 'RegistroANS' não existe aqui!")
    except Exception as e:
        print(f"   Erro ao ler: {e}")

    # 2. Analisa Cadop (Lado Direito do Join)
    print(f"\n2. ARQUIVO CADOP ({FILE_CADOP})")
    try:
        # Tenta ler como o transformer leu
        df_cadop = pd.read_csv(FILE_CADOP, sep=';', encoding='latin1', dtype=str)
        
        # Limpa nomes das colunas para facilitar leitura
        df_cadop.columns = [c.strip().upper() for c in df_cadop.columns]
        print(f"   Colunas encontradas (Primeiras 5): {list(df_cadop.columns)[:5]}")
        
        # Tenta achar a coluna de Registro
        col_reg = next((c for c in df_cadop.columns if 'REGISTRO' in c and 'ANS' in c), None)
        
        if col_reg:
            print(f"   ✅ Coluna de Registro identificada como: '{col_reg}'")
            exemplo = df_cadop[col_reg].iloc[0]
            print(f"   Amostra (Valor Puro): '{exemplo}'")
            print(f"   Tipo do Dado: {df_cadop[col_reg].dtype}")
        else:
            print("   ❌ ERRO: Nenhuma coluna parecida com 'Registro ANS' encontrada.")
            print("   DICA: Verifique se o separador ';' funcionou (se as colunas não estão todas juntas).")

    except Exception as e:
        print(f"   Erro ao ler: {e}")

if __name__ == "__main__":
    debug_keys()