import os
import requests
from bs4 import BeautifulSoup
import re

# Configurações baseadas na sua navegação visual
BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
OUTPUT_DIR = "../data/raw"

def setup_directories():
    """Garante que a pasta de download existe"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def get_soup(url):
    """Função auxiliar para baixar e fazer o parse do HTML"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def download_file(url, filename):
    """Baixa o arquivo salvando na pasta data/raw"""
    local_path = os.path.join(OUTPUT_DIR, filename)
    
    # Se o arquivo já existe, pula (bom para testes repetidos)
    if os.path.exists(local_path):
        print(f"Arquivo já existe: {filename}")
        return local_path

    print(f"Baixando {filename}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Sucesso: {local_path}")
        return local_path
    except Exception as e:
        print(f"Falha no download de {url}: {e}")
        return None

def main_scraper():
    setup_directories()
    print("Iniciando scraper dos dados da ANS...")
    
    # 1. Acessa a raiz para listar os Anos
    soup = get_soup(BASE_URL)
    if not soup:
        return

    # Pega links que parecem anos (4 dígitos + barra)
    links = [a.get('href') for a in soup.find_all('a') if a.get('href')]
    anos = sorted([l.strip('/') for l in links if re.match(r'^\d{4}/$', l)], reverse=True)
    
    arquivos_baixados = []
    
    # 2. Itera pelos anos (do mais recente para o antigo)
    for ano in anos:
        if len(arquivos_baixados) >= 3:
            break
            
        print(f"Verificando ano {ano}...")
        url_ano = f"{BASE_URL}{ano}/"
        soup_ano = get_soup(url_ano)
        
        if not soup_ano:
            continue

        # 3. Pega os ZIPs dentro do ano
        links_arquivos = [a.get('href') for a in soup_ano.find_all('a') if a.get('href')]
        zips = sorted([f for f in links_arquivos if f.lower().endswith('.zip')], reverse=True)
        
        for zip_name in zips:
            if len(arquivos_baixados) >= 3:
                break
            
            full_url = f"{url_ano}{zip_name}"
            # O nome do arquivo salvo será algo como "2025_3T2025.zip" para evitar conflitos
            download_file(full_url, f"{ano}_{zip_name}")
            arquivos_baixados.append(f"{ano}/{zip_name}")

    print("-" * 30)
    print(f"Processo finalizado. {len(arquivos_baixados)} arquivos baixados.")
    print(arquivos_baixados)

