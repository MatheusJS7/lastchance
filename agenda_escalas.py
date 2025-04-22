def mostrar_agenda_escalas(usuario, tipo_usuario):
    escalas_sheet = planilha.worksheet("escalas")
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
