import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define expected columns and their types
EXPECTED_COLUMNS = {
    'MUNICIPIO': 'string',
    'BAIRRO': 'string',
    'TIPO_CADASTRO': 'string',
    'STATUS': 'string',
    'IRREGULARIDADE_IDENTIFICADA': 'string',
    'SITUACAO_HIDROMETRO': 'string',
    'TIPO_EDIFICACAO': 'string',
    'FONTE_ALTERNATIVA': 'string',
    'NUMERO_MORADORES': 'float64',
    'CAPACIDADE_CAIXA_LITROS': 'float64'
}

# Load the cleaned data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "cleaned_client_data.csv",
            encoding='utf-8',
            sep=',',
            low_memory=False
        )
        
        # Mapeamento de colunas
        column_mapping = {
            'TOTAL_DE_MORADORES': 'NUMERO_MORADORES',
            'QUANTOS_LITROS_TOTAIS': 'CAPACIDADE_CAIXA_LITROS',
            'STATUS': 'STATUS_LIGACAO',
            'SITUACAO_HIDROMETRO': 'POSSUI_HIDROMETRO',
            'TIPO_EDIFICACAO': 'PADRAO_IMOVEL'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]

        for col, dtype in EXPECTED_COLUMNS.items():
            if col in df.columns:
                try:
                    if dtype == 'string':
                        df[col] = df[col].fillna('Não informado').astype('string')
                    elif dtype == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                except Exception as e:
                    logger.error(f"Erro ao converter coluna {col}: {str(e)}")

        df['POSSUI_HIDROMETRO'] = df['SITUACAO_HIDROMETRO'].apply(
            lambda x: 'SIM' if x in ['NORMAL', 'QUEBRADO'] else 'NÃO'
        )
        
        return df

    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Configuração de tema escuro
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSS para tema claro com azul água
st.markdown("""
    <style>
    :root {
        --primary-color: #0077B6;
        --secondary-color: #00B4D8;
        --accent-color: #00D9FF;
        --background: #F8FAFB;
        --surface: #FFFFFF;
        --text: #1a1a1a;
        --text-light: #5a6c7d;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--background);
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 3px solid var(--secondary-color);
    }
    
    [data-testid="stHeader"] {
        background-color: var(--surface);
        border-bottom: 3px solid var(--secondary-color);
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--surface) 0%, #F0F9FF 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        border-left: 5px solid var(--primary-color);
        box-shadow: 0 4px 12px rgba(0, 119, 182, 0.12);
    }
    
    .big-number {
        color: var(--primary-color);
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        color: var(--text-light);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 700;
    }
    
    p, span, div {
        color: var(--text) !important;
    }
    
    [data-testid="stTabs"] [role="tablist"] {
        background-color: transparent;
        border-bottom: 2px solid var(--secondary-color);
    }
    
    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-light) !important;
        background-color: transparent;
        border-bottom: 3px solid transparent;
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        border-bottom: 3px solid var(--primary-color) !important;
        color: var(--primary-color) !important;
    }
    
    hr {
        border-color: var(--secondary-color) !important;
        opacity: 0.3;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Cadastro de Clientes - Abastecimento de Água")
st.markdown("Análise completa dos dados de cadastro de clientes da empresa de abastecimento municipal")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filtros")

selected_municipio = st.sidebar.multiselect(
    "Selecionar Município",
    options=df["MUNICIPIO"].unique(),
    default=df["MUNICIPIO"].unique()
)

selected_bairro = st.sidebar.multiselect(
    "Selecionar Bairro",
    options=df[df["MUNICIPIO"].isin(selected_municipio)]["BAIRRO"].unique(),
    default=df[df["MUNICIPIO"].isin(selected_municipio)]["BAIRRO"].unique()
)

df_selection = df[df["MUNICIPIO"].isin(selected_municipio) & df["BAIRRO"].isin(selected_bairro)]

# --- KPI Metrics Section ---
st.subheader("📈 Métricas Principais")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    total_clientes = len(df_selection)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total de Clientes</div>
            <div class="big-number">{total_clientes:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    perc_hidrometro = (df_selection['POSSUI_HIDROMETRO'].value_counts(normalize=True).get('SIM', 0) * 100)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Percentual de Residências com Hidrômetro Instalado</div>
            <div class="big-number">{perc_hidrometro:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    media_moradores = df_selection['NUMERO_MORADORES'].mean()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Média de Moradores por Imóvel</div>
            <div class="big-number">{media_moradores:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    ligacao_clandestina = len(df_selection[df_selection['IRREGULARIDADE_IDENTIFICADA'] == 'LIGAÇÃO CLANDESTINA']) if 'IRREGULARIDADE_IDENTIFICADA' in df_selection.columns else 0
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ligações Clandestinas</div>
            <div class="big-number">{ligacao_clandestina:,}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Análise Técnica Completa ---
st.subheader("📊 Análise Técnica e Operacional")

# Row 1 - Gráficos de Pizza
col1, col2, col3 = st.columns(3)

with col1:
    if not df_selection.empty and "SITUACAO_LIGACAO" in df_selection.columns:
        ligacao_dist = df_selection["SITUACAO_LIGACAO"].value_counts().reset_index()
        ligacao_dist.columns = ["Status", "Contagem"]
        fig_ligacao = px.pie(
            ligacao_dist,
            values="Contagem",
            names="Status",
            title="Status de Ligação",
            color_discrete_sequence=["#00D9FF", "#1f77b4", "#ff7f0e", "#2ca02c"],
            hole=0.4
        )
        fig_ligacao.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=11)
        )
        st.plotly_chart(fig_ligacao, use_container_width=True, key="ligacao_chart")

with col2:
    if not df_selection.empty and "IRREGULARIDADE_IDENTIFICADA" in df_selection.columns:
        irregularidade_dist = df_selection["IRREGULARIDADE_IDENTIFICADA"].value_counts().reset_index()
        irregularidade_dist.columns = ["Irregularidade", "Contagem"]
        fig_irregularidade = px.pie(
            irregularidade_dist,
            values="Contagem",
            names="Irregularidade",
            title="Irregularidades Identificadas",
            color_discrete_sequence=["#FF6B6B", "#4ECDC4"],
            hole=0.4
        )
        fig_irregularidade.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=11)
        )
        st.plotly_chart(fig_irregularidade, use_container_width=True, key="irregularidade_chart")

with col3:
    if not df_selection.empty and "TIPO_EDIFICACAO" in df_selection.columns:
        edificacao_dist = df_selection["TIPO_EDIFICACAO"].value_counts().reset_index()
        edificacao_dist.columns = ["Tipo", "Contagem"]
        fig_edificacao = px.pie(
            edificacao_dist,
            values="Contagem",
            names="Tipo",
            title="Tipo de Edificação",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_edificacao.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=11)
        )
        st.plotly_chart(fig_edificacao, use_container_width=True, key="edificacao_chart")

st.markdown("---")

# Row 2 - Gráficos de Barras
col4, col5 = st.columns(2)

with col4:
    if not df_selection.empty and "LOGRADOURO" in df_selection.columns:
        logradouro_dist = df_selection["LOGRADOURO"].value_counts().head(15).reset_index()
        logradouro_dist.columns = ["Rua", "Quantidade"]
        fig_logradouro = px.bar(
            logradouro_dist,
            x="Quantidade",
            y="Rua",
            orientation="h",
            title="Top 15 Ruas com Mais Clientes",
            color="Quantidade",
            color_continuous_scale="Viridis"
        )
        fig_logradouro.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=11),
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_logradouro, use_container_width=True, key="logradouro_chart")

with col5:
    if not df_selection.empty and "QUADRA" in df_selection.columns:
        quadra_dist = df_selection["QUADRA"].value_counts().reset_index()
        quadra_dist.columns = ["Quadra", "Quantidade"]
        quadra_dist = quadra_dist.sort_values("Quadra")
        
        fig_quadra = px.bar(
            quadra_dist,
            x="Quadra",
            y="Quantidade",
            title="Quantitativo de Clientes por Quadra",
            color_discrete_sequence=["#DD831B"]
        )
        fig_quadra.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=11),
            xaxis_title="Quadra",
            yaxis_title="Quantidade",
            showlegend=False,
            xaxis=dict(type="category")
        )
        st.plotly_chart(fig_quadra, use_container_width=True, key="quadra_chart")

st.markdown("---")

# Row 3 - Tipo de Visita (Gráfico diferenciado)
col6, col7 = st.columns([1.2, 1])

with col6:
    if not df_selection.empty and "TIPO_VISITA" in df_selection.columns:
        visita_dist = df_selection["TIPO_VISITA"].value_counts().reset_index()
        visita_dist.columns = ["Tipo de Visita", "Quantidade"]
        
        fig_visita = go.Figure(data=[
            go.Bar(
                y=visita_dist["Tipo de Visita"],
                x=visita_dist["Quantidade"],
                orientation="h",
                marker=dict(
                    color="#0077B6"
                ),
                text=visita_dist["Quantidade"],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
            )
        ])
        fig_visita.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248, 250, 251, 0)",
            font=dict(color="#1a1a1a", size=12),
            title="Distribuição por Tipo de Visita",
            xaxis_title="Quantidade",
            yaxis_title="Tipo",
            height=400,
            showlegend=False,
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_visita, use_container_width=True, key="visita_chart")

with col7:
    if not df_selection.empty and "NUMERO_MORADORES" in df_selection.columns:
        st.markdown("### 📊 Distribuição de Moradores")
        
        moradores_stats = df_selection["NUMERO_MORADORES"].describe()
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.metric("Mínimo", f"{moradores_stats['min']:.0f}")
            st.metric("Mediana", f"{moradores_stats['50%']:.1f}")
        
        with col_m2:
            st.metric("Máximo", f"{moradores_stats['max']:.0f}")
            st.metric("Desvio Padrão", f"{moradores_stats['std']:.2f}")

st.markdown("---")

# Footer
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown(f"**Total de Registros:** {len(df_selection):,}")

with col_footer2:
    st.markdown(f"**Bairros Analisados:** {df_selection['BAIRRO'].nunique()}")

with col_footer3:
    st.markdown(f"*Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")