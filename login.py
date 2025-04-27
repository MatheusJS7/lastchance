
import json
import streamlit as st
import pytz
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# --- Configuração da página ---
st.set_page_config(page_title="Cartão de Ponto", page_icon="🕒", layout="wide")

# --- Estilos personalizados ---
st.markdown("""
    <style>
        .stApp { background-color: #800000; }
        .stButton>button {
            background-color: #f5f5dc;
            color: black;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stButton>button:hover {
            background-color: #f5f5dc;
        }
        .stTextInput>div>div>input,
        .stDateInput>div>input {
            color: #ffffff !important;
            font-weight: bold;
            border: 2px solid #800020 !important;
            border-radius: 4px !important;
        }
        .stTable td, .stTable th {
            color: #ffffff;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #ffffff;
        }
        .stImage {
            width: 100px;
            height: auto;
        }
    </style>
""", unsafe_allow_html=True)

# --- Adicionar logo ---
try:
    st.image("logo.jpeg", width=150)
except:
    st.warning("⚠️ Logo não encontrada. Verifique se 'logo.jpeg' está na mesma pasta do código.")

# --- Autenticação com Google Sheets (via Streamlit Secrets) ---
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
# Carrega credenciais do secrets.toml
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
client = gspread.authorize(creds)
planilha = client.open("Cartão de Ponto")
usuarios_sheet = planilha.worksheet("usuarios")
registros_sheet = planilha.worksheet("registros")
escalas_sheet = planilha.worksheet("escalas")

# --- Funções principais ---
def verificar_login(usuario, senha):
    for row in usuarios_sheet.get_all_records():
        if (
            str(row.get("Nome", "")).strip().lower() == usuario.strip().lower()
            and str(row.get("Senha", "")).strip() == senha.strip()
        ):
            return True
    return False

def obter_tipo_usuario(usuario):
    for row in usuarios_sheet.get_all_records():
        if str(row.get("Nome", "")).strip().lower() == usuario.strip().lower():
            return row.get("Tipo", "").lower()
    return "comum"

def calcular_total(entrada, saida_almoco, retorno_almoco, saida):
    fmt = "%H:%M:%S"
    try:
        e = datetime.strptime(entrada, fmt)
        sa = datetime.strptime(saida_almoco, fmt)
        ra = datetime.strptime(retorno_almoco, fmt)
        s = datetime.strptime(saida, fmt)
        total = (sa - e) + (s - ra)
        return str(total), total.total_seconds() / 3600
    except:
        return "", 0

def registrar_ponto(usuario):
    fuso_sp = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_sp)
    hoje = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")

    registros = registros_sheet.get_all_records()
    for i, row in enumerate(registros, start=2):
        if row["Nome"] == usuario and row["Data"] == hoje:
            if not row["Entrada"]:
                registros_sheet.update_cell(i, 3, hora)
                st.success("Entrada registrada!")
            elif not row["Saída Almoço"]:
                registros_sheet.update_cell(i, 4, hora)
                st.success("Saída almoço registrada!")
            elif not row["Retorno Almoço"]:
                registros_sheet.update_cell(i, 5, hora)
                st.success("Retorno almoço registrado!")
            elif not row["Saída"]:
                registros_sheet.update_cell(i, 6, hora)
                total, hrs = calcular_total(
                    row["Entrada"],
                    row["Saída Almoço"],
                    row["Retorno Almoço"],
                    hora
                )
                registros_sheet.update_cell(i, 7, total)
                extra = max(0, hrs - 8)
                registros_sheet.update_cell(i, 9, f"{extra:.2f}")
                st.success("Saída registrada!")
            else:
                st.info("Pontos de hoje completos.")
            return
    registros_sheet.append_row([usuario, hoje, hora, "", "", "", "", "", ""])
    st.success("Entrada registrada!")
    
def mostrar_historico(usuario):
    df = pd.DataFrame(registros_sheet.get_all_records())
    df = df[df["Nome"].str.lower() == usuario.strip().lower()]
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    with st.expander("📅 Filtrar por período"):
        inicio = st.date_input("Início", value=datetime.now())
        fim = st.date_input("Fim", value=datetime.now())
        df["Data_dt"] = pd.to_datetime(df["Data"], dayfirst=True)
        df = df[(df["Data_dt"] >= pd.to_datetime(inicio)) & (df["Data_dt"] <= pd.to_datetime(fim))]

    st.markdown("### Histórico de Pontos")
    st.dataframe(df.drop(columns=["Data_dt"]))

    # gráfico de horas extras
    df["Total_timedelta"] = pd.to_timedelta(df["Total"].fillna("0:00:00"))
    df["Horas"] = df["Total_timedelta"].dt.total_seconds() / 3600
    st.markdown("### Horas Trabalhadas por Dia")
    fig = px.bar(df, x="Data", y="Horas", labels={"Horas": "Horas (h)"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

def mostrar_agenda_escalas(usuario, tipo_usuario):
    escalas = pd.DataFrame(escalas_sheet.get_all_records())
    
    st.subheader("📆 Agenda de Escalas")
    
    if tipo_usuario == "gestor":
        with st.expander("➕ Cadastrar Escala"):
            nome = st.text_input("Nome do Funcionário")
            data = st.date_input("Data da Escala")
            inicio = st.time_input("Horário de Início")
            fim = st.time_input("Horário de Fim")
            obs = st.text_area("Observações")

            if st.button("Salvar Escala"):
                escalas_sheet.append_row([
                    nome, data.strftime("%d/%m/%Y"),
                    inicio.strftime("%H:%M"), fim.strftime("%H:%M"), obs
                ])
                st.success("Escala cadastrada com sucesso!")
                st.rerun()

    if not escalas.empty:
        if tipo_usuario == "gestor":
            st.dataframe(escalas)
        else:
            escalas_usuario = escalas[escalas["Nome"].str.lower() == usuario.lower()]
            st.dataframe(escalas_usuario)
    else:
        st.info("Nenhuma escala cadastrada ainda.")

# --- Interface de Login / Main ---
if "usuario_logado" not in st.session_state:
    st.subheader("🔐 Login")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if verificar_login(user, pwd):
            st.session_state.usuario_logado = user
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# Usuário logado
usuario = st.session_state.usuario_logado
tipo_usuario = obter_tipo_usuario(usuario)

col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(f"<h4 style='color:#cd7f32;'>👤 Bem‑vindo, <b>{usuario.capitalize()}</b></h4>", unsafe_allow_html=True)
with col2:
    if st.button("🚪 Sair"):
        del st.session_state.usuario_logado
        st.rerun()

# Menu principal
opcao = st.radio("", ["Registrar Ponto", "Histórico", "Agenda de Escalas"], horizontal=True)
if opcao == "Registrar Ponto":
    st.subheader("📍 Registro de Ponto")
    if st.button("Registrar agora"):
        registrar_ponto(usuario)
elif opcao == "Histórico":
    mostrar_historico(usuario)
elif opcao == "Agenda de Escalas":
    mostrar_agenda_escalas(usuario, tipo_usuario)










