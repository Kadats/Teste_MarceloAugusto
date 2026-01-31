import os
import zipfile
import pandas as pd
import re

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "../../data/raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "../../data/processed")

# Termos para filtrar "Despesas com Eventos/Sinistros"
# A classe 4 no plano de contas da ANS geralmente é despesa assistencial
TERMOS_FILTRO = ["EVENTO", "SINISTRO"]

def setup_directories():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

def process_file_content(f, filename, file_ext):
    """Lê o arquivo (CSV ou Excel) e retorna um DataFrame filtrado"""
    try:
        # Define parâmetros de leitura baseados na nossa inspeção
        # A ANS usa pt-br: decimal com vírgula, milhar com ponto
        if 'csv' in file_ext or 'txt' in file_ext:
            df = pd.read_csv(f, sep=';', encoding='latin1', thousands='.', decimal=',')
        else: # Excel
            df = pd.read_excel(f)

        # Normaliza nomes de colunas (tudo maiúsculo para evitar erro 'Descricao' vs 'DESCRICAO')
        df.columns = [c.upper().strip() for c in df.columns]

        # Verifica se tem as colunas essenciais
        required_cols = ['DATA', 'REG_ANS', 'DESCRICAO', 'VL_SALDO_FINAL']
        if not all(col in df.columns for col in required_cols):
            return None

        # --- FILTRO 1: Linhas que contenham EVENTO ou SINISTRO na descrição ---
        # Regex: Procura qualquer um dos termos ignorando maiúsculas/minúsculas
        regex_termo = '|'.join(TERMOS_FILTRO)
        df_filtered = df[df['DESCRICAO'].str.contains(regex_termo, case=False, na=False)].copy()

        # Se sobrou dado, adiciona metadados
        if not df_filtered.empty:
            # Extrai Ano e Trimestre da coluna DATA (formato YYYY-MM-DD ou similar)
            df_filtered['DATA'] = pd.to_datetime(df_filtered['DATA'], errors='coerce')
            df_filtered['Ano'] = df_filtered['DATA'].dt.year
            df_filtered['Trimestre'] = df_filtered['DATA'].dt.quarter
            
            # Nota: Usamos REG_ANS temporariamente pois não temos CNPJ ainda
            df_filtered.rename(columns={
                'REG_ANS': 'RegistroANS', 
                'VL_SALDO_FINAL': 'ValorDespesas'
            }, inplace=True)
            
            # Seleciona apenas o que interessa
            cols_final = ['RegistroANS', 'Ano', 'Trimestre', 'DESCRICAO', 'ValorDespesas']
            return df_filtered[cols_final]
            
        return None

    except Exception as e:
        print(f"   ❌ Erro ao processar {filename}: {e}")
        return None

def consolidate_data():
    setup_directories()
    print("--- 🚀 Iniciando Consolidação de Dados ---")
    
    all_data = []
    
    zip_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.zip')]
    
    for zip_name in zip_files:
        print(f"📦 Processando: {zip_name}")
        zip_path = os.path.join(RAW_DIR, zip_name)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for file in z.namelist():
                    # Aceita CSV, TXT e XLSX agora!
                    ext = file.split('.')[-1].lower()
                    if ext not in ['csv', 'txt', 'xlsx', 'xls']:
                        continue
                        
                    print(f"   📄 Lendo: {file}")
                    with z.open(file) as f:
                        df_part = process_file_content(f, file, ext)
                        if df_part is not None:
                            print(f"      ✅ Dados extraídos: {len(df_part)} linhas")
                            all_data.append(df_part)
                        else:
                            print(f"      ⚠️ Ignorado (Sem colunas ou dados relevantes)")
                            
        except Exception as e:
            print(f"❌ Erro crítico no zip {zip_name}: {e}")

    # Consolidação Final
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        
        # Tratamento de Inconsistências (Solicitado no PDF 1.3)
        # 1. Valores negativos? (Despesas costumam ser negativas contabilmente ou positivas?)
        # Vamos assumir que queremos o valor absoluto para análise, ou mantemos original.
        # Por enquanto, mantemos original.
        
        output_csv = os.path.join(PROCESSED_DIR, "consolidado_despesas.csv")
        df_final.to_csv(output_csv, index=False, sep=';', decimal=',')
        
        print("-" * 30)
        print(f"✅ SUCESSO! Arquivo gerado: {output_csv}")
        print(f"📊 Total de Registros: {len(df_final)}")
        print(f"⚠️ Nota: As colunas CNPJ e RazaoSocial não constam na fonte. Usamos 'RegistroANS'.")
    else:
        print("❌ Nenhum dado foi consolidado.")

if __name__ == "__main__":
    consolidate_data()