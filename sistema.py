import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Importação segura dos gráficos do Plotly
try:
    import plotly.graph_objects as go
    import plotly.express as px
    plotly_disponivel = True
except ImportError:
    plotly_disponivel = False

# Configuração da página para o modo amplo (wide) igual ao modelo
st.set_page_config(page_title="Controle Financeiro Mensal", layout="wide")

ARQUIVO_DADOS = "dados_financeiros.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            df['Data'] = pd.to_datetime(df['Data']).dt.date
            return df
        except:
            pass
    return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor", "Grupo", "Status"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

# --- ESTILIZAÇÃO CUSTOMIZADA DOS CARDS SUPERIORES ---
st.markdown("""
    <style>
    .barra-metricas {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 25px;
    }
    .card-f {
        flex: 1;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    }
    .c-gastos { background-color: #D32F2F; }      /* Vermelho */
    .c-recebi { background-color: #0288D1; }      /* Azul */
    .c-pago { background-color: #2E7D32; }        /* Verde Escuro */
    .c-falta { background-color: #FBC02D; color: black; } /* Amarelo */
    .c-saldo { background-color: #4CAF50; }       /* Verde Claro */
    
    .v-num { font-size: 22px; font-weight: 800; margin-top: 5px; }
    .t-lbl { font-size: 13px; text-transform: uppercase; opacity: 0.9; }
    </style>
""", unsafe_allow_html=True)

# --- DICIONÁRIO DE TRADUÇÃO DE MESES ---
meses_pt = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO", 
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

# --- BARRA DE SELEÇÃO DO MÊS DE VISUALIZAÇÃO ---
st.markdown("<h2 style='text-align: center; font-family: serif; margin-bottom: 0;'>🔍 Filtrar Período de Visualização</h2>", unsafe_allow_html=True)
col_sel_mes, col_sel_ano = st.columns(2)

with col_sel_mes:
    mes_selecionado_nome = st.selectbox("Escolha o Mês para analisar:", list(meses_pt.values()), index=datetime.today().month - 1)
    mes_selecionado_num = [k for k, v in meses_pt.items() if v == mes_selecionado_nome][0]

with col_sel_ano:
    ano_selecionado = st.selectbox("Escolha o Ano para analisar:", [str(a) for a in range(2026, 2051)], index=0)

# Título Grande do Mês Dinâmico na Tela
st.markdown(f"<h1 style='text-align: center; letter-spacing: 2px; font-family: serif; color: #F5B041; margin-top: 15px;'>✨ {mes_selecionado_nome} / {ano_selecionado}</h1>", unsafe_allow_html=True)
st.write("---")

# --- FILTRAGEM REAL DO BANCO DE DADOS ---
df_original = st.session_state.dados

if not df_original.empty:
    df_original_copy = df_original.copy()
    df_original_copy["Data_Dt"] = pd.to_datetime(df_original_copy["Data"])
    df_original_copy["Mês_Num"] = df_original_copy["Data_Dt"].dt.month
    df_original_copy["Ano_Num"] = df_original_copy["Data_Dt"].dt.year
    
    df_atual = df_original_copy[
        (df_original_copy["Mês_Num"] == mes_selecionado_num) & 
        (df_original_copy["Ano_Num"] == int(ano_selecionado))
    ]
else:
    df_atual = pd.DataFrame()

# --- PROCESSAMENTO DOS VALORES PARA OS CARDS ---
if df_atual.empty:
    v_gastos = 0.00
    v_recebidos = 0.00
    v_pago = 0.00
    v_falta = 0.00
    v_saldo = 0.00
else:
    v_recebidos = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]["Valor"].sum()
    v_gastos = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Grupo"] != "Desafios")]["Valor"].sum()
    
    if "Status" in df_atual.columns:
        v_pago = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Status"] == "PAGO") & (df_atual["Grupo"] != "Desafios")]["Valor"].sum()
        v_falta = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Status"] == "A PAGAR") & (df_atual["Grupo"] != "Desafios")]["Valor"].sum()
    else:
        v_pago = 0.00
        v_falta = v_gastos
        
    v_saldo = v_recebidos - v_pago

# Renderização do Bloco de Métricas Coloridas Superior
st.markdown(f"""
    <div class="barra-metricas">
        <div class="card-f c-gastos"><div class="t-lbl">Total de Gastos</div><div class="v-num">R$ {v_gastos:,.2f}</div></div>
        <div class="card-f c-recebi"><div class="t-lbl">Recebimentos</div><div class="v-num">R$ {v_recebidos:,.2f}</div></div>
        <div class="card-f c-pago"><div class="t-lbl">Total Pago</div><div class="v-num">R$ {v_pago:,.2f}</div></div>
        <div class="card-f c-falta"><div class="t-lbl">Faltam a Pagar</div><div class="v-num">R$ {v_falta:,.2f}</div></div>
        <div class="card-f c-saldo"><div class="t-lbl">Saldo Disponível</div><div class="v-num">R$ {v_saldo:,.2f}</div></div>
    </div>
""", unsafe_allow_html=True)

# --- CRIAÇÃO DAS ABAS HORIZONTAIS ---
aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "📥 NOVO LANÇAMENTO",
    "📌 GASTOS FIXOS", 
    "💳 PARCELAMENTOS", 
    "🗓️ GASTOS DO MÊS", 
    "💰 RECEBIMENTOS", 
    "📊 GASTOS POR CATEGORIA",
    "🎯 DESAFIOS DE DEPÓSITOS"
])

# --- ABA 1: FORMULÁRIO DE ENTRADA DE DADOS ---
with aba1:
    st.subheader("➕ Adicionar Nova Movimentação")
    with st.form("formulario_lancamento", clear_on_submit=True):
        col_data, col_tipo, col_grupo = st.columns(3)
        with col_data:
            data_minima = date(2026, 1, 1)
            data_maxima = date(2050, 12, 31)
            data_padrao = datetime.today().date()
            if data_padrao < data_minima:
                data_padrao = data_minima
                
            data = st.date_input("Data de Vencimento / Depósito", value=data_padrao, min_value=data_minima, max_value=data_maxima)
        with col_tipo:
            tipo = st.selectbox("Tipo", ["Despesa (Saída)", "Receita (Entrada)"])
        with col_grupo:
            grupo = st.selectbox("Classificação/Grupo", ["Gastos Fixos", "Parcelamentos", "Gastos do Mês", "Recebimentos", "Salário", "Desafios"])
            
        col_cat, col_val, col_status = st.columns(3)
        with col_cat:
            if tipo == "Despesa (Saída)":
                categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Casa", "Dinheiro", "Poupança/Desafio", "Outros"])
            else:
                categoria = st.selectbox("Categoria", ["Salário", "Investimentos", "Freelance", "Outros"])
        with col_val:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
        with col_status:
            status_pago = st.selectbox("Situação Inicial", ["A PAGAR", "PAGO"])
            
        descricao = st.text_input("Descrição / Detalhes (Ex: Depósito Semana 1)")
        botao_adicionar = st.form_submit_button("Salvar Registro")

    if botao_adicionar:
        novo_item = pd.DataFrame([{
            "Data": data,
            "Tipo": tipo,
            "Categoria": categoria,
            "Descrição": descricao,
            "Valor": valor,
            "Grupo": grupo,
            "Status": status_pago
        }])
        st.session_state.dados = pd.concat([st.session_state.dados, novo_item], ignore_index=True)
        salvar_dados(st.session_state.dados)
        st.success("Lançamento adicionado com sucesso!")
        st.rerun()

# --- ABA 2: GASTOS FIXOS ---
with aba2:
    st.subheader(f"📌 Relatório de Gastos Fixos — {mes_selecionado_nome}")
    df_fixos = df_atual[df_atual["Grupo"] == "Gastos Fixos"] if not df_atual.empty else pd.DataFrame()
    if not df_fixos.empty:
        st.dataframe(df_fixos[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info(f"Nenhum Gasto Fixo cadastrado em {mes_selecionado_nome}/{ano_selecionado}.")

# --- ABA 3: PARCELAMENTOS ---
with aba3:
    st.subheader(f"💳 Relatório de Parcelamentos — {mes_selecionado_nome}")
    df_parc = df_atual[df_atual["Grupo"] == "Parcelamentos"] if not df_atual.empty else pd.DataFrame()
    if not df_parc.empty:
        st.dataframe(df_parc[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info(f"Nenhum Parcelamento cadastrado em {mes_selecionado_nome}/{ano_selecionado}.")

# --- ABA 4: GASTOS DO MÊS ---
with aba4:
    st.subheader(f"🗓️ Gastos Variáveis / Do Mês — {mes_selecionado_nome}")
    df_mes = df_atual[df_atual["Grupo"] == "Gastos do Mês"] if not df_atual.empty else pd.DataFrame()
    if not df_mes.empty:
        st.dataframe(df_mes[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info(f"Nenhum Gasto do Mês cadastrado em {mes_selecionado_nome}/{ano_selecionado}.")

# --- ABA 5: RECEBIMENTOS ---
with aba5:
    st.subheader(f"💰 Entradas e Recebimentos — {mes_selecionado_nome}")
    df_rec_aba = df_atual[(df_atual["Tipo"] == "Receita (Entrada)") | (df_atual["Grupo"] == "Salário")] if not df_atual.empty else pd.DataFrame()
    if not df_rec_aba.empty:
        st.dataframe(df_rec_aba[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info(f"Nenhum Recebimento cadastrado em {mes_selecionado_nome}/{ano_selecionado}.")

# --- ABA 6: GASTOS POR CATEGORIA (REFEITA SEM ERROS) ---
with aba6:
    st.subheader(f"📊 Análise de {mes_selecionado_nome} por Categoria")
    
    # Busca saídas válidas de forma direta
    df_gastos_grafico = pd.DataFrame()
    if not df_atual.empty:
        df_gastos_grafico = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Grupo"] != "Desafios")]
