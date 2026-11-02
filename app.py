import streamlit as st
import pandas as pd
import random
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import re  # <- Biblioteca para Expressões Regulares

st.set_page_config(page_title="Validação de Clareza Textual", layout="centered")
st.title("🧪 Pesquisa de Clareza e Leitura")
st.caption("v5.0 - Blindagem Total (Expressões Regulares)")
st.write("Escolha qual das duas frases é mais fácil e agradável de entender.")

# --- CONFIGURAÇÃO GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # 1. Tenta usar o ficheiro local (no computador)
        credenciais = Credentials.from_service_account_file("credentials.json", scopes=escopos)
    except FileNotFoundError:
        # 2. Nuvem: Puxa os dados nativos do TOML configurado nos Secrets
        dict_credenciais = dict(st.secrets["gcp_service_account"])
        
        # --- BLINDAGEM TOTAL DA CHAVE PRIVADA ---
        if "private_key" in dict_credenciais:
            pk = str(dict_credenciais["private_key"]).replace("\\n", "\n")
            
            # Procura o início e o fim da chave para isolar o miolo
            match = re.search(r'-----BEGIN PRIVATE KEY-----(.*?)-----END PRIVATE KEY-----', pk, re.DOTALL)
            
            if match:
                # Extrai apenas os caracteres válidos de Base64 (ignora TUDO o resto: \n, \r, espaços, lixo invisível)
                clean_b64 = re.sub(r'[^a-zA-Z0-9+/=]', '', match.group(1))
                
                # Garante que o comprimento é múltiplo de 4 (corrige o problema do '1625')
                clean_b64 += "=" * ((4 - len(clean_b64) % 4) % 4)
                
                # Reconstrói em linhas perfeitas de exatamente 64 caracteres
                chunks = [clean_b64[i:i+64] for i in range(0, len(clean_b64), 64)]
                dict_credenciais["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(chunks) + "\n-----END PRIVATE KEY-----\n"
            
        credenciais = Credentials.from_service_account_info(dict_credenciais, scopes=escopos)
        
    cliente = gspread.authorize(credenciais)
    return cliente.open("Respostas_Motor_Semantico").sheet1

try:
    planilha = conectar_google_sheets()
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets. Verifique as credenciais. Erro: {e}")
    st.stop()
# -----------------------------------

@st.cache_data
def carregar_dados():
    df = pd.read_excel("planilha_testes_ab.xlsx")
    return df

try:
    df_testes = carregar_dados()
    
    if "index_atual" not in st.session_state:
        st.session_state.index_atual = 0
    if "sessao_id" not in st.session_state:
        st.session_state.sessao_id = str(uuid.uuid4())[:8] 

    idx = st.session_state.index_atual

    if idx < len(df_testes):
        linha = df_testes.iloc[idx]
        id_par = f"Par_{idx + 1}"
        
        st.progress((idx) / len(df_testes))
        st.subheader(f"Par {idx + 1} de {len(df_testes)}")

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
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                nova_linha = [data_hora, st.session_state.sessao_id, id_par, linha["Frase_A"], linha["Frase_B"], opcao_1[0]]
                planilha.append_row(nova_linha)
                
                st.session_state.index_atual += 1
                st.rerun()

        with col2:
            st.info(opcao_2[1])
            if st.button("Preferir esta versão", key="btn_2"):
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                nova_linha = [data_hora, st.session_state.sessao_id, id_par, linha["Frase_A"], linha["Frase_B"], opcao_2[0]]
                planilha.append_row(nova_linha)
                
                st.session_state.index_atual += 1
                st.rerun()
    else:
        st.success("🎉 Obrigado! Você concluiu todos os testes. Seus votos foram salvos na nuvem!")
        
except Exception as e:
    st.error(f"Erro na aplicação: {e}")
