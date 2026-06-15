import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Meu Controle Financeiro", layout="centered")

ARQUIVO_DADOS = "dados_financeiros.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns()
    with col2:
        st.image("logo.png", width=180)

st.markdown("<h1 style='text-align: center;'>💰 Meu Controle Financeiro</h1>", unsafe_allow_html=True)
st.write("---")

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
st.subheader("📊 Resumo do Mês")

df_atual = st.session_state.dados

if not df_atual.empty:
    total_receitas = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]["Valor"].sum()
    total_despesas = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]["Valor"].sum()
    saldo_final = total_receitas - total_despesas
    
    card1, card2, card3 = st.columns(3)
    card1.metric("Total Entradas", f"R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    card2.metric("Total Saídas", f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    card3.metric("Saldo Atual", f"R$ {saldo_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=float(saldo_final))
    
    df_despesas = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]
    if not df_despesas.empty:
        st.write("---")
        st.write("### 🍕 Distribuição das Despesas")
        gastos_por_categoria = df_despesas.groupby("Categoria")["Valor"].sum()
        st.pie_chart(gastos_por_categoria)
        
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
