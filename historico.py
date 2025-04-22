import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuração da planilha Google
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

# Abre a planilha e a aba de registros
spreadsheet = client.open("Cartão de Ponto")
registro_sheet = spreadsheet.worksheet("registros")

# Função para mostrar o histórico
def mostrar_historico(usuario):
    registros = registro_sheet.get_all_records()
    df = pd.DataFrame(registros)
    df_filtrado = df[df['Nome'] == usuario]
    
    if not df_filtrado.empty:
        st.write(df_filtrado)
    else:
        st.write("Nenhum registro encontrado.")

# Página de histórico
if 'usuario_logado' in st.session_state:
    st.title(f"Histórico de Ponto de {st.session_state['usuario_logado']}")
    mostrar_historico(st.session_state['usuario_logado'])
else:
    st.error("Você precisa estar logado para acessar esta página.")
