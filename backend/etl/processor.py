import os
import zipfile
import pandas as pd
import io

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "../../data/raw")

def inspect_zips():
    print(f"--- 🕵️ INSPECIONANDO CONTEÚDO (Lendo cabeçalhos) ---")
    
    if not os.path.exists(RAW_DIR):
        print("❌ Erro: Pasta data/raw não encontrada.")
        return

    zip_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.zip')]
    
    for zip_name in zip_files:
        print(f"\n📦 ZIP: {zip_name}")
        full_path = os.path.join(RAW_DIR, zip_name)
        
        try:
            with zipfile.ZipFile(full_path, 'r') as z:
                files_inside = z.namelist()
                
                for file in files_inside:
                    # Ignora pastas ou arquivos que não sejam dados (csv, txt)
                    if not (file.lower().endswith('.csv') or file.lower().endswith('.txt')):
                        continue
                        
                    print(f"   └── 📄 Lendo: {file}")
                    
                    try:
                        # Abre o arquivo direto da memória (sem descompactar no disco)
                        with z.open(file) as f:
                            # Tenta ler as primeiras 3 linhas para ver a cara dos dados
                            # ANS costuma usar encoding latin1 (cp1252) e separador ponto-e-vírgula
                            df_preview = pd.read_csv(
                                f, 
                                sep=';',          # Tentativa comum da ANS
                                encoding='latin1', # Encoding padrão de órgãos gov.br
                                nrows=3            # Só precisamos ver o topo
                            )
                            
                            # Mostra as colunas encontradas
                            cols = list(df_preview.columns)
                            print(f"       📊 Colunas detectadas: {cols}")
                            
                            # Verifica se tem cara de ser o arquivo certo (pelas colunas)
                            # Geralmente procuramos: 'CD_CONTA_CONTABIL', 'DESCRICAO', 'VL_SALDO_FINAL'
                            termos_chave = ['conta', 'descri', 'saldo', 'despesa']
                            tem_termo = any(t in str(cols).lower() for t in termos_chave)
                            
                            if tem_termo:
                                print(f"       ✅ PARECE SER O ARQUIVO CONTÁBIL!")
                            else:
                                print(f"       ⚠️ Colunas estranhas. Talvez separador errado?")
                                
                    except Exception as e:
                        print(f"       ❌ Erro ao ler CSV (encoding/sep?): {e}")

        except Exception as e:
            print(f"   ❌ Erro ao abrir zip: {e}")

if __name__ == "__main__":
    inspect_zips()