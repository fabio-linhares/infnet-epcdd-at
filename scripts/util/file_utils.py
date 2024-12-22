import os
import fcntl
import yaml
import json
import logging

logger = logging.getLogger(__name__)

def acquire_lock(lockfile):
    try:
        fd = open(lockfile, 'w')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except IOError:
        return None

def release_lock(fd):
    fcntl.flock(fd, fcntl.LOCK_UN)
    fd.close()

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Diretório {path} criado")

def save_yaml(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)

def load_yaml(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Arquivo YAML não encontrado: {filepath}")
        return {'data': {'config': {'overview_summary': 'Dados não disponíveis.'}}}
    except yaml.YAMLError as e:
        logger.error(f"Erro ao carregar arquivo YAML: {e}")
        return {'data': {'config': {'overview_summary': 'Erro ao carregar dados.'}}}

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# def load_json(filepath):
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         logger.error(f"Arquivo JSON não encontrado: {filepath}")
#         return {'insights': ['Dados não disponíveis.']}
#     except json.JSONDecodeError:
#         logger.error(f"Erro ao decodificar o arquivo JSON: {filepath}")
#         return {'insights': ['Erro ao carregar dados.']}

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Arquivo JSON carregado com sucesso: {file_path}")
        logger.debug(f"Conteúdo do arquivo JSON: {data}")
        return data
    except FileNotFoundError:
        logger.error(f"Arquivo JSON não encontrado: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar o arquivo JSON: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo JSON {file_path}: {str(e)}")
        return None