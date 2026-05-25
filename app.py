import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- CONFIGURAÇÃO DA INTERFACE SOFISTICADA ---
st.set_page_config(
    page_title="Simulador Avançado de Circuitos RLC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para um visual moderno
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #FF4B4B; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #555555; margin-bottom: 25px; }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #FF4B4B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ Laboratório Virtual de Circuitos RLC Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Projete, analise fasores e exporte relatórios técnicos de malhas em CA.</div>', unsafe_allow_html=True)

# --- SIDEBAR INTERATIVA: ARQUITETURA DO CIRCUITO ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3067/3067349.png", width=60)
st.sidebar.header("🛠️ Configuração da Rede")

tipo_circuito = st.sidebar.radio(
    "Topologia da Malha:",
    ["Série", "Paralelo"],
    help="Escolha se os componentes compartilham a mesma corrente (Série) ou a mesma tensão (Paralelo)."
)

st.sidebar.subheader("🔌 Parâmetros da Fonte de CA")
V_rms = st.sidebar.slider("Tensão da Fonte (V_rms)", min_value=1.0, max_value=440.0, value=127.0, step=1.0)
freq = st.sidebar.slider("Frequência de Operação (Hz)", min_value=1.0, max_value=1000.0, value=60.0, step=5.0)

st.sidebar.subheader("📦 Bancada de Componentes")
st.sidebar.caption("Ative e ajuste as propriedades de cada dispositivo:")

# Checkboxes para simular a inserção/remoção de componentes na bancada
com_R = st.sidebar.checkbox("Incluir Resistor (R)", value=True)
R_val = st.sidebar.number_input("Resistência (Ω)", min_value=0.1, max_value=10000.0, value=50.0, step=1.0) if com_R else 0.0

com_L = st.sidebar.checkbox("Incluir Indutor (L)", value=True)
L_val = st.sidebar.number_input("Indutância (mH)", min_value=0.1, max_value=5000.0, value=300.0, step=10.0) if com_L else 0.0

com_C = st.sidebar.checkbox("Incluir Capacitor (C)", value=True)
C_val = st.sidebar.number_input("Capacitância (µF)", min_value=0.1, max_value=2000.0, value=47.0, step=1.0) if com_C else 0.0

# --- NÚCLEO DE CÁLCULO ENGENHARIA ELÉTRICA ---
omega = 2 * np.pi * freq
L_henry = (L_val / 1000) if (com_L and L_val > 0) else 1e-9
C_farad = (C_val / 1000000) if (com_C and C_val > 0) else 1e9

# Cálculo das Reatâncias Isoladas
X_L = omega * L_henry if com_L else 0.0
X_C = (1 / (omega * C_farad)) if com_C else 0.0

# Montagem das impedâncias complexas individuais
Z_R = complex(R_val, 0) if com_R else (1e-9 if tipo_circuito == "Série" else 1e9)
Z_L = complex(0, X_L) if com_L else (1e-9
