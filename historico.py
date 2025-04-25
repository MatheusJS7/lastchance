import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuração da planilha Google
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
client = gspread.authorize(creds)

# Abre a planilha e a aba de registros
spreadsheet = client.open("Cartão de Ponto")
registro_sheet = spreadsheet.worksheet("registros")

# Função para mostrar o histórico
def mostrar_historico(usuario):
    registros = registro_sheet.get_all_records()
    df = pd.DataFrame(registros)
    df_filtrado = df[df['Nome'].str.lower() == usuario.lower()]

    if not df_filtrado.empty:
        st.subheader("📜 Histórico de Registros")
        st.dataframe(df_filtrado)
    else:
        st.info("Nenhum registro encontrado.")

# Página de histórico
if 'usuario_logado' in st.session_state:
    st.title(f"👤 Histórico de Ponto - {st.session_state['usuario_logado'].capitalize()}")
    mostrar_historico(st.session_state['usuario_logado'])
else:
    st.error("⚠️ Você precisa estar logado para acessar esta página.")

