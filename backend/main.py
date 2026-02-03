import sys
import os

# Adiciona o diretório atual ao path para garantir que o Python encontre os módulos 'etl' e 'database'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl import scraper, consolidator, transformer, aggregator
from database import importer

def main_pipeline():
    print("\n" + "="*50)
    print("🚀 INICIANDO PIPELINE DE DADOS - INTUITIVE CARE")
    print("="*50 + "\n")

    try:
        # Passo 1: Coleta
        print(">>> [1/5] Executando Scraper (Download)...")
        scraper.main_scraper()
        
        # Passo 2: Consolidação (Extração e Limpeza)
        print("\n>>> [2/5] Executando Consolidação...")
        consolidator.consolidate_data()
        
        # Passo 3: Transformação (Enriquecimento e Validação)
        print("\n>>> [3/5] Executando Transformação...")
        transformer.run_transformation()
        
        # Passo 4: Agregação (Cálculos Estatísticos)
        print("\n>>> [4/5] Executando Agregação Estatística...")
        aggregator.run_aggregation()
        
        # Passo 5: Carga no Banco
        print("\n>>> [5/5] Carga no Banco de Dados (PostgreSQL)...")
        # full_refresh=True garante que limpamos o banco antes de inserir para evitar duplicatas
        importer.load_data(full_refresh=True)

        print("\n" + "="*50)
        print("✅ SUCESSO! Pipeline finalizado.")
        print("📊 Banco de dados populado e pronto para a API.")
        print("="*50)

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NO PIPELINE: {e}")
        # Encerra com código de erro 1 para o Docker saber que falhou
        sys.exit(1)

if __name__ == "__main__":
    main_pipeline()

