import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import streamlit as st

# Autenticação com Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

# Acesso às planilhas
planilha = client.open("Cartão de Ponto")
usuarios_sheet = planilha.worksheet("usuarios")
registros_sheet = planilha.worksheet("registros")

# Verifica se o login é válido
def verificar_login(usuario, senha):
    dados = usuarios_sheet.get_all_records()
    for row in dados:
        if row["Nome"] == usuario and row["Senha"] == senha:
            return True
    return False

# Registra ponto (entrada, almoço e saída)
def registrar_ponto(usuario):
    hoje = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    registros = registros_sheet.get_all_records()

    for i, row in enumerate(registros, start=2):  # start=2 porque a primeira linha é o cabeçalho
        if row["Nome"] == usuario and row["Data"] == hoje:
            if row["Entrada"] == "":
                registros_sheet.update_cell(i, 3, hora)
                st.success("Entrada registrada!")
            elif row["Saída Almoço"] == "":
                registros_sheet.update_cell(i, 4, hora)
                st.success("Saída para almoço registrada!")
            elif row["Retorno Almoço"] == "":
                registros_sheet.update_cell(i, 5, hora)
                st.success("Retorno do almoço registrado!")
            elif row["Saída"] == "":
                registros_sheet.update_cell(i, 6, hora)
                st.success("Saída registrada!")
            else:
                st.info("Todos os pontos já foram registrados hoje.")
            return

    # Caso ainda não exista registro no dia, cria um novo
    registros_sheet.append_row([usuario, hoje, hora, "", "", "", ""])
    st.success("Entrada registrada!")

# Calcula o total de horas trabalhadas
def calcular_total(entrada, saida_almoco, retorno_almoco, saida):
    formato = "%H:%M:%S"
    try:
        entrada = datetime.strptime(entrada, formato)
        saida_almoco = datetime.strptime(saida_almoco, formato)
        retorno_almoco = datetime.strptime(retorno_almoco, formato)
        saida = datetime.strptime(saida, formato)

        manha = saida_almoco - entrada
        tarde = saida - retorno_almoco
        total = manha + tarde
        return str(total)
    except Exception:
        return ""

# Mostra o histórico do usuário logado
def mostrar_historico(usuario):
    dados = registros_sheet.get_all_records()
    historico = []

    for row in dados:
        if row["Nome"] == usuario:
            total = calcular_total(
                row.get("Entrada", ""),
                row.get("Saída Almoço", ""),
                row.get("Retorno Almoço", ""),
                row.get("Saída", "")
            )
            row["Total"] = total
            historico.append(row)

    if historico:
        st.markdown("### 📋 Histórico de Pontos")
        st.table(historico)
    else:
        st.info("Nenhum registro encontrado.")



