import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
import base64
from pathlib import Path

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

# Função para carregar e converter logo em base64
@st.cache_data
def get_logo_base64():
    try:
        logo_path = Path("logo-aguas-do-para.png")
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
    except Exception as e:
        logger.error(f"Erro ao carregar logo: {str(e)}")
    return None

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
logo_base64 = get_logo_base64()

# Configuração da página
st.set_page_config(
    page_title="Dashboard Águas do Pará",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderno e clean
st.markdown("""
    <style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary-color: #0077B6;
        --secondary-color: #00B4D8;
        --accent-color: #90E0EF;
        --background: #F8FAFB;
        --surface: #FFFFFF;
        --text: #1a1a1a;
        --text-light: #64748b;
        --border: #e2e8f0;
        --shadow: rgba(0, 119, 182, 0.08);
    }
    
    /* Background principal */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F8FAFB 0%, #EBF8FF 100%);
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFB 100%);
        border-right: 1px solid var(--border);
        box-shadow: 2px 0 12px var(--shadow);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: var(--primary-color) !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Header com logo */
    .dashboard-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px var(--shadow);
        border: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .logo-container {
        flex-shrink: 0;
    }
    
    .logo-container img {
        height: 80px;
        width: auto;
        object-fit: contain;
    }
    
    .header-content {
        flex: 1;
    }
    
    .header-title {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    .header-subtitle {
        color: var(--text-light);
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Cards de métricas modernos */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F0F9FF 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 12px var(--shadow);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 119, 182, 0.15);
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 1rem;
    }
    
    .metric-label {
        color: var(--text-light);
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    
    /* Títulos de seção */
    .section-title {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }
    
    /* Gráficos */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 12px var(--shadow);
        border: 1px solid var(--border);
    }
    
    /* Tabs modernos */
    [data-testid="stTabs"] {
        background: transparent;
    }
    
    [data-testid="stTabs"] [role="tablist"] {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 8px var(--shadow);
    }
    
    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-light);
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    [data-testid="stTabs"] [role="tab"]:hover {
        background: var(--background);
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white !important;
    }
    
    /* Divisores */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer-stats {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid var(--border);
        box-shadow: 0 2px 12px var(--shadow);
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    
    .footer-stat {
        text-align: center;
    }
    
    .footer-stat-label {
        color: var(--text-light);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .footer-stat-value {
        color: var(--primary-color);
        font-size: 1.25rem;
        font-weight: 700;
    }
    
    /* Multiselect customizado */
    [data-baseweb="select"] {
        border-radius: 8px;
    }
    
    /* Remover padding extra */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .dashboard-header {
            flex-direction: column;
            text-align: center;
        }
        
        .header-title {
            font-size: 1.5rem;
        }
        
        .logo-container img {
            height: 60px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Header com logo
if logo_base64:
    st.markdown(f"""
        <div class="dashboard-header">
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo Águas do Pará">
            </div>
            <div class="header-content">
                <h1 class="header-title">Dashboard de Cadastro de Clientes</h1>
                <p class="header-subtitle">Análise completa dos dados de abastecimento de água municipal</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="dashboard-header">
            <div class="header-content">
                <h1 class="header-title">💧 Dashboard de Cadastro de Clientes</h1>
                <p class="header-subtitle">Análise completa dos dados de abastecimento de água municipal</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.markdown("## 🔍 Filtros")

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
st.markdown('<div class="section-title">📈 Métricas Principais</div>', unsafe_allow_html=True)
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    total_clientes = len(df_selection)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-label">Total de Clientes</div>
            <div class="metric-value">{total_clientes:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    perc_hidrometro = (df_selection['POSSUI_HIDROMETRO'].value_counts(normalize=True).get('SIM', 0) * 100)
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💧</div>
            <div class="metric-label">Com Hidrômetro</div>
            <div class="metric-value">{perc_hidrometro:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    media_moradores = df_selection['NUMERO_MORADORES'].mean()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏠</div>
            <div class="metric-label">Média de Moradores</div>
            <div class="metric-value">{media_moradores:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    ligacao_clandestina = len(df_selection[df_selection['IRREGULARIDADE_IDENTIFICADA'] == 'LIGAÇÃO CLANDESTINA']) if 'IRREGULARIDADE_IDENTIFICADA' in df_selection.columns else 0
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚠️</div>
            <div class="metric-label">Ligações Clandestinas</div>
            <div class="metric-value">{ligacao_clandestina:,}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Análise Técnica Completa ---
st.markdown('<div class="section-title">📊 Análise Técnica e Operacional</div>', unsafe_allow_html=True)

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
            color_discrete_sequence=["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8"],
            hole=0.4
        )
        fig_ligacao.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            margin=dict(t=50, b=20, l=20, r=20)
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
            color_discrete_sequence=["#FF6B6B", "#4ECDC4", "#FFE66D"],
            hole=0.4
        )
        fig_irregularidade.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            margin=dict(t=50, b=20, l=20, r=20)
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
            color_discrete_sequence=["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8", "#ADE8F4"],
            hole=0.4
        )
        fig_edificacao.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            margin=dict(t=50, b=20, l=20, r=20)
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
            color_continuous_scale=["#90E0EF", "#00B4D8", "#0077B6"]
        )
        fig_logradouro.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            yaxis={"categoryorder": "total ascending"},
            margin=dict(t=50, b=40, l=20, r=20)
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
            color_discrete_sequence=["#0077B6"]
        )
        fig_quadra.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            xaxis_title="Quadra",
            yaxis_title="Quantidade",
            showlegend=False,
            xaxis=dict(type="category"),
            margin=dict(t=50, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_quadra, use_container_width=True, key="quadra_chart")

st.markdown("---")

# Row 3 - Tipo de Visita
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
                    color="#0077B6",
                    line=dict(color="#00B4D8", width=2)
                ),
                text=visita_dist["Quantidade"],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
            )
        ])
        fig_visita.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title="Distribuição por Tipo de Visita",
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            xaxis_title="Quantidade",
            yaxis_title="Tipo",
            height=400,
            showlegend=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(t=50, b=40, l=20, r=40)
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

# Footer com estatísticas
st.markdown(f"""
    <div class="footer-stats">
        <div class="footer-stat">
            <div class="footer-stat-label">Total de Registros</div>
            <div class="footer-stat-value">{len(df_selection):,}</div>
        </div>
        <div class="footer-stat">
            <div class="footer-stat-label">Municípios</div>
            <div class="footer-stat-value">{df_selection['MUNICIPIO'].nunique()}</div>
        </div>
        <div class="footer-stat">
            <div class="footer-stat-label">Bairros Analisados</div>
            <div class="footer-stat-value">{df_selection['BAIRRO'].nunique()}</div>
        </div>
        <div class="footer-stat">
            <div class="footer-stat-label">Última Atualização</div>
            <div class="footer-stat-value">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        </div>
    </div>
""", unsafe_allow_html=True)
