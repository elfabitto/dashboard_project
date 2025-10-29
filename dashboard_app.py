import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
import base64
from pathlib import Path
import tempfile
import os
import io
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define expected columns and their types
EXPECTED_COLUMNS = {
    'MUNICIPIO': 'string',
    'BAIRRO': 'string',
    'TIPO_CADASTRO': 'string',
    'SITUACAO_LIGACAO': 'string',
    'IRREGULARIDADE_IDENTIFICADA': 'string',
    'SITUACAO_HIDROMETRO': 'string',
    'TIPO_EDIFICACAO': 'string',
    'FONTE_ALTERNATIVA': 'string',
    'TOTAL_DE_MORADORES': 'float64',
    'QUANTOS_LITROS_TOTAIS': 'float64',
    'PADRAO_DO_IMOVEL': 'string',
    'LOGRADOURO': 'string',
    'QUADRA': 'string',
    'TIPO_VISITA': 'string'
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

def _save_uploaded_file(uploaded_file) -> str:
    """Salva uploaded_file (Streamlit UploadedFile) em arquivo temporário e retorna o caminho."""
    try:
        suffix = Path(uploaded_file.name).suffix
        tmp_dir = tempfile.gettempdir()
        tmp_src = os.path.join(tmp_dir, f"uploaded_{int(time.time())}{suffix}")
        with open(tmp_src, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return tmp_src
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo enviado: {e}")
        raise


# Processa o DataFrame carregado (conversões e otimizações)
def process_loaded_df(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Processar colunas
        for col, dtype in EXPECTED_COLUMNS.items():
            if col in df.columns:
                try:
                    if dtype == 'string':
                        df[col] = df[col].fillna('Não informado').astype('string')
                    elif dtype == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                except Exception as e:
                    logger.error(f"Erro ao converter coluna {col}: {str(e)}")

        # Criar coluna auxiliar para hidrômetro
        if 'SITUACAO_HIDROMETRO' in df.columns:
            df['POSSUI_HIDROMETRO'] = df['SITUACAO_HIDROMETRO'].apply(
                lambda x: 'SIM' if pd.notna(x) and str(x).upper() in ['NORMAL', 'QUEBRADO', 'INSTALADO'] else 'NÃO'
            )

        # Garantir que colunas numéricas existam
        if 'TOTAL_DE_MORADORES' not in df.columns:
            df['TOTAL_DE_MORADORES'] = 0
        if 'QUANTOS_LITROS_TOTAIS' not in df.columns:
            df['QUANTOS_LITROS_TOTAIS'] = 0

        # --- Otimizações de tipos para reduzir uso de memória e payload ---
        try:
            category_cols = [
                'MUNICIPIO','BAIRRO','STATUS','SITUACAO_LIGACAO',
                'TIPO_VISITA','PADRAO_DO_IMOVEL','IRREGULARIDADE_IDENTIFICADA','TIPO_EDIFICACAO'
            ]
            for col in category_cols:
                if col in df.columns:
                    df[col] = df[col].astype('category')

            # downcast em colunas numéricas conhecidas
            for col in ['TOTAL_DE_MORADORES','QUANTOS_LITROS_TOTAIS']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('float32')
        except Exception as e:
            logger.debug(f"Não foi possível otimizar tipos: {e}")
            pass

        return df
    except Exception as e:
        logger.error(f"Erro ao processar DataFrame: {e}")
        return df


# Load the data from a given path (cached by path)
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        if path.lower().endswith('.parquet'):
            df = pd.read_parquet(path)
        elif path.lower().endswith('.csv'):
            df = pd.read_csv(path)
        else:
            # assume excel
            df = pd.read_excel(path, engine='openpyxl')

        logger.info(f"Dados carregados de {path}: {len(df)} registros")
        return process_loaded_df(df)
    except Exception as e:
        logger.error(f"Erro ao carregar dados de {path}: {e}")
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()
    try:
        # Carregar diretamente do Excel
        df = pd.read_excel(
            "BASE_GERAL_2025_10_25 VS01.xlsx",
            engine='openpyxl'
        )
        
        logger.info(f"Dados carregados: {len(df)} registros")
        
        # Processar colunas
        for col, dtype in EXPECTED_COLUMNS.items():
            if col in df.columns:
                try:
                    if dtype == 'string':
                        df[col] = df[col].fillna('Não informado').astype('string')
                    elif dtype == 'float64':
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                except Exception as e:
                    logger.error(f"Erro ao converter coluna {col}: {str(e)}")

        # Criar coluna auxiliar para hidrômetro
        if 'SITUACAO_HIDROMETRO' in df.columns:
            df['POSSUI_HIDROMETRO'] = df['SITUACAO_HIDROMETRO'].apply(
                lambda x: 'SIM' if pd.notna(x) and str(x).upper() in ['NORMAL', 'QUEBRADO', 'INSTALADO'] else 'NÃO'
            )
        
        # Garantir que colunas numéricas existam
        if 'TOTAL_DE_MORADORES' not in df.columns:
            df['TOTAL_DE_MORADORES'] = 0
        if 'QUANTOS_LITROS_TOTAIS' not in df.columns:
            df['QUANTOS_LITROS_TOTAIS'] = 0
        # --- Otimizações de tipos para reduzir uso de memória e payload ---
        try:
            category_cols = [
                'MUNICIPIO','BAIRRO','STATUS','SITUACAO_LIGACAO',
                'TIPO_VISITA','PADRAO_DO_IMOVEL','IRREGULARIDADE_IDENTIFICADA','TIPO_EDIFICACAO'
            ]
            for col in category_cols:
                if col in df.columns:
                    # converter para category reduz consideravelmente o tamanho em memória
                    df[col] = df[col].astype('category')

            # downcast em colunas numéricas conhecidas
            for col in ['TOTAL_DE_MORADORES','QUANTOS_LITROS_TOTAIS']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('float32')
        except Exception as e:
            logger.debug(f"Não foi possível otimizar tipos: {e}")
            pass
            
        return df

    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# logo
logo_base64 = get_logo_base64()

# --- Input de arquivo pelo usuário (sidebar) ---
st.sidebar.markdown("## 🔁 Input de Planilha")
uploaded_file = st.sidebar.file_uploader("Faça upload da planilha (xlsx/csv)", type=['xlsx','xls','csv'])
if uploaded_file is not None:
    try:
        tmp_src = _save_uploaded_file(uploaded_file)
        convert_to_parquet = st.sidebar.checkbox("Converter para formato leve (parquet) temporário", value=True)
        if convert_to_parquet:
            parquet_path = f"{tmp_src}.parquet"
            try:
                # ler arquivo original e salvar como parquet
                if tmp_src.lower().endswith(('.xls', '.xlsx')):
                    df_tmp = pd.read_excel(tmp_src, engine='openpyxl')
                else:
                    df_tmp = pd.read_csv(tmp_src)
                df_tmp.to_parquet(parquet_path, index=False)
                st.sidebar.success("Arquivo convertido para parquet temporário e será usado no painel.")
                st.session_state['uploaded_path'] = parquet_path
            except Exception as e:
                logger.error(f"Falha ao converter para parquet: {e}")
                st.sidebar.warning("Não foi possível converter para parquet; o arquivo original será usado.")
                st.session_state['uploaded_path'] = tmp_src
        else:
            st.session_state['uploaded_path'] = tmp_src
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar o arquivo enviado: {e}")

# Determinar caminho dos dados: se o usuário enviou, usar isso; senão usar arquivo local
data_path = st.session_state.get('uploaded_path', None)
if data_path:
    df = load_data(data_path)
else:
    # Não carregar mais arquivo local por padrão. Inicializar DataFrame vazio
    st.sidebar.info("Nenhum arquivo carregado. Faça upload da planilha na seção 'Input de Planilha' para visualizar dados.")
    df = pd.DataFrame()


def prepare_map_points(df_map, max_points=5000):
    """Reduz o número de pontos para o mapa por amostragem ou agregação espacial.
    Retorna (df_plot, info) onde info é uma string com mensagem quando ocorreu redução.
    """
    try:
        n = len(df_map)
        if n <= max_points:
            return df_map.copy(), None

        # Tentar agregar por grid (arredondando coordenadas) para reduzir pontos
        df_tmp = df_map.copy()
        df_tmp['lat_r'] = df_tmp['LATITUDE'].round(3)
        df_tmp['lon_r'] = df_tmp['LONGITUDE'].round(3)
        df_agg = df_tmp.groupby(['lat_r', 'lon_r', 'STATUS']).size().reset_index(name='count')
        df_agg = df_agg.rename(columns={'lat_r': 'LATITUDE', 'lon_r': 'LONGITUDE'})

        info = f"Dados do mapa reduzidos: {n} -> {len(df_agg)} pontos (agregação por grid)."
        return df_agg, info
    except Exception as e:
        logger.debug(f"prepare_map_points falhou: {e}")
        # fallback: amostragem simples
        try:
            df_samp = df_map.sample(n=min(len(df_map), max_points), random_state=42)
            info = f"Dados do mapa amostrados para {len(df_samp)} pontos (fallback)."
            return df_samp, info
        except Exception:
            return df_map.copy(), None

# Configuração da página
st.set_page_config(
    page_title="Painel Diário Águas do Pará",
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

if not df.empty:
    selected_municipio = st.sidebar.multiselect(
        "Selecionar Município",
        options=sorted(df["MUNICIPIO"].unique()),
        default=sorted(df["MUNICIPIO"].unique())
    )

    selected_bairro = st.sidebar.multiselect(
        "Selecionar Bairro",
        options=sorted(df[df["MUNICIPIO"].isin(selected_municipio)]["BAIRRO"].unique()),
        default=sorted(df[df["MUNICIPIO"].isin(selected_municipio)]["BAIRRO"].unique())
    )

    # Filtro por STATUS
    if "STATUS" in df.columns:
        status_options = sorted([s for s in df["STATUS"].unique() if pd.notna(s)])
        selected_status = st.sidebar.multiselect(
            "Selecionar Status",
            options=status_options,
            default=status_options
        )
        df_selection = df[
            df["MUNICIPIO"].isin(selected_municipio) & 
            df["BAIRRO"].isin(selected_bairro) &
            df["STATUS"].isin(selected_status)
        ]
    else:
        df_selection = df[df["MUNICIPIO"].isin(selected_municipio) & df["BAIRRO"].isin(selected_bairro)]
else:
    st.error("Não foi possível carregar os dados.")
    st.stop()

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
    if 'POSSUI_HIDROMETRO' in df_selection.columns:
        perc_hidrometro = (df_selection['POSSUI_HIDROMETRO'].value_counts(normalize=True).get('SIM', 0) * 100)
    else:
        perc_hidrometro = 0
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💧</div>
            <div class="metric-label">Com Hidrômetro</div>
            <div class="metric-value">{perc_hidrometro:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    media_moradores = df_selection['TOTAL_DE_MORADORES'].mean() if 'TOTAL_DE_MORADORES' in df_selection.columns else 0
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🏠</div>
            <div class="metric-label">Média de Moradores</div>
            <div class="metric-value">{media_moradores:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    ligacao_clandestina = len(df_selection[df_selection['IRREGULARIDADE_IDENTIFICADA'].str.contains('CLANDESTINA', case=False, na=False)]) if 'IRREGULARIDADE_IDENTIFICADA' in df_selection.columns else 0
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚠️</div>
            <div class="metric-label">Ligações Clandestinas</div>
            <div class="metric-value">{ligacao_clandestina:,}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Gráfico de STATUS e Mapa ---
st.markdown('<div class="section-title">📋 Distribuição por Status</div>', unsafe_allow_html=True)

col_status = st.container()

with col_status:
    if not df_selection.empty and "STATUS" in df_selection.columns:
        status_dist = df_selection["STATUS"].value_counts().reset_index()
        status_dist.columns = ["Status", "Contagem"]
        
        # Definir cores específicas para cada status
        color_map = {
            'COLETAR': '#0077B6',  # Azul
            'VALIDAR': '#FFD700',  # Amarelo
            'REAMBULADO': '#28A745',  # Verde
            'AGUARDANDO CADASTRO': '#FF8C00',  # Laranja
            'EXCLUIR': '#000000',  # Preto
            'CORRIGIR': '#DC3545'  # Vermelho
        }
        
        # Criar lista de cores na ordem dos status
        colors = [color_map.get(status.upper(), '#808080') for status in status_dist['Status']]
        
        fig_status = px.pie(
            status_dist,
            values="Contagem",
            names="Status",
            title="Distribuição por Status do Cadastro",
            color_discrete_sequence=colors,
            hole=0.4
        )
        fig_status.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=14, family="Inter"),
            title_font=dict(size=18, color="#0077B6", family="Inter"),
            margin=dict(t=60, b=40, l=40, r=40),
            height=500
        )
        fig_status.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )
        st.plotly_chart(fig_status, use_container_width=True, key="status_chart")

# Mapa removido por opção do usuário (pode pesar muito).

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

# Row 3 - Tipo de Visita e Padrão do Imóvel
col6, col7 = st.columns(2)

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
    if not df_selection.empty and "PADRAO_DO_IMOVEL" in df_selection.columns:
        padrao_dist = df_selection["PADRAO_DO_IMOVEL"].value_counts().reset_index()
        padrao_dist.columns = ["Padrão", "Quantidade"]
        
        fig_padrao = px.bar(
            padrao_dist,
            x="Padrão",
            y="Quantidade",
            title="Distribuição por Padrão do Imóvel",
            color_discrete_sequence=["#00B4D8"]
        )
        fig_padrao.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a1a", size=12, family="Inter"),
            title_font=dict(size=16, color="#0077B6", family="Inter"),
            xaxis_title="Padrão",
            yaxis_title="Quantidade",
            showlegend=False,
            margin=dict(t=50, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_padrao, use_container_width=True, key="padrao_chart")

st.markdown("---")

# Estatísticas de Moradores
if not df_selection.empty and "TOTAL_DE_MORADORES" in df_selection.columns:
    st.markdown('<div class="section-title">👨‍👩‍👧‍👦 Análise de Moradores</div>', unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    moradores_stats = df_selection["TOTAL_DE_MORADORES"].describe()
    
    with col_m1:
        st.metric("Mínimo", f"{moradores_stats['min']:.0f}")
    
    with col_m2:
        st.metric("Média", f"{moradores_stats['mean']:.1f}")
    
    with col_m3:
        st.metric("Mediana", f"{moradores_stats['50%']:.1f}")
    
    with col_m4:
        st.metric("Máximo", f"{moradores_stats['max']:.0f}")

st.markdown("---")

# --- Nova Aba de Produtividade ---
st.markdown('<div class="section-title">🏆 Produtividade de Reambuladores</div>', unsafe_allow_html=True)

# Filtros de data
col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 2, 2])

with col_filtro1:
    tipo_filtro = st.selectbox(
        "Tipo de Filtro",
        ["Por Período", "Por Mês"],
        key="tipo_filtro_reambulador"
    )

# Converter DATA_COLETA para datetime se existir
if 'DATA_COLETA' in df_selection.columns:
    df_selection_copy = df_selection.copy()
    df_selection_copy['DATA_COLETA'] = pd.to_datetime(df_selection_copy['DATA_COLETA'], errors='coerce')
    
    if tipo_filtro == "Por Período":
        with col_filtro2:
            # Obter datas mínima e máxima
            data_min = df_selection_copy['DATA_COLETA'].min()
            data_max = df_selection_copy['DATA_COLETA'].max()
            
            if pd.notna(data_min) and pd.notna(data_max):
                data_inicio = st.date_input(
                    "Data Início",
                    value=data_min.date(),
                    min_value=data_min.date(),
                    max_value=data_max.date(),
                    key="data_inicio_reambulador"
                )
        
        with col_filtro3:
            if pd.notna(data_min) and pd.notna(data_max):
                data_fim = st.date_input(
                    "Data Fim",
                    value=data_max.date(),
                    min_value=data_min.date(),
                    max_value=data_max.date(),
                    key="data_fim_reambulador"
                )
                
                # Filtrar por período
                df_filtrado = df_selection_copy[
                    (df_selection_copy['DATA_COLETA'].dt.date >= data_inicio) &
                    (df_selection_copy['DATA_COLETA'].dt.date <= data_fim)
                ]
            else:
                st.warning("Não há dados de data disponíveis")
                df_filtrado = df_selection_copy
    else:  # Por Mês
        with col_filtro2:
            # Criar lista de meses disponíveis
            df_selection_copy['ANO_MES'] = df_selection_copy['DATA_COLETA'].dt.to_period('M')
            meses_disponiveis = sorted(df_selection_copy['ANO_MES'].dropna().unique(), reverse=True)
            
            if len(meses_disponiveis) > 0:
                mes_selecionado = st.selectbox(
                    "Selecione o Mês",
                    options=meses_disponiveis,
                    format_func=lambda x: x.strftime('%B/%Y') if pd.notna(x) else 'N/A',
                    key="mes_reambulador"
                )
                
                # Filtrar por mês
                df_filtrado = df_selection_copy[df_selection_copy['ANO_MES'] == mes_selecionado]
            else:
                st.warning("Não há dados de data disponíveis")
                df_filtrado = df_selection_copy
else:
    st.warning("Coluna DATA_COLETA não encontrada nos dados")
    df_filtrado = df_selection

st.markdown("---")

# Criar ranking de reambuladores
if 'REAMBULADOR' in df_filtrado.columns and not df_filtrado.empty:
    # Contar quantas vezes cada reambulador aparece (número de visitas)
    ranking = df_filtrado['REAMBULADOR'].value_counts().reset_index()
    ranking.columns = ['Reambulador', 'Número de Visitas']
    
    # Converter para string e remover valores nulos ou vazios
    ranking['Reambulador'] = ranking['Reambulador'].astype(str)
    ranking = ranking[ranking['Reambulador'].notna() & (ranking['Reambulador'] != '') & (ranking['Reambulador'] != 'nan')]
    
    # Remover valores nulos ou vazios
    ranking = ranking[ranking['Reambulador'].notna() & (ranking['Reambulador'] != '')]
    
    if not ranking.empty:
        # Métricas principais
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">👥</div>
                    <div class="metric-label">Total de Reambuladores</div>
                    <div class="metric-value">{len(ranking)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">📊</div>
                    <div class="metric-label">Total de Visitas</div>
                    <div class="metric-value">{ranking['Número de Visitas'].sum():,}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">🏆</div>
                    <div class="metric-label">Melhor Performance</div>
                    <div class="metric-value">{ranking.iloc[0]['Número de Visitas']:,} visitas</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gráfico de ranking e tabela
        col_grafico, col_tabela = st.columns([2, 1])
        
        with col_grafico:
            # Gráfico de barras horizontal
            fig_ranking = go.Figure(data=[
                go.Bar(
                    y=ranking['Reambulador'],
                    x=ranking['Número de Visitas'],
                    orientation='h',
                    marker=dict(
                        color=ranking['Número de Visitas'],
                        colorscale='Blues',
                        line=dict(color='#0077B6', width=1)
                    ),
                    text=ranking['Número de Visitas'],
                    textposition='outside',
                    hovertemplate="<b>%{y}</b><br>Visitas: %{x}<extra></extra>"
                )
            ])
            
            fig_ranking.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a1a", size=12, family="Inter"),
                title="Ranking de Reambuladores por Número de Visitas",
                title_font=dict(size=18, color="#0077B6", family="Inter"),
                xaxis_title="Número de Visitas",
                yaxis_title="Reambulador",
                height=max(400, len(ranking) * 25),
                showlegend=False,
                yaxis={"categoryorder": "total ascending"},
                margin=dict(t=60, b=40, l=200, r=40)
            )
            
            st.plotly_chart(fig_ranking, use_container_width=True, key="ranking_reambulador")
        
        with col_tabela:
            st.markdown("#### 📋 Ranking Completo")
            
            # Adicionar posição no ranking
            ranking_display = ranking.copy()
            ranking_display.insert(0, 'Posição', range(1, len(ranking_display) + 1))
            # Mostrar apenas top 100 na tabela para evitar envio massivo ao frontend
            max_show = 100
            st.dataframe(
                ranking_display.head(max_show),
                hide_index=True,
                use_container_width=True,
                height=max(400, min(len(ranking), max_show) * 35 + 38)
            )

            # Oferecer download do CSV completo
            try:
                csv_bytes = ranking.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV (completo)", csv_bytes, file_name='ranking_reambulador.csv', mime='text/csv')
            except Exception:
                # se algo falhar, apenas permitir copiar por clipboard
                st.markdown("Não foi possível gerar o arquivo para download.")
    else:
        st.warning("Não há dados de reambuladores para o período selecionado")
else:
    st.warning("Coluna REAMBULADOR não encontrada nos dados ou não há dados disponíveis")

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
