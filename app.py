import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- ARQUITETURA DE FRONTIER WEB (CSS + JS EMULADO) ---
st.set_page_config(
    page_title="RLC Core Engine Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de CSS de alta fidelidade para emular comportamento de uma SPA (Single Page Application)
st.markdown("""
    <style>
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
        font-size: 1.5rem;
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
st.markdown('<p style="font-size: 1.85rem; font-weight: 700; color: #09090B; margin-bottom: 2px;">Laboratório de Simulação e Análise RLC</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 0.95rem; color: #71717A; margin-bottom: 24px;">Ambiente de instrumentação analítica para malhas lineares em regime permanente senoidal.</p>', unsafe_allow_html=True)

# --- PAINEL DE HARDWARE LATERAL (SISTEMA DE ENTRADAS) ---
st.sidebar.markdown('<p style="font-size: 1.15rem; font-weight: 600; margin-bottom: 16px;">⚙️ Hardware Setup</p>', unsafe_allow_html=True)

tipo_circuito = st.sidebar.radio("SISTEMA DE CONEXÃO:", ["Série", "Paralelo"])

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #1E293B;"></div>', unsafe_allow_html=True)

st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: #94A3B8;">PARÂMETROS DA FONTE CA</p>', unsafe_allow_html=True)

# Seletores e Ajustes de Tensão da Fonte
v_comercial = st.sidebar.selectbox("Tensão Nominal (V_rms):", ["127V (Rede Residencial)", "220V (Rede Bifásica)", "380V (Rede Industrial)", "12V (Sinal de Controle)", "Personalizada"])
if v_comercial == "Personalizada":
    V_rms = st.sidebar.slider("Ajuste Fino de Tensão (V)", min_value=1.0, max_value=440.0, value=220.0, step=1.0)
else:
    V_rms = float(v_comercial.split("V")[0])

# Seletores e Ajustes de Frequência
f_comercial = st.sidebar.selectbox("Frequência do Sistema:", ["60 Hz (Padrão BR)", "50 Hz (Padrão EU)", "1000 Hz (Áudio/Testes)", "Personalizada"])
if f_comercial == "Personalizada":
    freq = st.sidebar.slider("Ajuste Fino de Frequência (Hz)", min_value=1.0, max_value=5000.0, value=60.0, step=5.0)
else:
    freq = float(f_comercial.split(" Hz")[0])

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #1E293B;"></div>', unsafe_allow_html=True)

st.sidebar.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: #94A3B8;">BANCADA DE COMPONENTES</p>', unsafe_allow_html=True)

# Entradas organizadas por colunas compactas para economia de espaço em tela
c_r1, c_r2 = st.sidebar.columns([1.2, 2])
with c_r1: com_R = st.checkbox("Resistor R", value=True)
with c_r2: R_val = st.number_input("Ω", min_value=0.1, max_value=10000.0, value=47.0, step=5.0, label_visibility="collapsed") if com_R else 0.0

c_l1, c_l2 = st.sidebar.columns([1.2, 2])
with c_l1: com_L = st.checkbox("Indutor L", value=True)
with c_l2: L_val = st.number_input("mH", min_value=0.1, max_value=5000.0, value=100.0, step=10.0, label_visibility="collapsed") if com_L else 0.0

c_c1, c_c2 = st.sidebar.columns([1.2, 2])
with c_c1: com_C = st.checkbox("Capacitor C", value=True)
with c_c2: C_val = st.number_input("µF", min_value=0.1, max_value=2000.0, value=33.0, step=5.0, label_visibility="collapsed") if com_C else 0.0

if not com_R and not com_L and not com_C:
    st.error("⚠️ Sistema Inoperante: Conecte ao menos uma carga à malha.")
    st.stop()

# --- NÚCLEO DE PROCESSAMENTO MATEMÁTICO ---
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

# Cálculo de Grandezas de Potência Elétrica
ang_rad = np.angle(Z_tot)
fp = np.cos(ang_rad)
caracter = "INDUTIVO (ATRASADO)" if ang_rad > 0.001 else "CAPACITIVO (AVANÇADO)" if ang_rad < -0.001 else "RESISTIVO"

S_aparente = V_rms * abs(I_tot)
P_ativa = S_aparente * fp
Q_reativa = S_aparente * np.sin(ang_rad)

# --- DISPOSIÇÃO DO WORKSPACE ---
col_esq, col_dir = st.columns([1, 2.2], gap="large")

with col_esq:
    st.markdown('<p style="font-size: 1rem; font-weight: 600; color: #09090B; margin-bottom: 12px;">📐 Topologia Esquemática</p>', unsafe_allow_html=True)
    
    fig_esq, ax_esq = plt.subplots(figsize=(4.5, 3.5))
    ax_esq.set_xlim(-0.8, 4.8)
    ax_esq.set_ylim(-1.8, 1.8)
    ax_esq.axis('off')
    fig_esq.patch.set_facecolor('#FAFAFA')
    ax_esq.set_facecolor('#FAFAFA')
    
    # Desenho da Fonte CA Vetorizada
    circle = plt.Circle((0, 0), 0.35, fill=False, color='#09090B', lw=2)
    ax_esq.add_patch(circle)
    sx = np.linspace(-0.15, 0.15, 30)
    sy = 0.15 * np.sin(2 * np.pi * sx / 0.3)
    ax_esq.plot(sx, sy, color='#09090B', lw=1.5)
    ax_esq.text(-0.4, -0.7, f" Fonte CA\n {V_rms:.0f} V", fontsize=8, fontweight='semibold')
    
    if tipo_circuito == "Série":
        ax_esq.plot([0, 0, 4, 4, 0], [0.35, 1.2, 1.2, -1.2, -1.2], color='#71717A', lw=1.5)
        ax_esq.plot([0, 0], [-0.35, -1.2], color='#71717A', lw=1.5)
        
        pos_x = 0.8
        if com_R:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#EF4444', lw=2))
            ax_esq.text(pos_x+0.2, 1.1, "R", color='#EF4444', fontsize=9, fontweight='bold')
            pos_x += 1.1
        if com_L:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#10B981', lw=2))
            ax_esq.text(pos_x+0.2, 1.1, "L", color='#10B981', fontsize=9, fontweight='bold')
            pos_x += 1.1
        if com_C:
            ax_esq.add_patch(plt.Rectangle((pos_x, 0.95), 0.7, 0.5, facecolor='#FFFFFF', edgecolor='#3B82F6', lw=2))
            ax_esq.text(pos_x+0.2, 1.1, "C", color='#3B82F6', fontsize=9, fontweight='bold')
    else:
        ax_esq.plot([0, 0, 3.8, 3.8], [0.35, 1.2, 1.2, -1.2], color='#71717A', lw=1.5)
        ax_esq.plot([0, 0, 3.8, 3.8], [-0.35, -1.2, -1.2, 1.2], color='#71717A', lw=1.5)
        
        pos_x = 1.2
        if com_R:
            ax_esq.plot([pos_x, pos_x], [1.2, -1.2], color='#EF4444', lw=3.5)
            ax_esq.text(pos_x+0.15, 0, "R", color='#EF4444', fontsize=9, fontweight='bold')
            pos_x += 1.1
        if com_L:
            ax_esq.plot([pos_x, pos_x], [1.2, -1.2], color='#10B981', lw=3.5)
            ax_esq.text(pos_x+0.15, 0, "L", color='#10B981', fontsize=9, fontweight='bold')
            pos_x += 1.1
        if com_C:
            ax_esq.plot([pos_x, pos_x], [1.2, -1.2], color='#3B82F6', lw=3.5)
            ax_esq.text(pos_x+0.15, 0, "C", color='#3B82F6', fontsize=9, fontweight='bold')

    st.pyplot(fig_esq)
    plt.close(fig_esq)

with col_dir:
    st.markdown('<p style="font-size: 1rem; font-weight: 600; color: #09090B; margin-bottom: 12px;">⚡ Fluxo de Potência e Corrente Total</p>', unsafe_allow_html=True)
    
    # Telemetria Superior (Grandezas Globais pedidas)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Corrente Total (I_rms)</div><div class="card-value">{abs(I_tot):.3f} <span style="font-size:1rem;color:#71717A">A</span></div><div class="card-sub">Fase: {-np.degrees(ang_rad):.1f}°</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Potência Ativa (P)</div><div class="card-value">{P_ativa:.1f} <span style="font-size:1rem;color:#71717A">W</span></div><div class="card-sub">Trabalho Real</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Potência Aparente (S)</div><div class="card-value">{S_aparente:.1f} <span style="font-size:1rem;color:#71717A">VA</span></div><div class="card-sub">Q = {Q_reativa:.1f} VAr</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    m4, m5, m6 = st.columns(3)
    with m4:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Impedância Equivalente</div><div class="card-value">{abs(Z_tot):.2f} <span style="font-size:1rem;color:#71717A">Ω</span></div><div class="card-sub">Z = {Z_tot.real:.1f} + j({Z_tot.imag:.1f})</div></div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Fator de Potência</div><div class="card-value">{fp:.3f}</div><div class="card-sub">{caracter}</div></div>', unsafe_allow_html=True)
    with m6:
        st.markdown(f'<div class="dashboard-card"><div class="card-label">Frequência Angular</div><div class="card-value">{omega:.1f} <span style="font-size:1rem;color:#71717A">rad/s</span></div><div class="card-sub">Ciclos: {freq:.0f} Hz</div></div>', unsafe_allow_html=True)

# Abas Inferiores de detalhamento de Dados e Vetores
st.write("##")
tab_dados, tab_vetores = st.tabs(["📋 Planilha de Quedas de Tensão e Correntes", "🧭 Diagramas Vetoriais Fasoriais"])

with tab_dados:
    # Tabela HTML estruturada contendo ângulos e quedas exigidas
    html_table = """<table class="styled-table">
    <thead><tr><th>Componente Eleito</th><th>Impedância Associada</th><th>Corrente de Ramo (A)</th><th>Ângulo Corrente</th><th>Queda de Tensão (V)</th><th>Ângulo Tensão</th></tr></thead>
    <tbody>"""
    if com_R: html_table += f"<tr><td><b>Resistor (R)</b></td><td>{R_val:.2f} Ω</td><td>{abs(correntes['R']):.3f} A</td><td>{np.degrees(np.angle(correntes['R'])):.1f}°</td><td>{abs(tensoes['R']):.2f} V</td><td>{np.degrees(np.angle(tensoes['R'])):.1f}°</td></tr>"
    if com_L: html_table += f"<tr><td><b>Indutor (L)</b></td><td>{X_L:.2f} Ω (X_l)</td><td>{abs(correntes['L']):.3f} A</td><td>{np.degrees(np.angle(correntes['L'])):.1f}°</td><td>{abs(tensoes['L']):.2f} V</td><td>{np.degrees(np.angle(tensoes['L'])):.1f}°</td></tr>"
    if com_C: html_table += f"<tr><td><b>Capacitor (C)</b></td><td>{X_C:.2f} Ω (X_c)</td><td>{abs(correntes['C']):.3f} A</td><td>{np.degrees(np.angle(correntes['C'])):.1f}°</td><td>{abs(tensoes['C']):.2f} V</td><td>{np.degrees(np.angle(tensoes['C'])):.1f}°</td></tr>"
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

with tab_vetores:
    gv1, gv2 = st.columns(2)
    
    with gv1:
        # Diagrama de Tensões Dimensionado Dinamicamente
        fig_v, ax_v = plt.subplots(figsize=(4, 4))
        fig_v.patch.set_facecolor('#FAFAFA'); ax_v.set_facecolor('#FAFAFA')
        ax_v.axhline(0, color='#CBD5E1', lw=1); ax_v.axvline(0, color='#CBD5E1', lw=1)
        
        if com_R and abs(tensoes['R']) > 1e-2: ax_v.quiver(0, 0, tensoes['R'].real, tensoes['R'].imag, angles='xy', scale_units='xy', scale=1, color='#EF4444', label='V_R', width=0.012)
        if com_L and abs(tensoes['L']) > 1e-2: ax_v.quiver(0, 0, tensoes['L'].real, tensoes['L'].imag, angles='xy', scale_units='xy', scale=1, color='#10B981', label='V_L', width=0.012)
        if com_C and abs(tensoes['C']) > 1e-2: ax_v.quiver(0, 0, tensoes['C'].real, tensoes['C'].imag, angles='xy', scale_units='xy', scale=1, color='#3B82F6', label='V_C', width=0.012)
        ax_v.quiver(0, 0, tensoes['Total'].real, tensoes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='#09090B', label='V_Total', width=0.007)
        
        lim_v = max(max(abs(tensoes['R']), abs(tensoes['L']), abs(tensoes['C']), V_rms), 1.0) * 1.2
        ax_v.set_xlim(-lim_v, lim_v); ax_v.set_ylim(-lim_v, lim_v); ax_v.set_aspect('equal'); ax_v.grid(True, color='#E2E8F0', alpha=0.5); ax_v.legend(frameon=False); ax_v.set_title("Fasores de Tensão (V)", fontsize=10, color='#64748B', weight='bold')
        st.pyplot(fig_v)
        plt.savefig("fasor_v.png", bbox_inches='tight', facecolor=fig_v.get_facecolor()); plt.close(fig_v)

    with gv2:
        # Diagrama de Correntes Dimensionado Dinamicamente
        fig_i, ax_i = plt.subplots(figsize=(4, 4))
        fig_i.patch.set_facecolor('#FAFAFA'); ax_i.set_facecolor('#FAFAFA')
        ax_i.axhline(0, color='#CBD5E1', lw=1); ax_i.axvline(0, color='#CBD5E1', lw=1)
        
        if com_R and abs(correntes['R']) > 1e-3: ax_i.quiver(0, 0, correntes['R'].real, correntes['R'].imag, angles='xy', scale_units='xy', scale=1, color='#EF4444', label='I_R', width=0.012)
        if com_L and abs(correntes['L']) > 1e-3: ax_i.quiver(0, 0, correntes['L'].real, correntes['L'].imag, angles='xy', scale_units='xy', scale=1, color='#10B981', label='I_L', width=0.012)
        if com_C and abs(correntes['C']) > 1e-3: ax_i.quiver(0, 0, correntes['C'].real, correntes['C'].imag, angles='xy', scale_units='xy', scale=1, color='#3B82F6', label='I_C', width=0.012)
        if abs(I_tot) > 1e-3: ax_i.quiver(0, 0, correntes['Total'].real, correntes['Total'].imag, angles='xy', scale_units='xy', scale=1, color='#09090B', label='I_Total', width=0.007)
        
        lim_i = max(max(abs(correntes['R']), abs(correntes['L']), abs(correntes['C']), abs(I_tot)), 0.1) * 1.2
        ax_i.set_xlim(-lim_i, lim_i); ax_i.set_ylim(-lim_i, lim_i); ax_i.set_aspect('equal'); ax_i.grid(True, color='#E2E8F0', alpha=0.5); ax_i.legend(frameon=False); ax_i.set_title("Fasores de Corrente (A)", fontsize=10, color='#64748B', weight='bold')
        st.pyplot(fig_i)
        plt.savefig("fasor_i.png", bbox_inches='tight', facecolor=fig_i.get_facecolor()); plt.close(fig_i)

# --- CONSTRUTOR PROFISSIONAL DE MEMORIAL PDF ---
def construir_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 12, "MEMORIAL TECNICO DE CALCULO E RELATORIO DE MALHA", ln=True, align="C", fill=True)
    pdf.ln(6)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 7, "1. CONDICOES DE CONTORNO DO SISTEMA:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 5, f"  Arranjo Configurado: Circuito {tipo_circuito}", ln=True)
    pdf.cell(190, 5, f"  Excitation Input: {V_rms:.1f} V_rms | Frequencia: {freq:.1f} Hz", ln=True)
    pdf.cell(190, 5, f"  Elementos de Carga Ativos: R={R_val} Ohm | L={L_val} mH | C={C_val} uF", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 7, "2. GRANDEZAS ELETRICAS E MATRIZ DE POTENCIA:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 5, f"  Impedancia Total do Sistema: {abs(Z_tot):.2f} Ohm (Angulo de Fase: {np.degrees(ang_rad):.1f}*)", ln=True)
    pdf.cell(190, 5, f"  Corrente Total Circulante (I_rms): {abs(I_tot):.3f} A", ln=True)
    pdf.cell(190, 5, f"  Potencia Ativa (P): {P_ativa:.1f} W", ln=True)
    pdf.cell(190, 5, f"  Potencia Reativa (Q): {Q_reativa:.1f} VAr", ln=True)
    pdf.cell(190, 5, f"  Potencia Aparente (S): {S_aparente:.1f} VA", ln=True)
    pdf.cell(190, 5, f"  Fator de Potencia Absoluto: {fp:.3f} ({caracter})", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 7, "3. MAPEAMENTO COMPLETO POR ELEMENTO PASSIVO:", ln=True)
    pdf.set_font("Arial", "", 9)
    if com_R: pdf.cell(190, 5, f"  * Resistor (R)   -> V_rms: {abs(tensoes['R']):.2f} V | I_rms: {abs(correntes['R']):.3f} A | Angulo V: {np.degrees(np.angle(tensoes['R'])):.1f}*", ln=True)
    if com_L: pdf.cell(190, 5, f"  * Indutor (L)    -> V_rms: {abs(tensoes['L']):.2f} V | I_rms: {abs(correntes['L']):.3f} A | Angulo V: {np.degrees(np.angle(tensoes['L'])):.1f}*", ln=True)
    if com_C: pdf.cell(190, 5, f"  * Capacitor (C)  -> V_rms: {abs(tensoes['C']):.2f} V | I_rms: {abs(correntes['C']):.3f} A | Angulo V: {np.degrees(np.angle(tensoes['C'])):.1f}*", ln=True)
    
    if os.path.exists("fasor_v.png") and os.path.exists("fasor_i.png"):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, "4. ANEXOS GRÁFICOS (DIAGRAMAS VETORIAIS):", ln=True)
        pdf.image("fasor_v.png", x=12, w=85)
        pdf.image("fasor_i.png", x=105, y=pdf.get_y()-85, w=85)
    return pdf.output(dest="S").encode("latin-1", errors="ignore")

pdf_data = construir_pdf()
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.download_button(
    label="📥 IMPRIMIR RELATÓRIO TÉCNICO (.PDF)",
    data=pdf_data,
    file_name="memorial_de_calculo_rlc.pdf",
    mime="application/pdf"
)
