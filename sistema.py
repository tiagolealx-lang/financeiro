import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuração da página para o modo amplo (wide) igual à planilha
st.set_page_config(page_title="Meu Controle Financeiro", layout="wide")

ARQUIVO_DADOS = "dados_financeiros.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        # Converte para datetime e depois extrai apenas a data pura para evitar erros
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=180)

st.markdown("<h1 style='text-align: center;'>💰 Meu Controle Financeiro</h1>", unsafe_allow_html=True)
st.write("---")

# --- FORMULÁRIO DE CAPTURA ---
st.subheader("➕ Novo Lançamento")
with st.form("formulario_lancamento", clear_on_submit=True):
    col_data, col_tipo = st.columns(2)
    with col_data:
        data = st.date_input("Data", datetime.today().date())
    with col_tipo:
        tipo = st.selectbox("Tipo", ["Despesa (Saída)", "Receita (Entrada)"])
        
    col_cat, col_val = st.columns(2)
    with col_cat:
        if tipo == "Despesa (Saída)":
            categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
        else:
            categoria = st.selectbox("Categoria", ["Salário", "Investimentos", "Freelance", "Outros"])
    with col_val:
        valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
        
    descricao = st.text_input("Descrição / Detalhes")
    botao_adicionar = st.form_submit_button("Salvar Lançamento")

if botao_adicionar:
    novo_item = pd.DataFrame([{
        "Data": data,
        "Tipo": tipo,
        "Categoria": categoria,
        "Descrição": descricao,
        "Valor": valor
    }])
    st.session_state.dados = pd.concat([st.session_state.dados, novo_item], ignore_index=True)
    salvar_dados(st.session_state.dados)
    st.success("Lançamento adicionado com sucesso!")
    st.rerun()

st.write("---")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .card-roxo {
        background-color: #6A1B9A;
        padding: 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.subheader("📊 Resumo Visual das Operações")
df_atual = st.session_state.dados

if not df_atual.empty:
    # Preparação da base temporal para os gráficos
    df_visual = df_atual.copy()
    df_visual["Data"] = pd.to_datetime(df_visual["Data"])
    df_visual["Mês_Num"] = df_visual["Data"].dt.month
    df_visual["Mês_Nome"] = df_visual["Data"].dt.strftime("%b")
    
    meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Cálculos financeiros base
    total_receitas = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]["Valor"].sum()
    total_despesas = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]["Valor"].sum()
    saldo_final = total_receitas - total_despesas
    
    # --- BLOCO CENTRAL: METRÍCALS EXCEL & GRÁFICO DE BARRAS ---
    col_card, col_barra = st.columns([1, 2])
    
    with col_card:
        st.markdown(f"""
            <div class="card-roxo">
                <p style="margin:0; font-size:16px; font-weight:bold; opacity:0.9;">Total das Operações (Saídas)</p>
                <h1 style="margin:0; font-size:38px; color:white; font-weight:bold;">R$ {total_despesas:,.2f}</h1>
                <p style="margin:0; font-size:14px; opacity:0.8; margin-top:15px;">
                    Saldo Atual em Caixa:<br><b>R$ {saldo_final:,.2f}</b>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_barra:
        # Agrupamento real por mês focado em despesas
        df_mensal = df_visual[df_visual["Tipo"] == "Despesa (Saída)"].groupby(["Mês_Nome"])["Valor"].sum().reset_index()
        
        # Garante a estrutura completa de 12 meses na tela
        df_meses_completos = pd.DataFrame({"Mês_Nome": meses_ordem})
        df_mensal = pd.merge(df_meses_completos, df_mensal, on="Mês_Nome", how="left").fillna(0)
        df_mensal['Mês_Nome'] = pd.Categorical(df_mensal['Mês_Nome'], categories=meses_ordem, ordered=True)
        df_mensal = df_mensal.sort_values('Mês_Nome')
        
        fig_barra = go.Figure(data=[go.Bar(
            x=df_mensal["Mês_Nome"], y=df_mensal["Valor"],
            text=[f"R$ {v:,.0f}" if v > 0 else "" for v in df_mensal["Valor"]],
            textposition='outside',
            marker_color='#F5B041'
        )])
        
        fig_barra.update_layout(
            height=220, 
            margin=dict(t=25, b=10, l=10, r=10),
            yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        st.plotly_chart(fig_barra, use_container_width=True)

    st.write("---")
    
    # --- LINHA INFERIOR: OS 3 GRÁFICOS DE ROSCA (DONUT) ---
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        st.markdown("<p style='text-align:center; font-weight:bold;'>Top Receitas do Plano %</p>", unsafe_allow_html=True)
        df_rec = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]
        if not df_rec.empty:
            g1_dados = df_rec.groupby("Categoria")["Valor"].sum().reset_index()
            fig1 = px.pie(g1_dados, values='Valor', names='Categoria', hole=0.5, 
                          color_discrete_sequence=['#2E7D32', '#9C27B0', '#F5B041'])
            fig1.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), 
                               paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.caption("<p style='text-align:center; color:gray;'>Nenhuma receita cadastrada</p>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("<p style='text-align:center; font-weight:bold;'>Top Despesas do Plano %</p>", unsafe_allow_html=True)
        df_desp = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]
        if not df_desp.empty:
            g2_dados = df_desp.groupby("Categoria")["Valor"].sum().reset_index()
            fig2 = px.pie(g2_dados, values='Valor', names='Categoria', hole=0.5, 
                          color_discrete_sequence=['#900C3F', '#C70039', '#FF5733', '#FFC300', '#DAF7A6'])
            fig2.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), 
                               paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("<p style='text-align:center; color:gray;'>Nenhuma despesa cadastrada</p>", unsafe_allow_html=True)

    with col_g3:
        st.markdown("<p style='text-align:center; font-weight:bold;'>Top Contas / Distribuição Geral</p>", unsafe_allow_html=True)
        g3_dados = df_atual.groupby("Categoria")["Valor"].sum().reset_index()
        fig3 = px.pie(g3_dados, values='Valor', names='Categoria', hole=0.5, 
                      color_discrete_sequence=['#F5B041', '#2E7D32', '#9C27B0'])
        fig3.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), 
                           paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig3, use_container_width=True)

    # --- TABELA DE HISTÓRICO ---
    st.write("---")
    st.subheader("📋 Histórico de Transações")
    df_exibicao = df_atual.sort_values(by="Data", ascending=False)
    st.dataframe(df_exibicao, use_container_width=True)
    
    if st.button("⚠️ Limpar Todos os Dados"):
        st.session_state.dados = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
        if os.path.exists(ARQUIVO_DADOS):
            os.remove(ARQUIVO_DADOS)
        st.success("Histórico apagado!")
        st.rerun()
else:
    st.info("Nenhum lançamento cadastrado ainda. Use o formulário acima para começar!")
