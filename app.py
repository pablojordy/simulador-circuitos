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

st.markdown('<div class="main-title">⚡ Laboratório Virtual de Circuitos RLC Pro</div>', unsafe_style_html=True)
st.markdown('<div class="subtitle">Projete, analise fasores e exporte relatórios técnicos de malhas em CA.</div>', unsafe_style_html=True)

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

# Checkboxes criativos para simular a inserção/remoção de componentes na bancada
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
Z_L = complex(0, X_L) if com_L else (1e-9 if tipo_circuito == "Série" else 1e9)
Z_C = complex(0, -X_C) if com_C else (1e-9 if tipo_circuito == "Série" else 1e9)

# Tratamento para circuito vazio
if not com_R and not com_L and not com_C:
    st.warning("⚠️ Insira pelo menos um componente na bancada lateral para iniciar a simulação.")
    st.stop()

# Resolução da malha equivalente
if tipo_circuito == "Série":
    Z_tot = (Z_R if com_R else 0) + (Z_L if com_L else 0) + (Z_C if com_C else 0)
    I_tot = V_rms / Z_tot
    
    V_R = I_tot * Z_R if com_R else 0j
    V_L = I_tot * Z_L if com_L else 0j
    V_C = I_tot * Z_C if com_C else 0j
    
    correntes = {"Total": I_tot, "R": I_tot, "L": I_tot, "C": I_tot}
    tensoes = {"Total": complex(V_rms, 0), "R": V_R, "L": V_L, "C": V_C}
else:
    Y_R = 1 / Z_R if com_R else 0
    Y_L = 1 / Z_L if com_L else 0
    Y_C = 1 / Z_C if com_C else 0
    
    Y_tot = Y_R + Y_L + Y_C
    Z_tot = 1 / Y_tot if Y_tot != 0 else complex(1e9, 0)
    I_tot = V_rms / Z_tot
    
    I_R = V_rms / Z_R if com_R else 0j
    I_L = V_rms / Z_L if com_L else 0j
    I_C = V_rms / Z_C if com_C else 0j
    
    correntes = {"Total": I_tot, "R": I_R, "L": I_L, "C": I_C}
    tensoes = {"Total": complex(V_rms, 0), "R": complex(V_rms, 0), "L": complex(V_rms, 0), "C": complex(V_rms, 0)}

# --- INTERFACE VISUAL PRINCIPAL (ORGANIZADA EM ABAS) ---
tab_dashboard, tab_fasores = st.tabs(["📊 Dashboard de Medições", "📈 Domínio da Frequência (Fasores)"])

with tab_dashboard:
    st.write("### 📌 Estado Atual do Sistema")
    
    # Cards de Destaque Rápido
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><b>Impedância Equivalente</b><br><span style="font-size:20px; color:#FF4B4B;">{abs(Z_tot):.2f} Ω</span><br><small>Ângulo: {np.degrees(np.angle(Z_tot)):.1f}°</small></div>', unsafe_style_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><b>Corrente da Fonte</b><br><span style="font-size:20px; color:#FF4B4B;">{abs(I_tot):.3f} A</span><br><small>Fase: {np.degrees(np.angle(I_tot)):.1f}°</small></div>', unsafe_style_html=True)
    with c3:
        fp = np.cos(np.angle(Z_tot))
        tipo_fp = "Indutivo" if np.angle(Z_tot) > 0 else "Capacitivo" if np.angle(Z_tot) < 0 else "Resistivo"
        st.markdown(f'<div class="metric-card"><b>Fator de Potência</b><br><span style="font-size:20px; color:#FF4B4B;">{fp:.3f}</span><br><small>Caráter: {tipo_fp}</small></div>', unsafe_style_html=True)
    with c4:
        P_ativa = V_rms * abs(I_tot) * fp
        st.markdown(f'<div class="metric-card"><b>Potência Ativa</b><br><span style="font-size:20px; color:#FF4B4B;">{P_ativa:.1f} W</span><br><small>Consumo Real</small></div>', unsafe_style_html=True)

    st.write("---")
    st.write("### 📝 Memorial Descritivo Completo")
    
    # Estrutura de Tabela Dinâmica baseada nos itens ativos
    linhas_tabela = [["Parâmetro / Componente", "Impedância de Ramo", "Corrente Eficaz (A)", "Queda de Tensão (V)", "Defasagem (°)"]]
    if com_R:
        linhas_tabela.append(["Resistor (R)", f"{R_val:.1f} Ω", f"{abs(correntes['R']):.3f} A", f"{abs(tensoes['R']):.2f} V", f"{np.degrees(np.angle(tensoes['R'])):.1f}°"])
    if com_L:
        linhas_tabela.append(["Indutor (L)", f"{X_L:.1f} Ω", f"{abs(correntes['L']):.3f} A", f"{abs(tensoes['L']):.2f} V", f"{np.degrees(np.angle(tensoes['L'])):.1f}°"])
    if com_C:
        linhas_tabela.append(["Capacitor (C)", f"{X_C:.1f} Ω", f"{abs(correntes['C']):.3f} A", f"{abs(tensoes['C']):.2f} V", f"{np.degrees(np.angle(tensoes['C'])):.1f}°"])
        
    st.table(linhas_tabela)

with tab_fasores:
    st.write("### 🧭 Análise Vetorial Complexa")
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        # Gráfico Fasores de Tensão
        fig_v, ax_v = plt.subplots(figsize=(5, 5))
        ax_v.axhline(0, color='gray', lw=0.7, ls='--')
        ax_v.axvline(0, color='gray', lw=0.7, ls='--')
        if com_R: ax_v.quiver(0, 0, tensoes['R'].real, tensoes['R'].imag, angles='xy', scale_units='xy', scale=1, color='red', label='V_R', width=0.015)
        if com_L: ax_v.quiver(0, 0, tensoes['L'].real, tensoes['L'].imag, angles='xy', scale_units='xy', scale=1, color='green', label='V_L', width=0.015)
        if com_C: ax_v.quiver(0, 0, tensoes['C'].real, tensoes['C'].imag, angles='xy', scale_units='xy', scale=1, color='blue', label='V_C', width=0.015)
        ax_v.quiver(0, 0, tensoes['Total'].real, tensoes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='black', label='V_Total', width=0.008, headwidth=4)
        
        lim_v = max(max(abs(tensoes['R']), abs(tensoes['L']), abs(tensoes['C']), V_rms), 1.0) * 1.3
        ax_v.set_xlim(-lim_v, lim_v)
        ax_v.set_ylim(-lim_v, lim_v)
        ax_v.set_aspect('equal')
        ax_v.grid(True, alpha=0.3)
        ax_v.legend(loc="upper right")
        ax_v.set_title("Fasores de Tensão (V)")
        st.pyplot(fig_v)
        plt.savefig("fasor_v.png", bbox_inches='tight')

    with col_f2:
        # Gráfico Fasores de Corrente
        fig_i, ax_i = plt.subplots(figsize=(5, 5))
        ax_i.axhline(0, color='gray', lw=0.7, ls='--')
        ax_i.axvline(0, color='gray', lw=0.7, ls='--')
        if com_R: ax_i.quiver(0, 0, correntes['R'].real, correntes['R'].imag, angles='xy', scale_units='xy', scale=1, color='red', label='I_R', width=0.015)
        if com_L: ax_i.quiver(0, 0, correntes['L'].real, correntes['L'].imag, angles='xy', scale_units='xy', scale=1, color='green', label='I_L', width=0.015)
        if com_C: ax_i.quiver(0, 0, correntes['C'].real, correntes['C'].imag, angles='xy', scale_units='xy', scale=1, color='blue', label='I_C', width=0.015)
        ax_i.quiver(0, 0, correntes['Total'].real, correntes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='black', label='I_Total', width=0.008, headwidth=4)
        
        lim_i = max(max(abs(correntes['R']), abs(correntes['L']), abs(correntes['C']), abs(I_tot)), 0.1) * 1.3
        ax_i.set_xlim(-lim_i, lim_i)
        ax_i.set_ylim(-lim_i, lim_i)
        ax_i.set_aspect('equal')
        ax_i.grid(True, alpha=0.3)
        ax_i.legend(loc="upper right")
        ax_i.set_title("Fasores de Corrente (A)")
        st.pyplot(fig_i)
        plt.savefig("fasor_i.png", bbox_inches='tight')

# --- ENGINE EXPORTAÇÃO PDF PARALELA ---
def construir_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Técnico
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 12, "RELATORIO TECNICO DE ANALISE ELETRICA", ln=True, align="C", fill=True)
    pdf.ln(5)
    
    # Parâmetros de Entrada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "1. Parametros de Entrada da Rede:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 6, f"  Configuracao Analisada: Circuito {tipo_circuito}", ln=True)
    pdf.cell(190, 6, f"  Fonte de Alimentacao: {V_rms:.1f} V_rms | Frequencia: {freq:.1f} Hz", ln=True)
    pdf.cell(190, 6, f"  Componentes em Malha: R={R_val} Ohm | L={L_val} mH | C={C_val} uF", ln=True)
    pdf.ln(5)
    
    # Resumo Executivo
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "2. Resultados Globais Equivalentes:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 6, f"  Impedancia Total Equivalente: {abs(Z_tot):.2f} Ohm com angulo de {np.degrees(np.angle(Z_tot)):.1f}* ", ln=True)
    pdf.cell(190, 6, f"  Corrente Total Demandada: {abs(I_tot):.3f} A", ln=True)
    pdf.cell(190, 6, f"  Fator de Potencia Resultante: {fp:.3f} ({tipo_fp})", ln=True)
    pdf.ln(5)
    
    # Tabela de Dados do Memorial
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 8, "3. Desmembramento por Elemento passivo:", ln=True)
    pdf.set_font("Arial", "", 10)
    for linha in linhas_tabela[1:]:
        pdf.cell(190, 7, f"  * {linha[0]} -> Impedancia: {linha[1]} | Corr.: {linha[2]} | Queda Tensao: {linha[3]} | Fase: {linha[4]}", ln=True)
    
    # Anexar Imagens no PDF
    if os.path.exists("fasor_v.png") and os.path.exists("fasor_i.png"):
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, "4. Mapeamento Fasorial Anexo:", ln=True)
        pdf.image("fasor_v.png", x=12, w=85)
        pdf.image("fasor_i.png", x=105, y=pdf.get_y()-85, w=85)
        
    return pdf.output(dest="S").encode("latin-1", errors="ignore")

# Download Button posicionado estrategicamente na sidebar
pdf_data = construir_pdf()
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Exportar Memorial Técnico (.PDF)",
    data=pdf_data,
    file_name="memorial_tecnico_circuito.pdf",
    mime="application/pdf"
)
