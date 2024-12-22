import os
import re
import markdown
from openai import OpenAI
import json
import torch
import faiss
from transformers import AutoTokenizer, AutoModel
import pandas as pd
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
import torch

load_dotenv()  # Carrega as variáveis do arquivo .env

huggingface_token = os.getenv("HUGGING_FACE_API_KEY")
#tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased", token=huggingface_token)

cache_dir = './models/transformers_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
os.environ['TRANSFORMERS_CACHE'] = cache_dir

# Configuração do cache e do tokenizer
os.environ['TRANSFORMERS_CACHE'] = './models/transformers_cache'

tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")

model = AutoModel.from_pretrained("neuralmind/bert-base-portuguese-cased")

# Funções auxiliares
def list_md_files(directory):
    """Função para listar arquivos .md"""
    return [f for f in os.listdir(directory) if f.endswith('.md')]

def read_md_file(file_path):
    """Função para ler o conteúdo do arquivo .md"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def natural_sort_key(s):
    """Função auxiliar para ordenação natural de strings"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def find_images(directory, file_prefix):
    """Função para encontrar imagens correspondentes"""
    images = [f for f in os.listdir(directory) if f.startswith(file_prefix) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return sorted(images, key=natural_sort_key)

def render_md_content(content):
    """Função para renderizar conteúdo markdown em HTML"""
    return markdown.markdown(content)

# Funções para o LLM e Self-Ask
def generate_llm_response(prompt):
    """Gera uma resposta usando o modelo de linguagem OpenAI."""
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
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"text": response}
    except Exception as e:
        print(f"Erro ao gerar resposta do LLM: {str(e)}")
        return {"error": str(e)}


def self_ask_assistant(user_input):
    initial_prompt = f"""..."""
    response = generate_llm_response(initial_prompt)
    return response['text'] if 'text' in response else json.dumps(response)

def get_largest_party(df_deputados):
    party_counts = df_deputados['siglaPartido'].value_counts()
    largest_party = party_counts.index[0]
    count = party_counts.iloc[0]
    
    prompt = f"""
    Com base nos dados atuais da Câmara dos Deputados:
    
    O partido com mais deputados é o {largest_party}, com {count} deputados.
    
    Por favor, forneça uma análise concisa sobre:
    1. O que isso significa para o equilíbrio de poder na Câmara?
    2. Como isso pode afetar a formação de coalizões?
    3. Quais são as implicações para a agenda legislativa?
    
    Limite sua resposta a 3-4 parágrafos.
    """
    
    return generate_llm_response(prompt)

def get_highest_spending_deputy(df_despesas):
    deputy_expenses = df_despesas.groupby('nome')['valorDocumento'].sum().sort_values(ascending=False)
    highest_spender = deputy_expenses.index[0]
    amount = deputy_expenses.iloc[0]
    
    prompt = f"""
    Com base nos dados atuais de despesas da Câmara dos Deputados:
    
    O deputado com mais despesas é {highest_spender}, com um total de R$ {amount:.2f}.
    
    Por favor, forneça uma análise concisa sobre:
    1. O que pode explicar esse alto nível de despesas?
    2. Como isso se compara com a média de despesas dos deputados?
    3. Quais são as implicações para a transparência e fiscalização dos gastos públicos?
    
    Limite sua resposta a 3-4 parágrafos.
    """
    
    return generate_llm_response(prompt)

def get_most_common_expense(df_despesas):
    expense_counts = df_despesas['tipoDespesa'].value_counts()
    most_common = expense_counts.index[0]
    count = expense_counts.iloc[0]
    
    prompt = f"""
    Com base nos dados atuais de despesas da Câmara dos Deputados:
    
    O tipo de despesa mais declarado é "{most_common}", com {count} ocorrências.
    
    Por favor, forneça uma análise concisa sobre:
    1. Por que este tipo de despesa é tão comum?
    2. Quais são as implicações deste padrão de gastos?
    3. Como isso se relaciona com as atividades parlamentares?
    
    Limite sua resposta a 3-4 parágrafos.
    """
    
    return generate_llm_response(prompt)


def get_economic_propositions(df_proposicoes):
    economic_props = df_proposicoes[df_proposicoes['tema'].str.contains('Economia', case=False)]
    
    prompt = f"""
    Analisando as proposições relacionadas à Economia na Câmara dos Deputados:
    
    Número total de proposições sobre Economia: {len(economic_props)}
    
    Temas mais frequentes:
    {economic_props['tema'].value_counts().head(5).to_string()}
    
    Por favor, forneça uma análise concisa sobre:
    1. Quais são as principais tendências nas proposições econômicas?
    2. Como essas proposições podem impactar a economia brasileira?
    3. Há algum tema econômico que parece estar sub-representado?
    
    Limite sua resposta a 3-4 parágrafos.
    """
    
    return generate_llm_response(prompt)


def get_science_tech_propositions(df_proposicoes):
    sci_tech_props = df_proposicoes[df_proposicoes['tema'].str.contains('Ciência|Tecnologia|Inovação', case=False)]
    
    prompt = f"""
    Analisando as proposições relacionadas à Ciência, Tecnologia e Inovação na Câmara dos Deputados:
    
    Número total de proposições sobre Ciência, Tecnologia e Inovação: {len(sci_tech_props)}
    
    Temas mais frequentes:
    {sci_tech_props['tema'].value_counts().head(5).to_string()}
    
    Por favor, forneça uma análise concisa sobre:
    1. Quais são as principais tendências nas proposições de Ciência, Tecnologia e Inovação?
    2. Como essas proposições podem impactar o desenvolvimento científico e tecnológico do Brasil?
    3. Há alguma área de Ciência, Tecnologia ou Inovação que parece estar sub-representada?
    
    Limite sua resposta a 3-4 parágrafos.
    """
    
    return generate_llm_response(prompt)

def generate_image_from_prompt(prompt, negative_prompt="", num_images=1):
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
    
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    
    images = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_images_per_prompt=num_images,
        guidance_scale=7.5
    ).images
    
    return images