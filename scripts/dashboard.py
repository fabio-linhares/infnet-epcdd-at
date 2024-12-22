import os
import sys
import logging
import json
import random

# Adicione o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Resto das importações
import streamlit as st
from openai import OpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from scripts.dataprep import deputados, despesas, proposicoes
from scripts.util.database_utils import get_db_connection, close_all_connections, initialize_database, save_chat_history
from scripts.util.file_utils import load_yaml, load_json
from scripts.util.data_utils import load_proposicoes, load_deputados, load_despesas, ensure_data_prepared
from scripts.util.utils import read_markdown_file, get_data_path
from scripts.util.deputados_analise import generate_pie_chart, generate_insights,sumarizar_proposicoes_por_chunks,salvar_sumarizacao 
from scripts.util.llms import list_md_files, read_md_file, find_images, render_md_content, generate_image_from_prompt
from scripts.util.llms import get_largest_party, get_highest_spending_deputy, get_most_common_expense, get_economic_propositions, get_science_tech_propositions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Iniciando a aplicação")

ensure_data_prepared()

# Load environment variables
load_dotenv()

# Obter os caminhos do README e Assessment a partir das variáveis de ambiente
readme_path = os.getenv('README_PATH', 'Caminho padrão para README não definido')
assessment_path = os.getenv('ASSESSMENT_PATH', 'Caminho padrão para ASSESSMENT não definido')

# Conteúdo do README e da Apresentação
readme_content = read_markdown_file(readme_path)
assessment_content = read_markdown_file(assessment_path)

# Initialize OpenAI client
try:
    client = OpenAI(
        base_url=os.getenv('OPENAI_BASE_URL'),
        api_key=os.getenv('OPENAI_API_KEY')
    )
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

# Close any open connections before starting
close_all_connections()

# Initialize SQLite database
try:
    initialize_database()
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    st.error(f"Database error: {str(e)}")
    st.stop()

try:
    # Ensure data is prepared before starting the app
    logger.info("Chamando ensure_data_prepared()")
    ensure_data_prepared()
    logger.info("ensure_data_prepared() concluído")

    # Streamlit app
    logger.info("Configurando página Streamlit")
    st.set_page_config(page_title="Dashboard - Câmara dos Deputados (ago/2024)", layout="wide")
    logger.info("Página Streamlit configurada")

    # Sidebar for navigation
    page = st.sidebar.radio("Navegação", ["Assessment", "Readme","Rubricas", "Chat", "LLMs", "Overview", "Despesas", "Proposições", "Análise de Deputados"])

    if page == "Assessment":
        st.markdown(assessment_content)
        
    elif page == "Readme": 
        st.markdown(readme_content)
    
    elif page == "Análise de Deputados":
        st.title("Análise de Deputados")
        
        # Gerar e exibir o gráfico
        party_counts = generate_pie_chart()
        config = load_yaml(get_data_path('config.yaml'))

        st.image('data/distribuicao_deputados.png')
        
        # Gerar e exibir insights
        insights = generate_insights(party_counts.to_dict(), config)
        
        st.subheader("Insights sobre a Distribuição de Deputados")
        if "error" in insights:
            st.error(insights["error"])
        else:
            st.json(insights)
    
    elif page == "Chat":
        logger.info("Renderizando página de Chat")
        st.title(os.getenv('APP_TITLE'))

        use_assistant = st.checkbox("Ativar Assistente Virtual")
        generate_images = st.checkbox("Gerar Imagens das Proposições")

        # Carregar os dados
        df_deputados = load_deputados()
        df_despesas = load_despesas()
        df_proposicoes = load_proposicoes()

        # Adicionar radio buttons para análises específicas
        analysis_option = st.radio(
            "Escolha uma análise específica:",
            ("Nenhuma", "Analisar Maior Partido", "Analisar Deputado com Mais Despesas", 
            "Analisar Despesa Mais Comum", "Analisar Proposições Econômicas", 
            "Analisar Proposições de Ciência e Tecnologia")
        )

        if generate_images:
            # Carregar sumarizações das proposições
            with open(get_data_path('sumarizacao_proposicoes.json'), 'r') as f:
                sumarizacoes = json.load(f)['sumarizacao_proposicoes']
            
            # Selecionar duas proposições aleatórias
            selected_propositions = random.sample(sumarizacoes, 2)
            
            for i, proposition in enumerate(selected_propositions):
                st.subheader(f"Proposição {i+1}")
                st.write(proposition)
                
                # Gerar prompts para as imagens
                prompts = [
                    f"Realistic painting of {proposition}",
                    f"Abstract art representing {proposition}",
                    f"Surrealist interpretation of {proposition}"
                ]
                
                negative_prompt = "low quality, blurry, text"
                
                for j, prompt in enumerate(prompts):
                    st.write(f"Estilo {j+1}")
                    images = generate_image_from_prompt(prompt, negative_prompt)
                    st.image(images[0], caption=f"Imagem gerada para: {prompt}")

            if analysis_option != "Nenhuma":
                if analysis_option == "Analisar Maior Partido":
                    response = get_largest_party(df_deputados)
                elif analysis_option == "Analisar Deputado com Mais Despesas":
                    response = get_highest_spending_deputy(df_despesas)
                elif analysis_option == "Analisar Despesa Mais Comum":
                    response = get_most_common_expense(df_despesas)
                elif analysis_option == "Analisar Proposições Econômicas":
                    response = get_economic_propositions(df_proposicoes)
                elif analysis_option == "Analisar Proposições de Ciência e Tecnologia":
                    response = get_science_tech_propositions(df_proposicoes)
                
                st.write(response['text'])

        # Resto do código do chat
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        if 'memory' not in st.session_state:
            st.session_state.memory = ChatMessageHistory()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input(os.getenv('INPUT_PLACEHOLDER'))

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            conversation_history = []
            for message in st.session_state.messages:
                if message["role"] == "user":
                    conversation_history.append(HumanMessage(content=message["content"]))
                else:
                    conversation_history.append(AIMessage(content=message["content"]))

            # Add conversation to memory
            for message in conversation_history:
                if isinstance(message, HumanMessage):
                    st.session_state.memory.add_user_message(message.content)
                elif isinstance(message, AIMessage):
                    st.session_state.memory.add_ai_message(message.content)

            # Get memory buffer
            memory_buffer = st.session_state.memory.messages

            if use_assistant:
                # Lógica do assistente virtual
                system_message = "Você é um assistente virtual especialista em informações sobre a Câmara dos Deputados do Brasil. Use a técnica Self-Ask para responder às perguntas."
                prompt = f"Conversation history: {[m.content for m in memory_buffer]}\n\nUser's question: {user_input}\n\nUse a técnica Self-Ask para decompor e responder à pergunta."
            else:
                # Lógica do chat normal
                system_message = os.getenv('SYSTEM_MESSAGE')
                prompt = f"Conversation history: {[m.content for m in memory_buffer]}\n\nUser's question: {user_input}"

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]

            # Make API call
            with st.spinner(os.getenv('THINKING_MESSAGE')):
                try:
                    completion = client.chat.completions.create(
                        model=os.getenv('MODEL_NAME'),
                        messages=messages,
                        temperature=float(os.getenv('TEMPERATURE')),
                        top_p=float(os.getenv('TOP_P')),
                        max_tokens=int(os.getenv('MAX_TOKENS')),
                        stream=True
                    )

                    # Display AI response
                    with st.chat_message("assistant"):
                        response_container = st.empty()
                        full_response = ""
                        for chunk in completion:
                            if chunk.choices[0].delta.content is not None:
                                full_response += chunk.choices[0].delta.content
                                response_container.markdown(full_response + "▌")
                        response_container.markdown(full_response)

                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                    # Save to database
                    try:
                        save_chat_history(user_input, full_response)
                    except Exception as e:
                        logger.warning(f"Failed to save chat history: {str(e)}")
                        st.warning("Failed to save chat history. Please try again.")

                except Exception as e:
                    logger.error(f"Error generating response: {str(e)}")
                    st.error(f"Error generating response: {str(e)}")

    elif page == "LLMs":
        logger.info("Renderizando página dos exercícios realizados com LLMs")
        st.title("LLMs")

        # Diretório onde estão os arquivos .md
        poe_directory = os.path.join(project_root, 'poe')

        # Listar arquivos .md
        md_files = list_md_files(poe_directory)

        if not md_files:
            st.warning("Nenhum arquivo .md encontrado no diretório poe.")
        else:
            # Inicializar o estado da sessão se ainda não existir
            if 'selected_file' not in st.session_state:
                st.session_state.selected_file = md_files[0]

            # Criar o menu de seleção
            selected_file = st.selectbox(
                "Selecione um arquivo para visualizar:",
                md_files,
                key='file_selector'
            )

            # Atualizar o estado da sessão
            if selected_file != st.session_state.selected_file:
                st.session_state.selected_file = selected_file

            # Exibir o conteúdo do arquivo selecionado
            file_path = os.path.join(poe_directory, st.session_state.selected_file)
            try:
                content = read_md_file(file_path)
                html_content = render_md_content(content)
                st.markdown(html_content, unsafe_allow_html=True)

                # Encontrar e exibir imagens correspondentes
                file_prefix = os.path.splitext(st.session_state.selected_file)[0]
                images = find_images(poe_directory, file_prefix + '_')

                if images:
                    st.subheader("Imagens relacionadas:")
                    for img in images:
                        img_path = os.path.join(poe_directory, img)
                        st.image(img_path, caption=img, use_container_width=True)
                else:
                    st.info("Sem imagens para exibir.")

            except Exception as e:
                logger.error(f"Erro ao ler o arquivo {file_path}: {e}")
                st.error(f"Erro ao ler o arquivo {st.session_state.selected_file}. Por favor, tente novamente.")

    elif page == "Overview":
        logger.info("Renderizando página de Overview")
        st.title("Overview: Câmara dos Deputados")
        
        # Load YAML config
        config = load_yaml(get_data_path('config.yaml'))
        
        st.write(config['overview_summary'])

        # Display distribution chart
        st.markdown('---')
        st.subheader("Distribuição dos Deputados")
        try:
            df_deputados = load_deputados()
            fig, ax = plt.subplots(figsize=(10, 6))
            df_deputados['siglaPartido'].value_counts().plot(kind='bar', ax=ax)
            plt.title('Distribuição dos Deputados por Partido')
            plt.xlabel('Partido')
            plt.ylabel('Número de Deputados')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        except FileNotFoundError:
            logger.error("Arquivo 'deputados.parquet' não encontrado.")
            st.error("Arquivo 'deputados.parquet' não encontrado. Certifique-se de que o arquivo esteja na pasta de dados.")
        except Exception as e:
            logger.error(f"Erro ao gerar o gráfico: {e}")
            st.error(f"Erro ao gerar o gráfico: {e}")

        # Display insights
        st.markdown('---')

        st.subheader("Insights sobre a Distribuição")
        try:
            insights_data = load_json(get_data_path('insights_distribuicao_deputados.json'))

            # Exibir padrões de despesas
            st.write("**Influência da Representação Partidária:**")
            for insight in insights_data['padroes_despesas']:
                st.write(f"- {insight}")

            # Exibir implicações para fiscalização
            st.write("**Impactos da Distribuição Partidária na Fiscalização e Transparência**")
            for insight in insights_data['implicacoes_fiscalizacao']:
                st.write(f"- {insight}")

            # Exibir tendências futuras
            st.write("**Cenários e Tendências para o Futuro Político na Câmara dos Deputados**")
            for insight in insights_data['tendencias_futuras']:
                st.write(f"- {insight}")



        except FileNotFoundError:
            logger.error("Arquivo 'insights_distribuicao_deputados.json' não encontrado.")
            st.error("Arquivo JSON não encontrado. Certifique-se de que o arquivo 'insights_distribuicao_deputados.json' esteja na pasta de dados.")
        except KeyError:
            logger.error("Chave 'insights' não encontrada no arquivo JSON.")
            st.error("Chave 'insights' não encontrada no arquivo JSON.")
        except Exception as e:
            logger.error(f"Erro ao carregar insights: {e}")
            st.error(f"Erro ao carregar insights: {e}")

    elif page == "Despesas":
        logger.info("Renderizando página de Despesas")
        st.title("Despesas dos Deputados")

        try:
            df_deputados = load_deputados()
            df_despesas = load_despesas()
            
            conhecimento = {
                'overview_summary': df_deputados['siglaPartido'].value_counts().to_dict(),
                'despesas_summary': {
                    'total': df_despesas['valorDocumento'].sum(),
                    'media_por_deputado': df_despesas.groupby('nome')['valorDocumento'].sum().mean(),
                    'top_5_categorias': df_despesas.groupby('tipoDespesa')['valorDocumento'].sum().nlargest(5).to_dict(),
                    'top_5_partidos': df_despesas.merge(df_deputados[['nome', 'siglaPartido']], on='nome').groupby('siglaPartido')['valorDocumento'].sum().nlargest(5).to_dict()
                }
            }
            
            logger.info(f"Conhecimento gerado: {conhecimento}")
            

            prompt_personalizado = f"""
                Atue como um analista político especializado em finanças públicas e gastos legislativos.

                Contexto: 
                1. Distribuição de deputados por partido na Câmara dos Deputados do Brasil:
                {conhecimento['overview_summary']}

                2. Resumo das despesas dos deputados:
                - Total de despesas: R$ {conhecimento['despesas_summary']['total']:.2f}
                - Média de despesas por deputado: R$ {conhecimento['despesas_summary']['media_por_deputado']:.2f}
                - Top 5 categorias de despesas: {conhecimento['despesas_summary']['top_5_categorias']}
                - Top 5 partidos com maiores despesas: {conhecimento['despesas_summary']['top_5_partidos']}

                Tarefa: Com base no contexto acima, analise como a distribuição partidária e os padrões de despesas 
                podem influenciar o uso da Cota para o Exercício da Atividade Parlamentar (CEAP). 
                Aprofunde e expanda os insights fornecidos, adicionando novas perspectivas e análises mais detalhadas sobre os gastos parlamentares.

                Formato de saída: Forneça sua análise em formato JSON com os seguintes campos:
                1. padroes_despesas: Lista de observações principais sobre os padrões de despesas dos deputados, considerando a distribuição partidária e os dados fornecidos
                2. implicacoes_fiscalizacao: Como essa distribuição e os padrões de gastos podem afetar a fiscalização e transparência dos gastos parlamentares
                3. tendencias_futuras: Possíveis tendências futuras nos gastos dos deputados baseadas nesta distribuição e nos padrões observados

                Exemplo de observação: "Partidos com maior representação tendem a ter maiores despesas totais, mas não necessariamente maiores despesas por deputado"

                Baseie sua análise em fatos e forneça 3 insights relevantes e bem fundamentados para cada campo, considerando aspectos como:
                - Diferenças nos padrões de gastos entre partidos maiores e menores
                - Possível influência ideológica nas prioridades de gastos
                - Impacto da distribuição partidária na aprovação de medidas de controle de despesas
                - Relação entre representatividade partidária e transparência nos gastos
                """

            logger.info(f"Prompt personalizado: {prompt_personalizado}")

            #insights_data = generate_insights(conhecimento['overview_summary'], conhecimento, prompt=prompt_personalizado)
            insights_data = generate_insights(conhecimento['overview_summary'], conhecimento, prompt=prompt_personalizado, tipo_insight="despesas")
            
            logger.info(f"Insights data: {insights_data}")

            st.subheader("Insights sobre as Despesas dos Deputados")

            for field in ['padroes_despesas', 'implicacoes_fiscalizacao', 'tendencias_futuras']:
                st.write(f"**{field.replace('_', ' ').title()}:**")
                if field in insights_data and insights_data[field]:
                    for item in insights_data[field]:
                        st.write(f"- {item}")
                else:
                    st.write("- Informações não disponíveis")

            # Adicione esta linha para debugar
            st.json(insights_data)
        
        except Exception as e:
            logger.error(f"Erro ao gerar ou exibir insights: {str(e)}")
            st.error(f"Ocorreu um erro ao gerar ou exibir os insights: {str(e)}")

        # Display expenses chart
        try:
            if df_despesas.empty:
                st.warning("Não há dados de despesas disponíveis.")
            else:
                deputados = df_despesas['nome'].unique()
                deputado_selecionado = st.selectbox('Selecione um Deputado:', deputados)

                df_deputado = df_despesas[df_despesas['nome'] == deputado_selecionado].copy()
                df_deputado['dataDocumento'] = pd.to_datetime(df_deputado['dataDocumento'])
                df_deputado = df_deputado.sort_values(by='dataDocumento')
                df_deputado = df_deputado.groupby('dataDocumento')['valorDocumento'].sum().reset_index()

                fig = px.bar(df_deputado, x='dataDocumento', y='valorDocumento', title=f'Despesas de {deputado_selecionado}')
                st.plotly_chart(fig)
        except Exception as e:
            logger.error(f"Ocorreu um erro ao carregar ou exibir as despesas: {e}")
            st.error(f"Ocorreu um erro ao carregar ou exibir as despesas: {e}")
            
    elif page == "Proposições":
        logger.info("Renderizando página de Proposições")
        st.title("Proposições")

        st.markdown("[Ir para o Chat com Assistente Virtual](/?page=Chat)")

        try:
            df_proposicoes = load_proposicoes()
            st.dataframe(df_proposicoes)

            # Realizar sumarização
            sumarizacoes = sumarizar_proposicoes_por_chunks(df_proposicoes)
            salvar_sumarizacao(sumarizacoes)

            # Exibir sumarizações
            st.subheader("Sumarização das Proposições")
            for i, sumario in enumerate(sumarizacoes, 1):
                st.markdown(f"**Resumo {i}:**")
                st.write(sumario)
                st.markdown("---")

        except FileNotFoundError:
            logger.error("Arquivo de proposições não encontrado.")
            st.error("Arquivo de proposições não encontrado. Certifique-se de que o arquivo esteja na pasta de dados.")
        except Exception as e:
            logger.error(f"Ocorreu um erro: {e}")
            st.error(f"Ocorreu um erro: {e}")

    elif page == "Rubricas":
        logger.info("Renderizando página de Rubricas")
        st.title("Rubricas do Assessment")

        # Caminho para o arquivo rubricas.md
        rubricas_file_path = os.path.join(project_root, 'poe', 'rubricas.md')

        try:
            # Ler o conteúdo do arquivo rubricas.md
            content = read_md_file(rubricas_file_path)
            
            # Renderizar o conteúdo do arquivo
            html_content = render_md_content(content)
            
            # Exibir o conteúdo renderizado
            st.markdown(html_content, unsafe_allow_html=True)
        
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo rubricas.md: {e}")
            st.error("Erro ao carregar as rubricas. Por favor, tente novamente mais tarde.")

                        

        # Close connections at the end of the script
        close_all_connections()
        logger.info("Aplicação encerrada")

except Exception as e:
    logger.error(f"Erro não tratado: {str(e)}")
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
    st.stop()