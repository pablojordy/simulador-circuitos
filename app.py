import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="RLC LAB",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# CSS PROFISSIONAL
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

h1, h2, h3 {
    color: #0F172A;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] * {
    color: white;
}

.metric-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    text-align: center;
}

.metric-value {
    font-size: 30px;
    font-weight: bold;
    color: #111827;
}

.metric-label {
    font-size: 14px;
    color: #6B7280;
}

.block {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TÍTULO
# =========================================================

st.title("⚡ RLC LAB — Simulador de Circuitos")
st.caption("Análise de circuitos RLC em regime permanente senoidal")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("CONFIGURAÇÕES")

tipo = st.sidebar.selectbox(
    "Topologia",
    ["Série", "Paralelo"]
)

st.sidebar.subheader("Fonte CA")

V_rms = st.sidebar.number_input(
    "Tensão RMS (V)",
    min_value=1.0,
    value=127.0
)

freq = st.sidebar.number_input(
    "Frequência (Hz)",
    min_value=1.0,
    value=60.0
)

st.sidebar.subheader("Componentes")

R = st.sidebar.number_input(
    "Resistência R (Ω)",
    min_value=0.0,
    value=100.0
)

L_mH = st.sidebar.number_input(
    "Indutância L (mH)",
    min_value=0.0,
    value=100.0
)

C_uF = st.sidebar.number_input(
    "Capacitância C (µF)",
    min_value=0.0,
    value=47.0
)

# =========================================================
# CONVERSÕES
# =========================================================

L = L_mH / 1000
C = C_uF / 1e6

omega = 2 * np.pi * freq

# =========================================================
# REATÂNCIAS
# =========================================================

Xl = omega * L if L > 0 else 0
Xc = 1 / (omega * C) if C > 0 else 0

Zr = complex(R, 0)
Zl = complex(0, Xl)
Zc = complex(0, -Xc)

# =========================================================
# CÁLCULOS
# =========================================================

if tipo == "Série":

    Z_total = Zr + Zl + Zc

    I_total = V_rms / Z_total if abs(Z_total) > 0 else 0

    V_R = I_total * Zr
    V_L = I_total * Zl
    V_C = I_total * Zc

else:

    Y_total = 0

    if R > 0:
        Y_total += 1 / Zr

    if Xl > 0:
        Y_total += 1 / Zl

    if Xc > 0:
        Y_total += 1 / Zc

    Z_total = 1 / Y_total if Y_total != 0 else complex(0)

    I_total = V_rms / Z_total if Z_total != 0 else 0

    V_R = complex(V_rms, 0)
    V_L = complex(V_rms, 0)
    V_C = complex(V_rms, 0)

# =========================================================
# POTÊNCIAS
# =========================================================

S = V_rms * np.conj(I_total)
P = S.real
Q = S.imag
FP = np.cos(np.angle(Z_total))

# =========================================================
# RESSONÂNCIA
# =========================================================

f_res = None

if L > 0 and C > 0:
    f_res = 1 / (2 * np.pi * np.sqrt(L * C))

# =========================================================
# CLASSIFICAÇÃO
# =========================================================

angulo = np.degrees(np.angle(Z_total))

if angulo > 1:
    comportamento = "INDUTIVO"

elif angulo < -1:
    comportamento = "CAPACITIVO"

else:
    comportamento = "RESISTIVO"

# =========================================================
# MÉTRICAS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">|Z|</div>
        <div class="metric-value">{abs(Z_total):.2f} Ω</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Corrente RMS</div>
        <div class="metric-value">{abs(I_total):.3f} A</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Fator de Potência</div>
        <div class="metric-value">{FP:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Comportamento</div>
        <div class="metric-value">{comportamento}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Resultados",
    "🧭 Fasores",
    "📄 Relatório"
])

# =========================================================
# RESULTADOS
# =========================================================

with tab1:

    st.subheader("Resultados Elétricos")

    dados = pd.DataFrame({
        "Parâmetro": [
            "Resistência",
            "Reatância Indutiva",
            "Reatância Capacitiva",
            "Impedância Total",
            "Ângulo de Fase",
            "Potência Ativa",
            "Potência Reativa",
            "Potência Aparente"
        ],

        "Valor": [
            f"{R:.2f} Ω",
            f"{Xl:.2f} Ω",
            f"{Xc:.2f} Ω",
            f"{abs(Z_total):.2f} Ω",
            f"{angulo:.2f} °",
            f"{P:.2f} W",
            f"{Q:.2f} var",
            f"{abs(S):.2f} VA"
        ]
    })

    st.dataframe(dados, use_container_width=True)

    if f_res:
        st.info(f"Frequência de ressonância: {f_res:.2f} Hz")

# =========================================================
# FASORES
# =========================================================

with tab2:

    st.subheader("Diagrama Fasorial")

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.axhline(0, color='black')
    ax.axvline(0, color='black')

    ax.quiver(
        0,
        0,
        Z_total.real,
        Z_total.imag,
        angles='xy',
        scale_units='xy',
        scale=1,
        label='Z total'
    )

    ax.grid(True)

    limite = max(abs(Z_total.real), abs(Z_total.imag), 1)

    ax.set_xlim(-limite * 1.3, limite * 1.3)
    ax.set_ylim(-limite * 1.3, limite * 1.3)

    ax.set_xlabel("Parte Real")
    ax.set_ylabel("Parte Imaginária")

    ax.legend()

    st.pyplot(fig)

# =========================================================
# RELATÓRIO PDF
# =========================================================

def gerar_pdf():

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RELATÓRIO TÉCNICO - RLC LAB", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 8, f"Topologia: {tipo}", ln=True)
    pdf.cell(0, 8, f"Tensão RMS: {V_rms} V", ln=True)
    pdf.cell(0, 8, f"Frequência: {freq} Hz", ln=True)

    pdf.ln(5)

    pdf.cell(0, 8, f"R = {R} Ω", ln=True)
    pdf.cell(0, 8, f"L = {L_mH} mH", ln=True)
    pdf.cell(0, 8, f"C = {C_uF} µF", ln=True)

    pdf.ln(5)

    pdf.cell(0, 8, f"|Z| = {abs(Z_total):.2f} Ω", ln=True)
    pdf.cell(0, 8, f"I = {abs(I_total):.3f} A", ln=True)
    pdf.cell(0, 8, f"FP = {FP:.3f}", ln=True)
    pdf.cell(0, 8, f"Potência Ativa = {P:.2f} W", ln=True)
    pdf.cell(0, 8, f"Potência Reativa = {Q:.2f} var", ln=True)

    nome = "relatorio_rlc.pdf"

    pdf.output(nome)

    return nome

with tab3:

    st.subheader("Exportar Relatório Técnico")

    if st.button("Gerar Relatório PDF"):

        arquivo = gerar_pdf()

        with open(arquivo, "rb") as f:

            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name=arquivo,
                mime="application/pdf"
            )
