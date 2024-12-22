import os
import sys

# Adicione o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import requests
import streamlit as st  
import logging
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from scripts.util.utils import get_data_path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

try:
    url_base=os.getenv('DP_URL')

except Exception as e:
    st.error(f"Error initializing API DP: {str(e)}")
    st.stop()

def get_deputados():
    url = f"{url_base}/deputados"
    params = {
        'ordem': 'ASC',
        'ordenarPor': 'nome'
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        deputados_data = response.json()["dados"]
        df_deputados = pd.DataFrame(deputados_data)
        df_deputados.to_parquet(get_data_path("deputados.parquet"), index=False)
        print(f"Dados dos deputados salvos em {get_data_path('deputados.parquet')}")
        return df_deputados
    else:
        print(f"Erro ao acessar API: {response.status_code}")
        return None


def get_despesas():
    logger.info("Iniciando obtenção de despesas")
    try:
        df_deputados = pd.read_parquet(get_data_path("deputados.parquet"))
        logger.info(f"Dados de {len(df_deputados)} deputados carregados")
    except FileNotFoundError:
        logger.warning("Arquivo de deputados não encontrado. Obtendo dados dos deputados.")
        df_deputados = get_deputados()
        if df_deputados is None:
            logger.error("Não foi possível obter os dados dos deputados.")
            return None

    lista_despesas = []
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    total_deputados = len(df_deputados)
    for index, deputado in df_deputados.iterrows():
        deputado_id = deputado["id"]
        logger.info(f"Obtendo despesas do deputado {deputado['nome']} ({index+1}/{total_deputados})")
        
        # Tenta obter despesas dos últimos 6 meses
        for i in range(6):
            data = datetime.now() - timedelta(days=30*i)
            ano = data.year
            mes = data.month
            
            url = f"{url_base}/deputados/{deputado_id}/despesas"
            params = {
                'ano': ano,
                'mes': mes,
                'ordem': 'ASC',
                'ordenarPor': 'ano'
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                despesas_data = response.json()["dados"]
                for despesa in despesas_data:
                    despesa["deputado_id"] = deputado_id
                    despesa["nome"] = deputado["nome"]
                    # Converta explicitamente a urlDocumento para string
                    despesa["urlDocumento"] = str(despesa.get("urlDocumento", ""))
                    lista_despesas.append(despesa)
                logger.info(f"Obtidas {len(despesas_data)} despesas para {ano}/{mes}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao acessar despesas do deputado {deputado_id} para {ano}/{mes}: {str(e)}")

    if not lista_despesas:
        logger.warning("Não foi possível obter despesas para nenhum deputado.")
        return None

    logger.info(f"Total de {len(lista_despesas)} despesas obtidas")
    df_despesas = pd.DataFrame(lista_despesas)
    
    # Converta todas as colunas object para string
    for col in df_despesas.select_dtypes(include=['object']):
        df_despesas[col] = df_despesas[col].astype(str)
    
    df_despesas_grouped = df_despesas.groupby(["dataDocumento", "nome", "tipoDespesa"]).sum().reset_index()
    
    try:
        df_despesas_grouped.to_parquet(get_data_path("serie_despesas_diárias_deputados.parquet"), index=False)
        logger.info(f"Dados de despesas salvos em {get_data_path('serie_despesas_diárias_deputados.parquet')}")
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo Parquet: {str(e)}")
        return None

    return df_despesas_grouped


def get_proposicoes():
    try:
        url_base=os.getenv('DP_URL')

    except Exception as e:
        st.error(f"Error initializing API DP: {str(e)}")
        st.stop()


    temas = {
        40: "Economia",
        46: "Educação",
        62: "Ciência, Tecnologia e Inovação"
    }
    
    all_proposicoes = []
    
    data_fim = datetime.now().strftime("%Y-%m-%d")
    data_inicio = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    for tema_id, tema_nome in temas.items():
        proposicoes_tema = []
        pagina = 1
        
        while len(proposicoes_tema) < 10:
            url = f"{url_base}/proposicoes"
            params = {
                'dataInicio': data_inicio,
                'dataFim': data_fim,
                'codTema': tema_id,
                'itens': 100,  # Máximo permitido pela API
                'pagina': pagina
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                proposicoes_data = response.json()["dados"]
                
                for prop in proposicoes_data:
                    if len(proposicoes_tema) < 10:
                        prop['tema'] = tema_nome
                        proposicoes_tema.append(prop)
                    else:
                        break
                
                if len(proposicoes_data) < 100:  # Última página
                    break
                
                pagina += 1
            else:
                print(f"Erro ao acessar API de proposições para o tema {tema_nome}: {response.status_code}")
                break
        
        all_proposicoes.extend(proposicoes_tema)
    
    if all_proposicoes:
        df_proposicoes = pd.DataFrame(all_proposicoes)
        df_proposicoes.to_parquet(get_data_path("proposicoes_deputados.parquet"), index=False)
        print(f"Dados das proposições salvos em {get_data_path('proposicoes_deputados.parquet')}")
        return df_proposicoes
    else:
        print("Não foi possível obter proposições.")
        return None


deputados = get_deputados
despesas = get_despesas
proposicoes = get_proposicoes

if __name__ == "__main__":
    get_deputados()
    get_despesas()
    get_proposicoes()