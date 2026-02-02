import pandas as pd
import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
INPUT_FILE = os.path.join(DATA_DIR, "processed/despesas_enriquecidas.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "processed/agregado_operadoras.csv")

def run_aggregation():
    print("--- 📊 Iniciando Agregação Estatística (Tarefa 2.3) ---")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ Erro: Arquivo enriquecido não encontrado. Rode o transformer.py antes.")
        return

    # 1. Carregamento
    print("📖 Lendo dados enriquecidos...")
    # Importante: decimal=',' pois salvamos assim no passo anterior
    df = pd.read_csv(INPUT_FILE, sep=';', decimal=',')
    
    # Garante que ValorDespesas é numérico
    df['ValorDespesas'] = pd.to_numeric(df['ValorDespesas'], errors='coerce').fillna(0)

    # 2. Agrupamento Intermediário (Por Trimestre)
    # Primeiro somamos quanto cada empresa gastou EM CADA trimestre/ano
    print("🧮 Calculando totais por trimestre...")
    df_trimestral = df.groupby(['RazaoSocial', 'UF', 'Ano', 'Trimestre'])['ValorDespesas'].sum().reset_index()
    
    # 3. Agregação Final (Estatísticas por Operadora)
    # Agora calculamos a média e desvio padrão baseados nos trimestres
    print("📉 Calculando estatísticas finais (Média e Desvio Padrão)...")
    
    df_final = df_trimestral.groupby(['RazaoSocial', 'UF'])['ValorDespesas'].agg(
        TotalDespesas='sum',
        MediaTrimestral='mean',
        DesvioPadrao='std'
    ).reset_index()

    # 4. Tratamento de Nulos (Trade-off acordado)
    # Se a empresa só tem dados de 1 trimestre, o desvio padrão é NaN.
    # Decisão: Substituir por 0.0
    nulos_antes = df_final['DesvioPadrao'].isna().sum()
    df_final['DesvioPadrao'] = df_final['DesvioPadrao'].fillna(0.0)
    
    # 5. Formatação e Ordenação
    # Arredondar para 2 casas decimais
    cols_numericas = ['TotalDespesas', 'MediaTrimestral', 'DesvioPadrao']
    df_final[cols_numericas] = df_final[cols_numericas].round(2)
    
    # Ordenar pelas que mais gastaram (Fica mais bonito no relatório)
    df_final.sort_values(by='TotalDespesas', ascending=False, inplace=True)

    # 6. Salvamento
    df_final.to_csv(OUTPUT_FILE, index=False, sep=';', decimal=',')
    
    print("-" * 30)
    print(f"✅ Agregação Concluída!")
    print(f"📄 Arquivo gerado: {OUTPUT_FILE}")
    print(f"📊 Total de Operadoras Agrupadas: {len(df_final)}")
    print(f"🛠️  Desvios Padrão corrigidos (NaN -> 0): {nulos_antes}")
    
    # Preview
    print("\n🏆 Top 3 Operadoras com maiores despesas:")
    print(df_final.head(3).to_string(index=False))

if __name__ == "__main__":
    run_aggregation()

