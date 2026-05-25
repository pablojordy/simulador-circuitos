import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Simulador de Circuitos RLC", layout="wide")
st.title("⚡ Simulador de Circuito Elétrico Simplificado")
st.write("Calcule circuitos RLC (Série/Paralelo) e gere o relatório com diagrama fasorial.")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("Parâmetros do Circuito")
tipo_circuito = st.sidebar.selectbox("Configuração do Circuito", ["Série", "Paralelo"])

V_rms = st.sidebar.number_input("Tensão da Fonte (V_rms)", min_value=0.1, value=127.0, step=1.0)
freq = st.sidebar.number_input("Frequência (Hz)", min_value=0.1, value=60.0, step=1.0)

R = st.sidebar.number_input("Resistência R (Ohms)", min_value=0.0, value=10.0, step=1.0)
L_mH = st.sidebar.number_input("Indutância L (mH)", min_value=0.0, value=100.0, step=10.0)
C_uF = st.sidebar.number_input("Capacitância C (µF)", min_value=0.0, value=100.0, step=10.0)

# --- CÁLCULOS ELÉTRICOS ---
omega = 2 * np.pi * freq
L = L_mH / 1000  # Converte mH para H
C = C_uF / 1000000  # Converte µF para F

# Reatâncias
X_L = omega * L
X_C = 1 / (omega * C) if C > 0 else 1e9

# Impedâncias complexas
Z_R = R + 0j
Z_L = 0 + X_L * 1j
Z_C = 0 - X_C * 1j

if tipo_circuito == "Série":
    Z_tot = Z_R + Z_L + Z_C
    I_tot = V_rms / Z_tot
    
    # Quedas de tensão (Série)
    V_R = I_tot * Z_R
    V_L = I_tot * Z_L
    V_C = I_tot * Z_C
    
    correntes = {"Total": I_tot, "R": I_tot, "L": I_tot, "C": I_tot}
    tensoes = {"Total": V_rms + 0j, "R": V_R, "L": V_L, "C": V_C}

else: # Paralelo
    # Admitâncias
    Y_R = 1 / Z_R if R > 0 else 0
    Y_L = 1 / Z_L if X_L > 0 else 0
    Y_C = 1 / Z_C
    
    Y_tot = Y_R + Y_L + Y_C
    Z_tot = 1 / Y_tot if Y_tot != 0 else 0 + 0j
    I_tot = V_rms / Z_tot
    
    # Correntes nos ramos (Paralelo)
    I_R = V_rms / Z_R if R > 0 else 0j
    I_L = V_rms / Z_L if X_L > 0 else 0j
    I_C = V_rms / Z_C
    
    correntes = {"Total": I_tot, "R": I_R, "L": I_L, "C": I_C}
    tensoes = {"Total": V_rms + 0j, "R": V_rms + 0j, "L": V_rms + 0j, "C": V_rms + 0j}

# --- INTERFACE DE RESULTADOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Memorial Descritivo")
    st.markdown(f"**Impedância Total:** {abs(Z_tot):.2f} Ω (Ângulo: {np.degrees(np.angle(Z_tot)):.1f}°)")
    st.markdown(f"**Corrente Total:** {abs(I_tot):.2f} A")
    
    st.write("### Detalhamento por Componente:")
    dados_tabela = [
        ["Componente", "Impedância/Reatância (Ω)", "Corrente (A)", "Queda de Tensão (V)", "Fase (°)"],
        ["Resistor (R)", f"{R:.2f}", f"{abs(correntes['R']):.2f}", f"{abs(tensoes['R']):.2f}", f"{np.degrees(np.angle(tensoes['R'])):.1f}"],
        ["Indutor (L)", f"{X_L:.2f}", f"{abs(correntes['L']):.2f}", f"{abs(tensoes['L']):.2f}", f"{np.degrees(np.angle(tensoes['L'])):.1f}"],
        ["Capacitor (C)", f"{X_C:.2f}", f"{abs(correntes['C']):.2f}", f"{abs(tensoes['C']):.2f}", f"{np.degrees(np.angle(tensoes['C'])):.1f}"]
    ]
    st.table(dados_tabela)

# --- GERAR DIAGRAMA FASORIAL ---
fig, ax = plt.subplots(figsize=(5, 5))
ax.axhline(0, color='gray', lw=0.5, ls='--')
ax.axvline(0, color='gray', lw=0.5, ls='--')

# Plotando os fasores de Tensão
ax.quiver(0, 0, tensoes['R'].real, tensoes['R'].imag, angles='xy', scale_units='xy', scale=1, color='r', label='V_R')
ax.quiver(0, 0, tensoes['L'].real, tensoes['L'].imag, angles='xy', scale_units='xy', scale=1, color='g', label='V_L')
ax.quiver(0, 0, tensoes['C'].real, tensoes['C'].imag, angles='xy', scale_units='xy', scale=1, color='b', label='V_C')

# Ajuste de limites do gráfico dinâmico
max_v = max(abs(tensoes['R']), abs(tensoes['L']), abs(tensoes['C']), V_rms)
ax.set_xlim(-max_v*1.2, max_v*1.2)
ax.set_ylim(-max_v*1.2, max_v*1.2)
ax.set_aspect('equal')
ax.grid(True)
plt.legend()
plt.title("Diagrama Fasorial de Tensões (V)")

with col2:
    st.subheader("📈 Diagrama Fasorial")
    st.pyplot(fig)
    plt.savefig("fasor.png", bbox_inches='tight')

# --- GERADOR DE PDF ---
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatorio de Simulacao de Circuito Eletrico", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Configuracao: Circuito {tipo_circuito}", ln=True)
    pdf.cell(190, 10, f"Tensao da Fonte: {V_rms} V | Frequencia: {freq} Hz", ln=True)
    pdf.cell(190, 10, f"R: {R} Ohms | L: {L_mH} mH | C: {C_uF} uF", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Memorial Descritivo:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Impedancia Total: {abs(Z_tot):.2f} Ohms", ln=True)
    pdf.cell(190, 10, f"Corrente Total: {abs(I_tot):.2f} A", ln=True)
    pdf.ln(5)
    
    for item in dados_tabela[1:]:
        pdf.cell(190, 8, f"{item[0]} -> I: {item[2]}A | V: {item[3]}V | Fase: {item[4]}*", ln=True)
    
    if os.path.exists("fasor.png"):
        pdf.ln(10)
        pdf.image("fasor.png", x=10, w=100)
        
    return pdf.output(dest="S").encode("latin-1")

pdf_bytes = gerar_pdf()

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Baixar Relatório PDF",
    data=pdf_bytes,
    file_name="relatorio_circuito.pdf",
    mime="application/pdf"
)
