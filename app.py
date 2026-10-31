import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Validação de Clareza Textual", layout="centered")
st.title("🧪 Pesquisa de Clareza e Leitura")
st.write("Escolha qual das duas frases é mais fácil e agradável de entender.")

@st.cache_data
def carregar_dados():
    # Lê a planilha preenchida pelo Especialista de Domínio
    df = pd.read_excel("planilha_testes_ab.xlsx")
    return df

try:
    df_testes = carregar_dados()
    
    if "index_atual" not in st.session_state:
        st.session_state.index_atual = 0
    if "votos" not in st.session_state:
        st.session_state.votos = []

    idx = st.session_state.index_atual

    if idx < len(df_testes):
        linha = df_testes.iloc[idx]
        
        st.progress((idx) / len(df_testes))
        st.subheader(f"Par {idx + 1} de {len(df_testes)}")

        # Embaralha a ordem de exibição para eliminar viés de posição
        opcoes = [("A", linha["Frase_A"]), ("B", linha["Frase_B"])]
        if "ordem_embaralhada" not in st.session_state or st.session_state.get("idx_salvo") != idx:
            random.shuffle(opcoes)
            st.session_state.ordem_embaralhada = opcoes
            st.session_state.idx_salvo = idx

        opcao_1, opcao_2 = st.session_state.ordem_embaralhada

        col1, col2 = st.columns(2)
        
        with col1:
            st.info(opcao_1[1])
            if st.button("Preferir esta versão", key="btn_1"):
                st.session_state.votos.append({"categoria": linha["Categoria"], "escolha": opcao_1[0]})
                st.session_state.index_atual += 1
                st.rerun()

        with col2:
            st.info(opcao_2[1])
            if st.button("Preferir esta versão", key="btn_2"):
                st.session_state.votos.append({"categoria": linha["Categoria"], "escolha": opcao_2[0]})
                st.session_state.index_atual += 1
                st.rerun()
    else:
        st.success("🎉 Obrigado! Você concluiu todos os testes.")
        df_resultados = pd.DataFrame(st.session_state.votos)
        df_resultados.to_csv("resultados_votos_ab.csv", index=False)
        
except Exception as e:
    st.error(f"Aguardando a planilha 'planilha_testes_ab.xlsx'. Erro: {e}")