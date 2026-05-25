import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- ARQUITETURA DA INTERFACE PROFISSIONAL ---
st.set_page_config(
    page_title="Laboratório de Análise de Circuitos RLC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design de UI Industrial (Removendo traços comuns de templates de IA)
st.markdown("""
    <style>
    /* Estilização Global e Botões de Seleção Tipo "Cards" */
    .stRadio div[role="radiogroup"] { flex-direction: row; gap: 10px; }
    div[data-testid="stMarkdownContainer"] h1 { font-family: 'Courier New', Courier, monospace; color: #1E293B; }
    
    .panel-tecnico {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-family: monospace;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0F172A;
    }
    .metric-unit {
        font-size: 14px;
        color: #64748B;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ INSTRUMENTAÇÃO E SIMULAÇÃO DE MALHAS RLC")
st.caption("Ambiente de homologação e análise vetorial de circuitos passivos em regime permanente senoidal.")
st.write("---")

# --- CONSTRUÇÃO DA BANCADA DE TRABALHO (SIDEBAR) ---
st.sidebar.header("🕹️ PAINEL DE CONTROLE DE HARDWARE")

# Alterado para Botões de Seleção Avançados (Grid de Opções)
tipo_circuito = st.sidebar.radio(
    "TOPOLOGIA DA REDE:",
    ["Série", "Paralelo"],
    help="Define o arranjo de conexões dos nós da malha."
)

st.sidebar.write("---")
st.sidebar.subheader("🔌 FONTE DE ALIMENTAÇÃO CA")

# Botões de seleção rápida para Tensões Comerciais de mercado
v_comercial = st.sidebar.selectbox(
    "Selecione a Tensão (V_rms):",
    ["Personalizado", "12V (Sinal/Controle)", "127V (Residencial)", "220V (Bifásico)", "380V (Industrial)"]
)

if v_comercial == "Personalizado":
    V_rms = st.sidebar.slider("Ajuste Fino de Tensão (V)", min_value=1.0, max_value=440.0, value=127.0, step=1.0)
else:
    V_rms = float(v_comercial.split("V")[0])

# Botões de seleção para frequências padrões de rede e laboratório
f_comercial = st.sidebar.selectbox(
    "Frequência da Rede (Hz):",
    ["60 Hz (Padrão BR)", "50 Hz (Padrão Europeu)", "1000 Hz (Áudio/Laboratório)", "Personalizada"]
)

if f_comercial == "Personalizada":
    freq = st.sidebar.slider("Ajuste Fino de Frequência (Hz)", min_value=1.0, max_value=5000.0, value=60.0, step=10.0)
else:
    freq = float(f_comercial.split(" Hz")[0])

st.sidebar.write("---")
st.sidebar.subheader("🧰 COMPONENTES DA BANCADA")

# Modificado para caixas estruturadas com botões de incremento precisos
with st.sidebar.expander("Resistor (R)", expanded=True):
    com_R = st.checkbox("Acoplar Resistor à malha", value=True)
    R_val = st.number_input("Valor da Resistência (Ω)", min_value=0.1, max_value=10000.0, value=50.0, step=5.0) if com_R else 0.0

with st.sidebar.expander("Indutor (L)", expanded=True):
    com_L = st.checkbox("Acoplar Indutor à malha", value=True)
    L_val = st.number_input("Valor da Indutância (mH)", min_value=0.1, max_value=5000.0, value=300.0, step=10.0) if com_L else 0.0

with st.sidebar.expander("Capacitor (C)", expanded=True):
    com_C = st.checkbox("Acoplar Capacitor à malha", value=True)
    C_val = st.number_input("Valor da Capacitância (µF)", min_value=0.1, max_value=2000.0, value=47.0, step=1.0) if com_C else 0.0

if not com_R and not com_L and not com_C:
    st.error("❌ Erro de Hardware: Nenhum componente conectado. Acople pelo menos um elemento na sidebar.")
    st.stop()

# --- LÓGICA MATEMÁTICA DE ENGENHARIA ---
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

# --- DISPOSIÇÃO DO WORKSPACE ---
col_esquema, col_dados = st.columns([1, 2])

with col_esquema:
    st.write("### 📐 Esquema de Ligação")
    
    # Gerador de Diagrama de Blocos Esquemático Dinâmico (Muda baseado na seleção do usuário)
    fig_esq, ax_esq = plt.subplots(figsize=(4, 3))
    ax_esq.set_xlim(-1, 5)
    ax_esq.set_ylim(-2, 2)
    ax_esq.axis('off')
    
    # Desenho básico da fonte
    ax_esq.plot([0, 0], [-1, 1], color='#0F172A', lw=2)
    ax_esq.text(-0.5, 0, f" Fonte CA\n {V_rms}V", fontsize=9, fontweight='bold')
    
    if tipo_circuito == "Série":
        # Linhas de conexão série
        ax_esq.plot([0, 4, 4, 0, 0], [1, 1, -1, -1, -1], color='#64748B', lw=1.5, ls='--')
        pos_x = 1.0
        if com_R:
            ax_esq.凜ectangle = plt.Rectangle((pos_x, 0.7), 0.6, 0.6, facecolor='#EF4444', edgecolor='black')
            ax_esq.add_patch(ax_esq.凜ectangle); ax_esq.text(pos_x, 1.4, f"R\n{R_val}Ω", fontsize=8); pos_x += 1.0
        if com_L:
            ax_esq.凜ectangle = plt.Rectangle((pos_x, 0.7), 0.6, 0.6, facecolor='#10B981', edgecolor='black')
            ax_esq.add_patch(ax_esq.凜ectangle); ax_esq.text(pos_x, 1.4, f"L\n{L_val}mH", fontsize=8); pos_x += 1.0
        if com_C:
            ax_esq.凜ectangle = plt.Rectangle((pos_x, 0.7), 0.6, 0.6, facecolor='#3B82F6', edgecolor='black')
            ax_esq.add_patch(ax_esq.凜ectangle); ax_esq.text(pos_x, 1.4, f"C\n{C_val}µF", fontsize=8)
    else:
        # Linhas de conexão paralelo
        ax_esq.plot([0, 3.5], [1, 1], color='#64748B', lw=1.5)
        ax_esq.plot([0, 3.5], [-1, -1], color='#64748B', lw=1.5)
        pos_x = 1.2
        if com_R:
            ax_esq.plot([pos_x, pos_x], [1, -1], color='#EF4444', lw=3); ax_esq.text(pos_x+0.1, 0, f"R ({R_val}Ω)", fontsize=8); pos_x += 1.0
        if com_L:
            ax_esq.plot([pos_x, pos_x], [1, -1], color='#10B981', lw=3); ax_esq.text(pos_x+0.1, 0, f"L ({L_val}H)", fontsize=8); pos_x += 1.0
        if com_C:
            ax_esq.plot([pos_x, pos_x], [1, -1], color='#3B82F6', lw=3); ax_esq.text(pos_x+0.1, 0, f"C ({C_val}F)", fontsize=8)

    st.pyplot(fig_esq)
    plt.close(fig_esq)

with col_dados:
    st.write("### 📋 Leituras do Barramento Principal")
    
    # Telemetria Avançada Estilo Painel de Controle de Laboratório (Clean UI)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="panel-tecnico">IMPEDÂNCIA DO SISTEMA<br><span class="metric-value">{abs(Z_tot):.2f}</span> <span class="metric-unit">Ω</span><br><small>Fase: {np.degrees(np.angle(Z_tot)):.1f}°</small></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="panel-tecnico">CORRENTE EFICAZ (RMS)<br><span class="metric-value">{abs(I_tot):.3f}</span> <span class="metric-unit">A</span><br><small>Fase: {np.degrees(np.angle(I_tot)):.1f}°</small></div>', unsafe_allow_html=True)
    with m3:
        fp = np.cos(np.angle(Z_tot))
        caracter = "INDUTIVO" if np.angle(Z_tot) > 0.01 else "CAPACITIVO" if np.angle(Z_tot) < -0.01 else "RESISTIVO"
        st.markdown(f'<div class="panel-tecnico">FATOR DE POTÊNCIA<br><span class="metric-value">{fp:.3f}</span><br><small>Caráter: {caracter}</small></div>', unsafe_allow_html=True)

# Tabela e Gráficos Vetoriais organizados abaixo do painel
st.write("---")
tab_tabela, tab_graficos = st.tabs(["📋 Planilha de Dados", "🧭 Diagramas Vetoriais Fasoriais"])

with tab_tabela:
    linhas_tabela = [["Componente de Ramo", "Impedância Linear (Ω)", "Corrente Eficaz (A)", "Queda de Tensão (V)", "Ângulo de Fase (°)"]]
    if com_R: linhas_tabela.append(["Resistor (R)", f"{R_val:.2f} Ω", f"{abs(correntes['R']):.3f} A", f"{abs(tensoes['R']):.2f} V", f"{np.degrees(np.angle(tensoes['R'])):.1f}°"])
    if com_L: linhas_tabela.append(["Indutor (L)", f"{X_L:.2f} Ω", f"{abs(correntes['L']):.3f} A", f"{abs(tensoes['L']):.2f} V", f"{np.degrees(np.angle(tensoes['L'])):.1f}°"])
    if com_C: linhas_tabela.append(["Capacitor (C)", f"{X_C:.2f} Ω", f"{abs(correntes['C']):.3f} A", f"{abs(tensoes['C']):.2f} V", f"{np.degrees(np.angle(tensoes['C'])):.1f}°"])
    st.table(linhas_tabela)

with tab_graficos:
    g1, g2 = st.columns(2)
    with g1:
        fig_v, ax_v = plt.subplots(figsize=(4, 4))
        ax_v.axhline(0, color='black', lw=0.5, ls=':'); ax_v.axvline(0, color='black', lw=0.5, ls=':')
        if com_R and abs(tensoes['R']) > 1e-2: ax_v.quiver(0, 0, tensoes['R'].real, tensoes['R'].imag, angles='xy', scale_units='xy', scale=1, color='#EF4444', label='V_R')
        if com_L and abs(tensoes['L']) > 1e-2: ax_v.quiver(0, 0, tensoes['L'].real, tensoes['L'].imag, angles='xy', scale_units='xy', scale=1, color='#10B981', label='V_L')
        if com_C and abs(tensoes['C']) > 1e-2: ax_v.quiver(0, 0, tensoes['C'].real, tensoes['C'].imag, angles='xy', scale_units='xy', scale=1, color='#3B82F6', label='V_C')
        ax_v.quiver(0, 0, tensoes['Total'].real, tensoes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='#0F172A', label='V_Total', width=0.007)
        lim_v = max(max(abs(tensoes['R']), abs(tensoes['L']), abs(tensoes['C']), V_rms), 1.0) * 1.2
        ax_v.set_xlim(-lim_v, lim_v); ax_v.set_ylim(-lim_v, lim_v); ax_v.set_aspect('equal'); ax_v.grid(True, alpha=0.2); ax_v.legend(); ax_v.set_title("Fasores de Tensão (V)")
        st.pyplot(fig_v)
        plt.savefig("fasor_v.png", bbox_inches='tight'); plt.close(fig_v)
        
    with g2:
        fig_i, ax_i = plt.subplots(figsize=(4, 4))
        ax_i.axhline(0, color='black', lw=0.5, ls=':'); ax_i.axvline(0, color='black', lw=0.5, ls=':')
        if com_R and abs(correntes['R']) > 1e-3: ax_i.quiver(0, 0, correntes['R'].real, correntes['R'].imag, angles='xy', scale_units='xy', scale=1, color='#EF4444', label='I_R')
        if com_L and abs(correntes['L']) > 1e-3: ax_i.quiver(0, 0, correntes['L'].real, correntes['L'].imag, angles='xy', scale_units='xy', scale=1, color='#10B981', label='I_L')
        if com_C and abs(correntes['C']) > 1e-3: ax_i.quiver(0, 0, correntes['C'].real, correntes['C'].imag, angles='xy', scale_units='xy', scale=1, color='#3B82F6', label='I_C')
        if abs(I_tot) > 1e-3: ax_i.quiver(0, 0, correntes['Total'].real, correntes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='#0F172A', label='I_Total', width=0.007)
        lim_i = max(max(abs(correntes['R']), abs(correntes['L']), abs(correntes['C']), abs(I_tot)), 0.1) * 1.2
        ax_i.set_xlim(-lim_i, lim_i); ax_i.set_ylim(-lim_i, lim_i); ax_i.set_aspect('equal'); ax_i.grid(True, alpha=0.2); ax_i.legend(); ax_i.set_title("Fasores de Corrente (A)")
        st.pyplot(fig_i)
        plt.savefig("fasor_i.png", bbox_inches='tight'); plt.close(fig_i)

# --- ENGINE EXPORTAÇÃO PDF PARALELA ---
def construir_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(245, 247, 250)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 12, "MEMORIAL DE CONFIGURACAO E CALCULO ELETRICO", ln=True, align="C", fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "1. Especificacoes Gerais de Hardware:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f"  Topologia de Malha: Circuito {tipo_circuito}", ln=True)
    pdf.cell(190, 6, f"  Tensao Nominal de Entrada: {V_rms:.1f} V_rms | Frequencia: {freq:.1f} Hz", ln=True)
    pdf.cell(190, 6, f"  Valores Fixados: R={R_val} Ohm | L={L_val} mH | C={C_val} uF", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 8, "2. Resultados Globais:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 6, f"  Impedancia Equivalente complexa: {abs(Z_tot):.2f} Ohm (Fase: {np.degrees(np.angle(Z_tot)):.1f}*)", ln=True)
    pdf.cell(190, 6, f"  Corrente Total Circulante: {abs(I_tot):.3f} A", ln=True)
    pdf.cell(190, 6, f"  Fator de Potencia: {fp:.3f} ({caracter})", ln=True)
    
    if os.path.exists("fasor_v.png") and os.path.exists("fasor_i.png"):
        pdf.ln(5)
        pdf.image("fasor_v.png", x=12, w=85)
        pdf.image("fasor_i.png", x=105, y=pdf.get_y()-85, w=85)
    return pdf.output(dest="S").encode("latin-1", errors="ignore")

pdf_data = construir_pdf()
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Exportar Relatório Técnico (.PDF)",
    data=pdf_data,
    file_name="relatorio_bancada_rlc.pdf",
    mime="application/pdf"
)
