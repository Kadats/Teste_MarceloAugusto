import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FILE_DESPESAS = os.path.join(PROCESSED_DIR, "consolidado_despesas.csv")

# URL oficial da ANS
URL_BASE_CADOP = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"

def get_cadop_url():
    """Entra na página e descobre o nome real do arquivo CSV"""
    try:
        print(f"🔎 Buscando arquivo em: {URL_BASE_CADOP}")
        response = requests.get(URL_BASE_CADOP)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and href.lower().endswith('.csv'):
                print(f"   ✅ Arquivo encontrado: {href}")
                return f"{URL_BASE_CADOP}{href}"
                
        print("❌ Nenhum CSV encontrado na página do Cadop.")
        return None
    except Exception as e:
        print(f"❌ Erro ao acessar página do Cadop: {e}")
        return None

def download_cadop():
    target_url = get_cadop_url()
    if not target_url: return None

    filename = target_url.split('/')[-1]
    local_path = os.path.join(RAW_DIR, filename)
    
    if os.path.exists(local_path):
        print(f"📂 Arquivo já existe em cache: {filename}")
        return local_path

    print(f"📥 Baixando {filename}...")
    try:
        r = requests.get(target_url, stream=True)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Download concluído.")
        return local_path
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None

def validar_cnpj(cnpj):
    """Valida CNPJ (Algoritmo Módulo 11)"""
    # Remove tudo que não é dígito
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    
    # Validações básicas de tamanho e sequência repetida
    if len(cnpj) != 14 or cnpj == cnpj[0] * len(cnpj):
        return False

    def calc_digito(doc, pesos):
        soma = sum(int(d) * p for d, p in zip(doc, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    if calc_digito(cnpj[:12], pesos1) != int(cnpj[12]):
        return False
    if calc_digito(cnpj[:13], pesos2) != int(cnpj[13]):
        return False
    return True

def run_transformation():
    print("--- 🔄 Iniciando Transformação e Enriquecimento ---")
    
    if not os.path.exists(FILE_DESPESAS):
        print("❌ Erro: Arquivo de despesas não encontrado.")
        return

    # 1. Carrega Despesas
    print("📖 Lendo arquivo de despesas...")
    df_despesas = pd.read_csv(FILE_DESPESAS, sep=';', decimal=',')
    
    # 2. Carrega Cadop
    cadop_path = download_cadop()
    if not cadop_path: return

    print("📖 Lendo Cadastro de Operadoras...")
    # Tenta ler ignorando erros de linha ruim (comum em arquivos gov)
    try:
        df_cadop = pd.read_csv(cadop_path, sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')
    except:
        df_cadop = pd.read_csv(cadop_path, encoding='latin1', dtype=str, on_bad_lines='skip')
    
    # Normaliza nomes das colunas (remove espaços e poe em maiúsculo)
    df_cadop.columns = [c.strip().upper() for c in df_cadop.columns]
    
    # --- CORREÇÃO DO MAPEAMENTO ---
    # Agora usamos os nomes exatos que vimos no debug
    print(f"   Colunas do Cadop: {list(df_cadop.columns)[:5]}...")
    
    map_cols = {}
    
    # Busca explícita pelas colunas certas
    if 'REGISTRO_OPERADORA' in df_cadop.columns:
        map_cols['RegistroANS'] = 'REGISTRO_OPERADORA'
    
    if 'CNPJ' in df_cadop.columns:
        map_cols['CNPJ'] = 'CNPJ'
        
    if 'RAZAO_SOCIAL' in df_cadop.columns:
        map_cols['RazaoSocial'] = 'RAZAO_SOCIAL'
    
    # A UF as vezes vem como 'UF' ou 'SIGLA_UF' ou dentro do endereço
    col_uf = next((c for c in df_cadop.columns if c == 'UF' or c == 'SIGLA_UF'), None)
    if col_uf:
        map_cols['UF'] = col_uf

    print(f"   Mapeamento definido: {map_cols}")

    if 'RegistroANS' not in map_cols:
        print("❌ ERRO CRÍTICO: Não foi possível identificar a coluna REGISTRO_OPERADORA.")
        return

    # Seleciona e renomeia
    df_cadop = df_cadop[list(map_cols.values())].rename(columns={v: k for k, v in map_cols.items()})
    
    print("⚙️  Normalizando tipos para o JOIN...")
    
    # Converte ambos para string pura, removendo .0 se houver (ex: '123.0' vira '123')
    df_despesas['RegistroANS'] = df_despesas['RegistroANS'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    df_cadop['RegistroANS'] = df_cadop['RegistroANS'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

    # 3. JOIN
    print("🔗 Realizando o Cruzamento (Left Join)...")
    df_merged = pd.merge(df_despesas, df_cadop, on='RegistroANS', how='left')
    
    # 4. Validação
    print("🕵️ Validando CNPJs...")
    df_merged['CNPJ_Valido'] = df_merged['CNPJ'].apply(lambda x: validar_cnpj(x) if pd.notna(x) else False)
    
    # Estatísticas
    total = len(df_merged)
    validos = df_merged[df_merged['CNPJ_Valido'] == True]
    invalidos = df_merged[df_merged['CNPJ_Valido'] == False]
    
    print("-" * 30)
    print(f"📊 RESULTADO FINAL:")
    print(f"   Total de Linhas: {total}")
    print(f"   ✅ CNPJs Válidos (Match ok): {len(validos)}")
    print(f"   ❌ Inválidos ou Sem Match: {len(invalidos)}")
    
    # Salva Válidos
    file_validos = os.path.join(PROCESSED_DIR, "despesas_enriquecidas.csv")
    validos.drop(columns=['CNPJ_Valido']).to_csv(file_validos, index=False, sep=';', decimal=',')
    
    # Salva Inválidos (Relatório de Inconsistência)
    file_erros = os.path.join(PROCESSED_DIR, "inconsistencias.csv")
    invalidos.to_csv(file_erros, index=False, sep=';', decimal=',')
    
    print(f"\n📂 Arquivos gerados em {PROCESSED_DIR}")

if __name__ == "__main__":
    run_transformation()