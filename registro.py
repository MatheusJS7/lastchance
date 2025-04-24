import streamlit as st
import gspread
import pytz
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuração da planilha Google
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

# Abre a planilha e a aba de registros
spreadsheet = client.open("Cartão de Ponto")
registro_sheet = spreadsheet.worksheet("registros")

# Função para registrar o ponto
def registrar_ponto(usuario, tipo_ponto):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    hora_atual = datetime.now().strftime("%H:%M:%S")
    
    # Adiciona o ponto na planilha
    registro_sheet.append_row([data_atual, usuario, tipo_ponto, hora_atual])
    st.success(f"{tipo_ponto} registrado com sucesso!")

# Página de registro de ponto
if 'usuario_logado' in st.session_state:
    st.title(f"Registro de Ponto de {st.session_state['usuario_logado']}")

    # Botões para registrar os pontos
    if st.button("Registrar Entrada"):
        registrar_ponto(st.session_state['usuario_logado'], "Entrada")
    
    if st.button("Registrar Saída"):
        registrar_ponto(st.session_state['usuario_logado'], "Saída")
    
    if st.button("Registrar Almoço"):
        registrar_ponto(st.session_state['usuario_logado'], "Almoço")

    if st.button("Registrar Retorno Almoço"):
        registrar_ponto(st.session_state['usuario_logado'], "Retorno Almoço")
else:
    st.error("Você precisa estar logado para acessar esta página.")
