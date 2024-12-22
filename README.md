# Projeto Câmara IA

Esta solução utiliza Inteligência Artificial para processar e analisar informações da Câmara dos Deputados do Brasil. 

## Estrutura do Projeto

- `data/`: Armazena dados processados e coletados.
- `docs/`: Contém gráficos e documentos gerados.
- `notebooks/`: Inclui notebooks para tarefas específicas.
- `scripts/`: Contém scripts Python para processamento offline e dashboard.
- `models/`: Reúne modelos treinados e bases vetoriais.
- `tests/`: Testes automatizados para validação do código.
- `.env`: Arquivo para variáveis sensíveis (não exportado para o git).
- `requirements.txt`: Lista de dependências do projeto.

## Como usar

1. Configure o ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

3. Preencha o arquivo `.env` com sua chave Gemini.

4. Execute o script de processamento:
    ```bash
    python scripts/dataprep.py
    ```

5. Inicie o dashboard:
    ```bash
    streamlit run scripts/dashboard.py
    ```
