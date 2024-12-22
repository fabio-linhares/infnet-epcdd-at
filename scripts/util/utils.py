import os
from openai import OpenAI
import json

def get_project_root():
    """Retorna o diretório raiz do projeto."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_data_path(filename):
    """Retorna o caminho completo para um arquivo no diretório de dados."""
    return os.path.join(get_project_root(), 'data', filename)

def read_markdown_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Arquivo {filepath} não encontrado."
    except Exception as e:
        return f"Erro ao ler o arquivo {filepath}: {str(e)}"

def generate_llm_response(prompt):
    """
    Gera uma resposta usando o modelo de linguagem OpenAI.
    """
    client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    try:
        completion = client.chat.completions.create(
            model=os.getenv('MODEL_NAME'),
            messages=[
                {"role": "system", "content": os.getenv('SYSTEM_MESSAGE')},
                {"role": "user", "content": prompt}
            ],
            temperature=float(os.getenv('TEMPERATURE')),
            top_p=float(os.getenv('TOP_P')),
            max_tokens=int(os.getenv('MAX_TOKENS'))
        )
        response = completion.choices[0].message.content
        
        # Tenta analisar a resposta como JSON
        try:
            json_response = json.loads(response)
            return json_response
        except json.JSONDecodeError:
            # Se não for um JSON válido, retorna a resposta como texto
            return {"text": response}
    except Exception as e:
        print(f"Erro ao gerar resposta do LLM: {str(e)}")
        return {"error": str(e)}