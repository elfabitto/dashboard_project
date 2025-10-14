# Dashboard de Cadastro de Clientes - Bairro Telégrafo

Este projeto contém um dashboard interativo desenvolvido em Streamlit para analisar dados de cadastro de clientes do bairro Telégrafo em Belém, focando no abastecimento de água municipal.

## Estrutura do Projeto

- `dashboard_app.py`: O código-fonte do aplicativo Streamlit que gera o dashboard interativo.
- `cleaned_client_data.csv`: O arquivo CSV contendo os dados de clientes limpos e processados.
- `static_visualizations/`: Uma pasta contendo as visualizações estáticas geradas a partir dos dados.

## Como Rodar o Dashboard Localmente

Para rodar este dashboard em seu ambiente local (por exemplo, no VS Code), siga os passos abaixo:

1.  **Clone ou Baixe o Repositório:**
    Se você estiver usando Git, clone este repositório:
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd dashboard_project
    ```
    Se você baixou o projeto como um arquivo ZIP, descompacte-o e navegue até a pasta `dashboard_project`.

2.  **Crie um Ambiente Virtual (Recomendado):**
    É uma boa prática criar um ambiente virtual para gerenciar as dependências do projeto.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Windows: .\venv\Scripts\activate
    ```

3.  **Instale as Dependências:**
    Instale as bibliotecas necessárias usando pip:
    ```bash
    pip install pandas streamlit plotly
    ```

4.  **Execute o Dashboard:**
    Com as dependências instaladas, você pode iniciar o aplicativo Streamlit:
    ```bash
    streamlit run dashboard_app.py
    ```

    Após executar o comando, o Streamlit abrirá automaticamente o dashboard em seu navegador padrão. Se não abrir, verifique o terminal para a URL local (geralmente `http://localhost:8501`).

## Visualizações Geradas

O dashboard apresenta as seguintes análises:

- Métricas principais (KPIs)
- Distribuição por Status de Ligação
- Irregularidades Identificadas
- Análise de correlação entre variáveis
- Evolução temporal de cadastros
- Média de moradores por residência
- Capacidade total de caixas d'água
- Análise de pontos de consumo

Essas visualizações podem ser usadas em relatórios ou apresentações.

Essas visualizações podem ser usadas em relatórios ou apresentações.

