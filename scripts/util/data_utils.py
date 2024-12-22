import pandas as pd
import logging
import os
import json

from scripts.util.utils import get_data_path
from scripts.util.file_utils import ensure_directory_exists, save_yaml, save_json
from scripts.dataprep import deputados, despesas, proposicoes

logger = logging.getLogger(__name__)

def ensure_data_prepared():
    logger.info("Iniciando preparação dos dados")
    ensure_directory_exists(get_data_path(''))
    
    try:
        if not os.path.exists(get_data_path('deputados.parquet')):
            logger.info("Obtendo dados dos deputados")
            deputados()
        
        if not os.path.exists(get_data_path('serie_despesas_diárias_deputados.parquet')):
            logger.info("Obtendo dados das despesas")
            despesas()
        
        if not os.path.exists(get_data_path('proposicoes_deputados.parquet')):
            logger.info("Obtendo dados das proposições")
            proposicoes()
    except Exception as e:
        logger.error(f"Erro durante a obtenção de dados: {str(e)}")
        raise
    
    # Generate config.yaml if it doesn't exist
    if not os.path.exists(get_data_path('config.yaml')):
        config = {
            'data': {
                'config': {
                    'overview_summary': 'Esta é uma visão geral da Câmara dos Deputados.'
                }
            }
        }
        save_yaml(config, get_data_path('config.yaml'))
    
    # Generate insights files if they don't exist
    empty_insights = {"insights": []}
    empty_sumarizacao = {"sumarizacao_proposicoes": []}

    files_to_create = [
        ('insights_despesas_deputados.json', empty_insights),
        ('insights_distribuicao_deputados.json', empty_insights),
        ('sumarizacao_proposicoes.json', empty_sumarizacao)
    ]

    for filename, content in files_to_create:
        file_path = get_data_path(filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=4)
    
    logger.info("Preparação dos dados concluída")



def load_deputados():
    try:
        df = pd.read_parquet(get_data_path('deputados.parquet'))
        if df.empty:
            logger.warning("Arquivo 'deputados.parquet' está vazio.")
            return pd.DataFrame({'siglaPartido': ['Dados não disponíveis']})
        return df
    except FileNotFoundError:
        logger.error("Arquivo 'deputados.parquet' não encontrado.")
        return pd.DataFrame({'siglaPartido': ['Arquivo não encontrado']})
    except Exception as e:
        logger.error(f"Erro ao carregar 'deputados.parquet': {e}")
        return pd.DataFrame({'siglaPartido': ['Erro ao carregar dados']})

def load_despesas():
    try:
        df = pd.read_parquet(get_data_path('serie_despesas_diárias_deputados.parquet'))
        if df.empty:
            logger.warning("Arquivo de despesas está vazio.")
            return pd.DataFrame({'nome': ['Dados não disponíveis'], 'dataDocumento': [pd.Timestamp.now()], 'valorDocumento': [0]})
        return df
    except FileNotFoundError:
        logger.error("Arquivo de despesas não encontrado.")
        return pd.DataFrame({'nome': ['Arquivo não encontrado'], 'dataDocumento': [pd.Timestamp.now()], 'valorDocumento': [0]})
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de despesas: {e}")
        return pd.DataFrame({'nome': ['Erro ao carregar dados'], 'dataDocumento': [pd.Timestamp.now()], 'valorDocumento': [0]})

def load_proposicoes():
    try:
        df = pd.read_parquet(get_data_path('proposicoes_deputados.parquet'))
        if df.empty:
            logger.warning("Arquivo de proposições está vazio.")
            return pd.DataFrame({'Proposição': ['Dados não disponíveis']})
        return df
    except FileNotFoundError:
        logger.error("Arquivo de proposições não encontrado.")
        return pd.DataFrame({'Proposição': ['Arquivo não encontrado']})
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de proposições: {e}")
        return pd.DataFrame({'Proposição': ['Erro ao carregar dados']})