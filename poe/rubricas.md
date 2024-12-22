## 1. Explicar o que é Inteligência Artificial Generativa e os Modelos Grandes de Linguagem (LLMs)

1. Explique com profundidade a arquitetura desenhada para a solução.  
   A arquitetura da solução é composta por várias camadas que trabalham em conjunto para fornecer uma análise completa dos dados da Câmara dos Deputados. As camadas incluem:

      - Camada de Dados: Armazena os dados brutos em diferentes formatos, como Parquet e JSON.
      - Camada de Processamento: Utiliza scripts Python para processar os dados e gerar insights.
      - Camada de Apresentação: Utiliza o Streamlit para criar um dashboard interativo que exibe os resultados.
      - Camada de Integração: Utiliza APIs para obter dados adicionais e integrar com outros sistemas. 



2. Explique com profundidade o funcionamento de LLMs para sumarização de textos.  
   Os Modelos Grandes de Linguagem (LLMs) são treinados em vastos conjuntos de dados textuais e podem gerar resumos de textos longos. O processo inclui:

      1. Preparação do Input: O texto a ser sumarizado é formatado como um prompt para o LLM.
      2. Geração do Resumo: O LLM processa o prompt e gera um resumo baseado em seu treinamento.
      3. Pós-Processamento: O resumo gerado pode ser refinado ou formatado conforme necessário.



3. Explique com profundidade as vantagens e desvantagens dos LLMs escolhidos para sumarização.  
      - Assistant: Claro e objetivo, mas pode ser genérico.
      - Claude-3.5-Haiku: Oferece detalhes específicos, mas pode ser extenso.
      - Grok-beta: Direto e aborda pontos-chave, mas falta profundidade.

4. Justifique o motivo da escolha do LLM final para a aplicação.   
   O LLM final escolhido foi o Assistant, devido à sua capacidade de fornecer uma visão geral clara e concisa sobre a Câmara dos Deputados, equilibrando a necessidade de informação com a acessibilidade para um público amplo.

---

## 2. Gerar textos a partir de técnicas com LLMs usando Prompt Engineering

1. Analise com profundidade as diferenças nas respostas do LLM.  
   As respostas dos LLMs diferem em termos de estrutura, estilo e relevância do conteúdo apresentado. O Assistant é mais conciso, enquanto o Claude-3.5-Haiku oferece mais detalhes e o Grok-beta é mais direto.


2. Crie um prompt para que o LLM escreva um código funcional de geração de análises de qualidade com gráficos de pizza.  
   O prompt deve incluir instruções específicas para o LLM gerar um código funcional que:

      - Carregue os dados necessários.
      - Gere um gráfico de pizza.
      - Forneça insights sobre a distribuição de deputados.

3. Explique com profundidade o objetivo dos elementos de cada prompt para a geração dos insights sobre a distribuição de deputados da câmara.  

      - Persona: Estabelecer o contexto de expertise.
      - Contexto: Fornecer os dados necessários.
      - Tarefa: Definir claramente o que se espera da análise.
      - Formato de Saída: Especificar o formato desejado (JSON).  

4. Manipule o resultado do LLM como dados estruturados em YAML.  

   O resultado do LLM pode ser manipulado para criar um arquivo YAML com a seguinte estrutura:

   ```yaml
   overview_summary: |
   [Resposta escolhida do modelo final, formatada corretamente]

---

## 3. Utilizar técnicas avançadas de Prompt Engineering

1. Crie uma aplicação com prompt-chaining para instruir o LLM a enumerar possíveis análises e, posteriormente, use esse resultado para a instrução de outro LLM.  

   A aplicação pode ser criada utilizando prompt-chaining para instruir o LLM a:

      1. Enumerar possíveis análises.
      2. Usar o resultado para a instrução de outro LLM. 

2. Demonstre proficiência ao utilizar a técnica de generated knowledge para analisar os dados das despesas dos deputados.  

   A técnica de generated knowledge pode ser utilizada para analisar os dados das despesas dos deputados, fornecendo insights mais profundos e contextualizados.

3. Avalie com proficiência o resultado do código de desenvolvimento das abas do dashboard com a técnica chain-of-thoughts.  

   O resultado do código pode ser avaliado em termos de:

      - Completude e robustez da arquitetura.
      - Implementação de práticas avançadas de engenharia de software e DevOps.
      - Utilização de técnicas sofisticadas de ciência de dados e machine learning.

4. Avalie com proficiência o código com a técnica de Meta-prompting para gerar as abas do dashboard numa única instrução.  

   O código pode ser avaliado em termos de:

      - Capacidade de gerar abas do dashboard numa única instrução.
      - Eficiência e escalabilidade.

---

## 4. Criar soluções a partir de Prompt Engineering

1. Avalie com profundidade os resultados do código do dashboard gerado pelas técnicas de CoT e Batch-prompting.  

   Os resultados do código do dashboard gerado pelas técnicas de CoT e Batch-prompting podem ser avaliados em termos de:

      - Completude e robustez da arquitetura.
      - Implementação de práticas avançadas de engenharia de software e DevOps.

2. Avalie com profundidade o resultado do uso de LLMs para sumarização de textos longos.  

   O resultado do uso de LLMs para sumarização de textos longos pode ser avaliado em termos de:

      - Precisão e relevância dos resumos gerados.
      - Capacidade de capturar detalhes importantes.

3. Implemente e avalie com proficiência o resultado do LLM utilizando prompts baseados em buscas em bases vetoriais.  

   
   O resultado do LLM utilizando prompts baseados em buscas em bases vetoriais pode ser avaliado em termos de:

      - Eficiência e precisão das buscas.
      - Capacidade de gerar respostas relevantes.

4. Explique com profundidade como podemos usar a técnica de Self-Ask prompting para definir as instruções de sistema de um LLM.  

   A técnica de Self-Ask prompting envolve:

      1. Decompor perguntas complexas em subperguntas.
      2. Utilizar o resultado para gerar respostas mais detalhadas e contextualizadas.

---

## 5. Utilizar técnicas Prompt Engineering para gerar imagens

1. Explique com profundidade como funciona o modelo DALL-E.  

   O modelo DALL-E é um modelo de aprendizagem profunda que utiliza uma variante da arquitetura Transformer para compreender e interpretar entradas textuais e gerar imagens.

2. Explique com profundidade como funciona o modelo MidJourney.  

   O modelo MidJourney é uma ferramenta de geração de imagens que utiliza prompts textuais para gerar imagens rapidamente, permitindo a exploração de variados conceitos e ideias.  

3. Explique com profundidade como funciona o modelo Stable Diffusion.  

   O modelo Stable Diffusion é um modelo de difusão latente que opera com representações de imagens em dimensão menor, utilizando um espaço latente de dimensão inferior ao invés do espaço real de pixels.

4. Explique com profundidade as diferenças entre as imagens geradas com diferentes prompts.  

   As imagens geradas com diferentes prompts podem variar em termos de:

   - Estilo visual.
   - Composição.
   - Relevância do conteúdo apresentado.

   As diferenças podem ser avaliadas em termos de:

   - Capacidade de capturar detalhes importantes.
   - Eficiência em transmitir a essência da proposição.
   - Criatividade e originalidade das imagens geradas.


