import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- ARQUITETURA DE FRONTIER WEB (CSS + JS EMULADO) ---
st.set_page_config(
    page_title="RLC Core Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de CSS de alta fidelidade para emular comportamento de uma SPA (Single Page Application)
st.markdown("""
    <style>
    /* Reset de fontes para emparelhamento moderno */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
        color: #171717;
    }
    
    /* Customização fina da Sidebar (estilo painel escuro JS) */
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Transformando Radio Buttons normais em Tabs estofadas de JS */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        background-color: #F1F5F9;
        padding: 4px;
        border-radius: 8px;
        gap: 2px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: transparent;
        padding: 6px 16px !important;
        border-radius: 6px;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-testid="stWidgetSelected"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
    }
    
    /* Cards de Telemetria Avançados (Visual de Glassmorphism controlado) */
    .dashboard-card {
        background: #FFFFFF;
        border: 1px solid #E4E4E7;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-2px);
        border-color: #CBD5E1;
    }
    .card-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #71717A;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .card-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.75rem;
        font-weight: 700;
        color: #09090B;
    }
    .card-sub {
        font-size: 0.85rem;
        color: #A1A1AA;
        margin-top: 4px;
    }
    
    /* Customização de Tabelas de Engenharia */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
    }
    .styled-table th {
        background-color: #F8FAFC;
        color: #64748B;
        text-align: left;
        padding: 12px;
        font-weight: 600;
        border-bottom: 2px solid #E2E8F0;
    }
    .styled-table td {
        padding: 12px;
        border-bottom: 1px solid #E2E8F0;
        color: #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO DA APLICAÇÃO WEB ---
st.markdown('<p style="font-size: 1.85rem; font-weight: 700; color: #09090B; margin-bottom: 2px;">Core Engine: Simulador RLC Fluido</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 0.95rem; color: #71717A; margin-bottom: 24px;">Instrumentação analítica de sistemas de potência em malhas senoidais permanentes.</p>', unsafe_allow_html=True)

# --- PANEL DE HARDWARE LATERAL (DOMINIO DO STATE) ---
st.sidebar.markdown('<p style="font-size: 1.15rem; font-weight: 600; margin-bottom: 16px;">⚙️ Hardware Setup</p>', unsafe_allow_html=True)

tipo_circuito = st.sidebar.radio("CONEXÃO DA ARQUITETURA:", ["Série", "Paralelo"])

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #1E293B;"></div>', unsafe_allow_html=True)

# Seletores Rápidos de Tensão e Frequência Comercial
st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: #94A3B8;">FONTE DE EXCITAÇÃO</p>', unsafe_allow_html=True)
v_comercial = st.sidebar.selectbox("Tensão Eficaz (V_rms):", ["127V (Rede Monofásica)", "220V (Rede Bifásica)", "380V (Rede Industrial)", "12V (Sinal de Controle)"])
V_rms = float(v_comercial.split("V")[0])

f_comercial = st.sidebar.selectbox("Frequência de Oscilação:", ["60 Hz (Padrão Nacional)", "50 Hz (Padrão Internacional)", "1000 Hz (Frequência de Teste)"])
freq = float(f_comercial.split(" Hz")[0])

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #1E293B;"></div>', unsafe_allow_html=True)

# Componentes da Malha organizados de maneira compacta
st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: #94A3B8;">COMPONENTES ACOPLADOS</p>', unsafe_allow_html=True)

c_r1, c_r2 = st.sidebar.columns([1, 2])
with c_r1: com_R = st.checkbox("R (Ω)", value=True, key="chk_r")
with c_r2: R_val = st.number_input("", min_value=0.1, max_value=5000.0, value=50.0, step=10.0, label_visibility="collapsed") if com_R else 0.0

c_l1, c_l2 = st.sidebar.columns([1, 2])
with c_l1: com_L = st.checkbox("L (mH)", value=True, key="chk_l")
with c_l2: L_val = st.number_input("", min_value=0.1, max_value=5000.0, value=300.0, step=50.0, label_visibility="collapsed") if com_L else 0.0

c_c1, c_c2 = st.sidebar.columns([1, 2])
with c_c1: com_C = st.checkbox("C (µF)", value=True, key="chk_c")
with c_c2: C_val = st.number_input("", min_value=0.1, max_value=2000.0, value=47.0, step=5.0, label_visibility="collapsed") if com_C else 0.0

if not com_R and not com_L and not com_C:
    st.error("Malha Aberta. Por favor, conecte ao menos um componente de carga.")
    st.stop()

# --- INSTANCIAÇÃO MATEMÁTICA DO BACKEND ---
omega = 2 * np.pi * freq
X_L = omega * (L_val / 1000.0) if com_L else 0.0
X_C = 1.0 / (omega * (C_val / 1000000.0)) if com_C else 0.0

Z_R = complex(R_val, 0)
Z_L = complex(0, X_L)
Z_C = complex(0, -X_C)

if tipo_circuito == "Série":
    Z_tot = (Z_R if com_R else 0j) + (Z_L if com_L else 0j) + (Z_C if com_C else 0j)
    I_tot = V_rms / Z_tot if abs(Z_tot) > 0 else 0j
    V_R = I_tot * Z_R if com_R else 0j
    V_L = I_tot * Z_L if com_L else 0j
    V_C = I_tot * Z_C if com_C else 0j
    correntes = {"Total": I_tot, "R": I_tot, "L": I_tot, "C": I_tot}
    tensoes = {"Total": complex(V_rms, 0), "R": V_R, "L": V_L, "C": V_C}
else:
    Y_R = 1.0 / Z_R if (com_R and R_val > 0) else 0j
    Y_L = 1.0 / Z_L if (com_L and X_L > 0) else 0j
    Y_C = 1.0 / Z_C if (com_C and X_C > 0) else 0j
    Y_tot = Y_R + Y_L + Y_C
    Z_tot = 1.0 / Y_tot if abs(Y_tot) > 0 else complex(1e9, 0)
    I_tot = V_rms * Y_tot
    I_R = V_rms / Z_R if com_R else 0j
    I_L = V_rms / Z_L if com_L else 0j
    I_C = V_rms / Z_C if com_C else 0j
    correntes = {"Total": I_tot, "R": I_R, "L": I_L, "C": I_C}
    tensoes = {"Total": complex(V_rms, 0), "R": complex(V_rms, 0), "L": complex(V_rms, 0), "C": complex(V_rms, 0)}

if abs(I_tot) < 1e-6: I_tot = 0j
fp = np.cos(np.angle(Z_tot))
caracter = "INDUTIVO" if np.angle(Z_tot) > 0.01 else "CAPACITIVO" if np.angle(Z_tot) < -0.01 else "RESISTIVO"

# --- RENDERIZAÇÃO FLUIDA DO ESPAÇO DE TRABALHO ---
col_esq, col_dir = st.columns([1, 2.2], gap="large")

with col_esq:
    st.markdown('<p style="font-size: 1rem; font-weight: 600; color: #09090B; margin-bottom: 12px;">📐 Topologia Dinâmica da Carga</p>', unsafe_allow_html=True)
    
    # Renderização vetorizada limpa do circuito (Estilo Esquema JavaScript Canvas)
    fig_esq, ax_esq = plt.subplots(figsize=(4.5, 3.5))
    ax_esq.set_xlim(-0.8, 4.8)
    ax_esq.set_ylim(-1.8, 1.8)
    ax_esq.axis('off')
    fig_esq.patch.set_facecolor('#FAFAFA')
    ax_esq.set_facecolor('#FAFAFA')
    
    # Desenho da Fonte CA Estilizada
    circle = plt.Circle((0, 0), 0.35, fill=False, color='#09090B', lw=2)
    ax_esq.add_patch(circle)
    # Onda senoidal interna na fonte
    sx = np.linspace(-0.15, 0.15, 30)
    sy = 0.15 * np.sin(2 * np.pi * sx / 0.3)
    ax_esq.plot(sx, sy, color='#09090B', lw=1.5)
    ax_esq.text(-0.4, -0.7, f" Fonte CA\n {V_rms:.0f}V", fontsize=8, fontweight='semibold', family='sans-serif')
    
    if tipo_circuito == "Série":
        ax_esq.plot([0, 0, 4, 4, 0], [0.35, 1.2, 1.2, -1.2, -1.2], color='#71717A', lw=1.5)
        ax_esq.plot([0, 0], [-0.35, -1.2], color='#71717A', lw=1.5)
        
        pos_x = 0.8
        if com_R:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#EF4444', lw=2))
            ax_esq.text(pos_x+0.12, 1.05, "R", color='#EF4444', fontsize=9, fontweight='bold', family='monospace')
            pos_x += 1.1
        if com_L:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#10B981', lw=2))
            ax_esq.text(pos_x+0.15, 1.05, "L", color='#10B981', fontsize=9, fontweight='bold', family='monospace')
            pos_x += 1.1
        if com_C:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#3B82F6', lw=2))
            ax_esq.text(pos_x+0.15, 1.05, "C", color='#3B82F6', fontsize=9, fontweight='bold', family='monospace')
    else:
        ax_esq.plot([0, 0, 3.8, 3.8], [0.35, 1.2, 1.2, -1.2], color='#71717A', lw=1.5)
        ax_esq.plot([0, 0, 3.8, 3.8], [-0.35, -1.2, -1.2, 1.2], color='#71717A', lw=1.5)
        
        pos_x = 1.2
        if com_R:
            ax_esq.plot([pos_x, pos_x], [1.2, -1.2], color='#EF4444', lw=3.5)
            ax_esq.text(pos_x+0.1, 0, "R", color='#EF4444', fontsize=9, fontweight='bold', family='monospace')
            pos_x += 1.1
        if com_L:
            ax_esq.plot([pos_x, pos_x],
