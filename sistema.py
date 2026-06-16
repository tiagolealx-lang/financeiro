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

# Título Principal estilizado centralizado
st.markdown("<h1 style='text-align: center; letter-spacing: 2px; font-family: serif;'>✨ JUNHO</h1>", unsafe_allow_html=True)
st.write("---")

# --- PROCESSAMENTO DOS VALORES PARA OS CARDS REAIS ---
df_atual = st.session_state.dados

if df_atual.empty:
    # Valores de Exemplo baseados no seu modelo caso esteja vazio
    v_gastos = 2483.64
    v_recebidos = 3500.00
    v_pago = 615.47
    v_falta = 1868.17
    v_saldo = 2884.53
else:
    # Cálculos Reais Dinâmicos
    v_recebidos = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]["Valor"].sum()
    v_gastos = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]["Valor"].sum()
    
    # Tratamento de status de pagamento se houver a coluna
    if "Status" in df_atual.columns:
        v_pago = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Status"] == "PAGO")]["Valor"].sum()
        v_falta = df_atual[(df_atual["Tipo"] == "Despesa (Saída)") & (df_atual["Status"] == "A PAGAR")]["Valor"].sum()
    else:
        v_pago = 0.0
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

# --- CRIAÇÃO DAS ABAS HORIZONTAIS (UMA DO LADO DA OUTRA) ---
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📥 NOVO LANÇAMENTO",
    "📌 GASTOS FIXOS", 
    "💳 PARCELAMENTOS", 
    "🗓️ GASTOS DO MÊS", 
    "💰 RECEBIMENTOS", 
    "📊 GASTOS POR CATEGORIA"
])

# --- ABA 1: FORMULÁRIO DE ENTRADA DE DADOS ---
with aba1:
    st.subheader("➕ Adicionar Nova Movimentação")
    with st.form("formulario_lancamento", clear_on_submit=True):
        col_data, col_tipo, col_grupo = st.columns(3)
        with col_data:
            data = st.date_input("Data de Vencimento", datetime.today().date(), min_value=date(2026, 1, 1), max_value=date(2050, 12, 31))
        with col_tipo:
            tipo = st.selectbox("Tipo", ["Despesa (Saída)", "Receita (Entrada)"])
        with col_grupo:
            grupo = st.selectbox("Classificação/Grupo", ["Gastos Fixos", "Parcelamentos", "Gastos do Mês", "Recebimentos"])
            
        col_cat, col_val, col_status = st.columns(3)
        with col_cat:
            if tipo == "Despesa (Saída)":
                categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Casa", "Dinheiro", "Outros"])
            else:
                categoria = st.selectbox("Categoria", ["Salário", "Investimentos", "Freelance", "Outros"])
        with col_val:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
        with col_status:
            status_pago = st.selectbox("Situação Inicial", ["A PAGAR", "PAGO"])
            
        descricao = st.text_input("Descrição / Detalhes (Ex: Empréstimo Nubank)")
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
    st.subheader("📌 Relatório de Gastos Fixos")
    df_fixos = df_atual[df_atual["Grupo"] == "Gastos Fixos"] if not df_atual.empty else pd.DataFrame()
    if not df_fixos.empty:
        st.dataframe(df_fixos[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info("Nenhum Gasto Fixo cadastrado.")

# --- ABA 3: PARCELAMENTOS ---
with aba3:
    st.subheader("💳 Relatório de Parcelamentos")
    df_parc = df_atual[df_atual["Grupo"] == "Parcelamentos"] if not df_atual.empty else pd.DataFrame()
    if not df_parc.empty:
        st.dataframe(df_parc[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info("Nenhum Parcelamento cadastrado.")

# --- ABA 4: GASTOS DO MÊS ---
with aba4:
    st.subheader("🗓️ Gastos Variáveis / Do Mês")
    df_mes = df_atual[df_atual["Grupo"] == "Gastos do Mês"] if not df_atual.empty else pd.DataFrame()
    if not df_mes.empty:
        st.dataframe(df_mes[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info("Nenhum Gasto do Mês cadastrado.")

# --- ABA 5: RECEBIMENTOS ---
with aba5:
    st.subheader("💰 Entradas e Recebimentos")
    df_rec_aba = df_atual[df_atual["Tipo"] == "Receita (Entrada)"] if not df_atual.empty else pd.DataFrame()
    if not df_rec_aba.empty:
        st.dataframe(df_rec_aba[["Data", "Categoria", "Descrição", "Valor", "Status"]], use_container_width=True)
    else:
        st.info("Nenhum Recebimento cadastrado.")

# --- ABA 6: GASTOS POR CATEGORIA (GRÁFICOS) ---
with aba6:
    st.subheader("📊 Análise Detalhada por Categoria")
    
    if df_atual.empty:
        st.info("💡 Dados demonstrativos ativados para fins de análise visual.")
        df_pizza = pd.DataFrame({"Categoria": ["Casa", "Dinheiro", "Alimentação", "Transporte"], "Valor": [996.00, 1100.00, 387.64, 0.0]})
        df_mensal_barra = pd.DataFrame({"Mês": ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], "Valor": [0,0,0,0,0,2483.64,0,0,0,0,0,0]})
    else:
        df_despesas_reais = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]
        if not df_despesas_reais.empty:
            df_pizza = df_despesas_reais.groupby("Categoria")["Valor"].sum().reset_index()
        else:
            df_pizza = pd.DataFrame()
            
        df_visual_barra = df_atual.copy()
        df_visual_barra["Data"] = pd.to_datetime(df_visual_barra["Data"])
        df_visual_barra["Mês"] = df_visual_barra["Data"].dt.strftime("%b")
        df_mensal_barra = df_visual_barra[df_visual_barra["Tipo"] == "Despesa (Saída)"].groupby(["Mês"])["Valor"].sum().reset_index()

    if plotly_disponivel and not df_pizza.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("**Distribuição Percentual de Gastos**")
            fig1 = px.pie(df_pizza, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=px.colors.Pastel)
            fig1.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_g2:
            st.markdown("**Histórico de Saídas Mensais**")
            fig2 = go.Figure(data=[go.Bar(x=df_mensal_barra["Mês"], y=df_mensal_barra["Valor"], marker_color='#F5B041')])
            fig2.update_layout(height=300, yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("Cadastre despesas para visualizar os gráficos.")
