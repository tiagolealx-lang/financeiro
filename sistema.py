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

# Configuração da página para o modo amplo (wide) igual à planilha do Excel
st.set_page_config(page_title="Meu Controle Financeiro", layout="wide")

ARQUIVO_DADOS = "dados_financeiros.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            df['Data'] = pd.to_datetime(df['Data']).dt.date
            return df
        except:
            pass
    return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image("logo.png", width=180)

st.markdown("<h1 style='text-align: center;'>💰 Meu Controle Financeiro</h1>", unsafe_allow_html=True)
st.write("---")

# --- FORMULÁRIO DE CAPTURA ---
st.subheader("➕ Novo Lançamento")
with st.form("formulario_lancamento", clear_on_submit=True):
    col_data, col_tipo = st.columns(2)
    with col_data:
        # LIMITAÇÃO DO CALENDÁRIO: Começa em 01/01/2026 e vai até 31/12/2050
        data_minima = date(2026, 1, 1)
        data_maxima = date(2050, 12, 31)
        
        data = st.date_input(
            "Data", 
            value=datetime.today().date(),
            min_value=data_minima,
            max_value=data_maxima
        )
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

# --- VISUALIZAÇÃO DO DASHBOARD ---
st.subheader("📊 Resumo Visual das Operações")

df_atual = st.session_state.dados

# CSS do cartão roxo do Excel
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

# LÓGICA DE DADOS: Se estiver vazio, força os dados idênticos à imagem do Excel
if df_atual.empty:
    st.info("💡 Exibindo dados demonstrativos idênticos ao modelo do Excel. Cadastre um lançamento acima para atualizar com seus dados reais!")
    
    total_despesas = 30585.00
    saldo_final = 63494.00
    
    meses_eixo = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    valores_eixo = [0, 2000, 0, 0, 5600, 18452, 0, 533, 0, 5700, 0, 0]
    
    df_receitas = pd.DataFrame({"Categoria": ["Receitas Operacionais 1", "Receitas Operacionais 2", "Receitas Não Operacionais"], "Valor": [44, 28, 28]})
    df_despesas = pd.DataFrame({"Categoria": ["Despesas Op 3", "Despesas Op 4", "Impostos", "Despesas Op 1", "Despesas Op 2"], "Valor": [55, 16, 16, 10, 3]})
    df_contas = pd.DataFrame({"Categoria": ["Despesas_op_1.1", "Despesas_op_1.2", "Despesas_op_1.4"], "Valor": [74, 21, 5]})
else:
    # Se já tiver dados cadastrados, calcula o real
    total_receitas = df_atual[df_atual["Tipo"] == "Receita (Entrada)"]["Valor"].sum()
    total_despesas = df_atual[df_atual["Tipo"] == "Despesa (Saída)"]["Valor"].sum()
    saldo_final = total_receitas - total_despesas
    
    df_visual = df_atual.copy()
    df_visual["Data"] = pd.to_datetime(df_visual["Data"])
    df_visual["Mês_Nome"] = df_visual["Data"].dt.strftime("%B")
    
    meses_map = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
        'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
        'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    df_visual["Mês_Nome"] = df_visual["Mês_Nome"].map(meses_map)
    
    meses_eixo = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    df_mensal = df_visual[df_visual["Tipo"] == "Despesa (Saída)"].groupby(["Mês_Nome"])["Valor"].sum().reset_index()
    df_meses_completos = pd.DataFrame({"Mês_Nome": meses_eixo})
    df_mensal = pd.merge(df_meses_completos, df_mensal, on="Mês_Nome", how="left").fillna(0)
    valores_eixo = df_mensal["Valor"].tolist()
    
    df_receitas = df_atual[df_atual["Tipo"] == "Receita (Entrada)"].groupby("Categoria")["Valor"].sum().reset_index()
    df_despesas = df_atual[df_atual["Tipo"] == "Despesa (Saída)"].groupby("Categoria")["Valor"].sum().reset_index()
    df_contas = df_atual.groupby("Categoria")["Valor"].sum().reset_index()

# --- RENDERIZAÇÃO DO LAYOUT ---
if plotly_disponivel:
    col_card, col_barra = st.columns(2)
    
    with col_card:
        st.markdown(f"""
            <div class="card-roxo">
                <p style="margin:0; font-size:16px; font-weight:bold; opacity:0.9;">Total das Operações no ano</p>
                <h1 style="margin:0; font-size:38px; color:white; font-weight:bold;">R$ {total_despesas:,.2f}</h1>
                <p style="margin:0; font-size:13px; opacity:0.8; margin-top:15px;">
                    Saldo em Caixa: R$ {saldo_final:,.2f}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_barra:
        st.markdown("<p style='font-weight:bold; margin-bottom:0;'>Gráfico Mensal de Plano Selecionado</p>", unsafe_allow_html=True)
        fig_barra = go.Figure(data=[go.Bar(
            x=meses_eixo, y=valores_eixo,
            text=[f"R$ {v:,.0f}" if v > 0 else "" for v in valores_eixo],
            textposition='outside',
            marker_color='#F5B041'
        )])
        fig_barra.update_layout(
            height=220, margin=dict(t=25, b=10, l=10, r=10),
            yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white")
        )
        st.plotly_chart(fig_barra, use_container_width=True)

    st.write("---")
    
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Top 3 Receitas do Plano %</p>", unsafe_allow_html=True)
        if not df_receitas.empty and df_receitas["Valor"].sum() > 0:
            fig1 = px.pie(df_receitas, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=['#2E7D32', '#9C27B0', '#F5B041'])
            fig1.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.caption("<p style='text-align:center; color:gray; padding-top:20px;'>Nenhuma receita cadastrada</p>", unsafe_allow_html=True)

    with col_g2:
        st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Top 5 Despesas do Plano %</p>", unsafe_allow_html=True)
        if not df_despesas.empty and df_despesas["Valor"].sum() > 0:
            fig2 = px.pie(df_despesas, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=['#900C3F', '#C70039', '#FF5733', '#FFC300', '#DAF7A6'])
            fig2.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("<p style='text-align:center; color:gray; padding-top:20px;'>Nenhuma despesa cadastrada</p>", unsafe_allow_html=True)

    with col_g3:
        st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>Top 5 Contas desse Plano</p>", unsafe_allow_html=True)
        if not df_contas.empty and df_contas["Valor"].sum() > 0:
            fig3 = px.pie(df_contas, values='Valor', names='Categoria', hole=0.5, color_discrete_sequence=['#F5B041', '#2E7D32', '#9C27B0'])
            fig3.update_layout(showlegend=True, height=220, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.caption("<p style='text-align:center; color:gray; padding-top:20px;'>Nenhum registro cadastrado</p>", unsafe_allow_html=True)
else:
    st.warning("Aguardando carregamento dos componentes visuais do Plotly.")

# --- HISTÓRICO ORIGINAL ---
st.write("---")
st.subheader("📋 Histórico de Transações")
if not df_atual.empty:
    df_exibicao = df_atual.sort_values(by="Data", ascending=False)
    st.dataframe(df_exibicao, use_container_width=True)
    
    if st.button("⚠️ Limpar Todos os Dados"):
        st.session_state.dados = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
        if os.path.exists(ARQUIVO_DADOS):
            os.remove(ARQUIVO_DADOS)
