import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import pytz
from datetime import datetime

# --- CONFIGURAÇÃO GOOGLE SHEETS ---
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(service_account_info, 
         scopes=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])
client = gspread.authorize(creds)
planilha = client.open("Cartão de Ponto")

# --- FUNÇÃO ---
def mostrar_agenda_escalas(usuario, tipo_usuario):
    # abre a aba dentro da função (ou você pode pré-definir fora)
    escalas_sheet = planilha.worksheet("escalas")
    # usa o pandas (pd) para criar DataFrame
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
                    nome,
                    data.strftime("%d/%m/%Y"),
                    inicio.strftime("%H:%M"),
                    fim.strftime("%H:%M"),
                    obs
                ])
                st.success("Escala cadastrada com sucesso!")
                st.rerun()

    if not escalas.empty:
        st.dataframe(escalas)
    else:
        st.info("Nenhuma escala cadastrada ainda.")

