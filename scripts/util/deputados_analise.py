import pandas as pd
import os
import matplotlib.pyplot as plt
import json
from scripts.util.utils import generate_llm_response, get_data_path
from .utils import get_data_path
from .llms import generate_llm_response
import logging

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pie_chart():
    # Carregar os dados dos deputados
    df = pd.read_parquet(get_data_path('deputados.parquet'))
    
    # Contar o número de deputados por partido
    party_counts = df['siglaPartido'].value_counts()
    
    # Gerar o gráfico de pizza
    plt.figure(figsize=(10, 10))
    plt.pie(party_counts.values, labels=party_counts.index, autopct='%1.1f%%')
    plt.title('Distribuição de Deputados por Partido\n\n')
    plt.axis('equal')
    
    # Salvar o gráfico
    plt.savefig(get_data_path('../data/distribuicao_deputados.png'))
    plt.close()
    
    return party_counts


def generate_insights(contexto, conhecimento, prompt=None, tipo_insight=None):
    default_prompt = f"""
    Atue como um analista político especializado em sistemas legislativos.
    
    Contexto: A atual distribuição de deputados por partido na Câmara dos Deputados do Brasil é a seguinte:
    {contexto}
    
    Conhecimento Gerado: {conhecimento['overview_summary']}

    Tarefa: Com base no contexto e no conhecimento gerado acima, analise como esta distribuição partidária 
    influencia o funcionamento da Câmara. Aprofunde e expanda os insights fornecidos, adicionando novas 
    perspectivas e análises mais detalhadas.
    
    Formato de saída: Forneça sua análise em formato JSON com os seguintes campos:
    1. padroes_despesas: Lista de observações principais sobre os padrões de despesas
    2. implicacoes_fiscalizacao: Como essa distribuição afeta a fiscalização e transparência dos gastos
    3. tendencias_futuras: Possíveis tendências futuras baseadas nesta distribuição
    
    Exemplo de observação: "O partido X, com maior representação, tende a ter mais influência na definição da agenda legislativa"
    
    Baseie sua análise em fatos e forneça 3 insights relevantes e bem fundamentados para cada campo.
    """
    
    # Use o prompt fornecido se existir, caso contrário, use o prompt padrão
    prompt_to_use = prompt if prompt else default_prompt
    
    response = generate_llm_response(prompt_to_use)
    
    logger.info(f"Resposta do LLM: {response}")
    
    # Determine o nome do arquivo baseado no tipo de insight
    if tipo_insight == "despesas":
        filename = 'insights_despesas_deputados.json'
    else:
        filename = 'insights_distribuicao_deputados.json'
    
    if isinstance(response, dict) and 'text' in response:
        try:
            # Extrair o JSON da resposta
            json_str = response['text'].split('```json\n')[1].split('\n```')[0]
            insights_data = json.loads(json_str)
            
            # Verificar se todos os campos necessários estão presentes
            expected_fields = ['padroes_despesas', 'implicacoes_fiscalizacao', 'tendencias_futuras']
            if all(key in insights_data for key in expected_fields):
                # Salvar os insights em um arquivo JSON
                with open(get_data_path(filename), 'w') as f:
                    json.dump(insights_data, f, indent=4)
                
                return insights_data
            else:
                logger.error("Resposta do LLM não contém todos os campos necessários")
        except json.JSONDecodeError:
            logger.error("Não foi possível decodificar o JSON da resposta do LLM")
        except IndexError:
            logger.error("Não foi possível extrair o JSON da resposta do LLM")
    
    elif isinstance(response, dict) and "insights" in response:
        # Se a resposta contiver insights, tenta formatá-la como JSON
        try:
            formatted_response = {
                "padroes_despesas": [response["insights"]],
                "implicacoes_fiscalizacao": ["Não foi possível gerar implicações estruturadas."],
                "tendencias_futuras": ["Não foi possível gerar tendências futuras estruturadas."]
            }
            with open(get_data_path(filename), 'w') as f:
                json.dump(formatted_response, f, indent=4)
            return formatted_response
        except Exception as e:
            logger.error(f"Erro ao formatar resposta: {str(e)}")
            return {"error": "Não foi possível gerar ou formatar insights"}
    
    logger.error(f"Resposta do LLM não está no formato esperado: {response}")
    return {
        "padroes_despesas": ["Não foi possível gerar padrões de despesas."],
        "implicacoes_fiscalizacao": ["Não foi possível gerar implicações de fiscalização."],
        "tendencias_futuras": ["Não foi possível gerar tendências futuras."]
    }
#############################################

# def generate_insights(contexto, conhecimento, prompt=None):
#     default_prompt = f"""
#     Atue como um analista político especializado em sistemas legislativos.
    
#     Contexto: A atual distribuição de deputados por partido na Câmara dos Deputados do Brasil é a seguinte:
#     {contexto}
    
#     Conhecimento Gerado: {conhecimento['overview_summary']}

#     Tarefa: Com base no contexto e no conhecimento gerado acima, analise como esta distribuição partidária 
#     influencia o funcionamento da Câmara. Aprofunde e expanda os insights fornecidos, adicionando novas 
#     perspectivas e análises mais detalhadas.
    
#     Formato de saída: Forneça sua análise em formato JSON com os seguintes campos:
#     1. observacoes_principais: Lista de observações principais sobre a distribuição
#     2. implicacoes_processo_legislativo: Como essa distribuição afeta o processo legislativo
#     3. cenarios_futuros: Possíveis cenários futuros baseados nesta distribuição
    
#     Exemplo de observação: "O partido X, com maior representação, tende a ter mais influência na definição da agenda legislativa"
    
#     Baseie sua análise em fatos e forneça 3 insights relevantes e bem fundamentados.
#     """
    
#     # Use o prompt fornecido se existir, caso contrário, use o prompt padrão
#     prompt_to_use = prompt if prompt else default_prompt
    
#     response = generate_llm_response(prompt_to_use)

#     logger.info(f"Resposta do LLM: {response}")
    
#     #if isinstance(response, dict) and "error" not in response:
#     if isinstance(response, dict) and all(key in response for key in ['padroes_despesas', 'implicacoes_fiscalizacao', 'tendencias_futuras']):
#         # Salvar os insights em um arquivo JSON
#         with open(get_data_path('insights_distribuicao_deputados.json'), 'w') as f:
#             json.dump(response, f, indent=4)
        
#         return response
    
#     elif isinstance(response, dict) and "insights" in response:
#         # Se a resposta contiver insights, tenta formatá-la como JSON
#         try:
#             formatted_response = {
#                 "observacoes_principais": [response["insights"]],
#                 "implicacoes_processo_legislativo": "Não foi possível gerar implicações estruturadas.",
#                 "cenarios_futuros": "Não foi possível gerar cenários futuros estruturados."
#             }
#             with open(get_data_path('insights_distribuicao_deputados.json'), 'w') as f:
#                 json.dump(formatted_response, f, indent=4)
#             return formatted_response
#         except Exception as e:
#             print(f"Erro ao formatar resposta: {str(e)}")
#             return {"error": "Não foi possível gerar ou formatar insights"}
#     else:
#         return {"error": "Não foi possível gerar insights"}


# def generate_insights(contexto, conhecimento):
#     prompt = f"""
#     Atue como um analista político especializado em sistemas legislativos.
    
#     Contexto: A atual distribuição de deputados por partido na Câmara dos Deputados do Brasil é a seguinte:
#     {contexto}
    
#     Conhecimento Gerado: {conhecimento['overview_summary']}

#     Tarefa: Com base no contexto e no conhecimento gerado acima, analise como esta distribuição partidária 
#     influencia o funcionamento da Câmara. Aprofunde e expanda os insights fornecidos, adicionando novas 
#     perspectivas e análises mais detalhadas.
    
#     Formato de saída: Forneça sua análise em formato JSON com os seguintes campos:
#     1. observacoes_principais: Lista de observações principais sobre a distribuição
#     2. implicacoes_processo_legislativo: Como essa distribuição afeta o processo legislativo
#     3. cenarios_futuros: Possíveis cenários futuros baseados nesta distribuição
    
#     Exemplo de observação: "O partido X, com maior representação, tende a ter mais influência na definição da agenda legislativa"
    
#     Baseie sua análise em fatos e forneça 3 insights relevantes e bem fundamentados.
#     """
    
#     response = generate_llm_response(prompt)
    
#     if isinstance(response, dict) and "error" not in response:
#         # Salvar os insights em um arquivo JSON
#         with open(get_data_path('insights_distribuicao_deputados.json'), 'w') as f:
#             json.dump(response, f, indent=4)
        
#         return response
#     elif isinstance(response, dict) and "insights" in response:
#         # Se a resposta contiver insights, tenta formatá-la como JSON
#         try:
#             formatted_response = {
#                 "observacoes_principais": [response["insights"]],
#                 "implicacoes_processo_legislativo": "Não foi possível gerar implicações estruturadas.",
#                 "cenarios_futuros": "Não foi possível gerar cenários futuros estruturados."
#             }
#             with open(get_data_path('insights_distribuicao_deputados.json'), 'w') as f:
#                 json.dump(formatted_response, f, indent=4)
#             return formatted_response
#         except Exception as e:
#             print(f"Erro ao formatar resposta: {str(e)}")
#             return {"error": "Não foi possível gerar ou formatar insights"}
#     else:
#         return {"error": "Não foi possível gerar insights"}



def sumarizar_proposicoes_por_chunks(df_proposicoes, chunk_size=5):
    """
    Sumariza as proposições por chunks e retorna o resultado.
    """
    sumarizacoes = []
    
    for i in range(0, len(df_proposicoes), chunk_size):
        chunk = df_proposicoes.iloc[i:i+chunk_size]
        
        # Criar um prompt para o chunk atual
        prompt = f"""
        Sumarize as seguintes proposições:
        
        {chunk[['tema', 'ementa']].to_string(index=False)}
        
        Forneça um resumo conciso das principais tendências e temas abordados nestas proposições.
        """
        
        # Gerar a sumarização para o chunk
        sumarizacao = generate_llm_response(prompt)
        
        if isinstance(sumarizacao, dict) and "text" in sumarizacao:
            sumarizacoes.append(sumarizacao["text"])
        elif isinstance(sumarizacao, str):
            sumarizacoes.append(sumarizacao)
    
    return sumarizacoes

def salvar_sumarizacao(sumarizacoes):
    """
    Salva as sumarizações em um arquivo JSON.
    """
    data = {"sumarizacao_proposicoes": sumarizacoes}
    with open(get_data_path('sumarizacao_proposicoes.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


