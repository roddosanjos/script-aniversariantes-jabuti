import streamlit as st
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuração visual da página
st.set_page_config(page_title="Aniversariantes Jabuti", page_icon="🎉", layout="centered")

st.title("🎉 Consulta de Aniversariantes")
st.write("Digite o dia e o mês para listar quem está de parabéns nessa data.")

# --------------------- Autenticação com o Google Sheets ---------------------
@st.cache_data(ttl=300)  # Guarda os dados na memória por 5 minutos para ficar rápido
def carregar_dados():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # O Streamlit lê as credenciais de forma segura através dos 'secrets' da plataforma
    credenciais_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
    
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(credenciais_json), escopo)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open('Aniversariantes Jabuti do Lavrado').sheet1  
    return planilha.get_all_records()

try:
    dados = carregar_dados()
except Exception as e:
    st.error(f"Erro ao conectar com a planilha do Google: {e}")
    st.stop()

# --------------------- Interface do Usuário ---------------------

# Campo de texto simples para quem não é de TI preencher facilmente
data_input = st.text_input("Insira a data desejada (Formato: DD/MM)", placeholder="Ex: 25/05")

if st.button("🔍 Buscar Aniversariantes", use_container_width=True):
    if not data_input:
        st.warning("Por favor, digite uma data primeiro!")
    else:
        try:
            # Converte e padroniza o que o usuário digitou (Ex: "05/05" vira "05-05")
            data_objeto = datetime.strptime(data_input, '%d/%m')
            alvo_busca = data_objeto.strftime('%m-%d')
            
            aniversariantes_encontrados = []
            ano_atual = datetime.now().year

            for linha in dados:
                try:
                    # Lê a data de nascimento da planilha
                    data_aniversario = datetime.strptime(linha['Data de Nascimento'], '%d/%m/%Y')
                    
                    if data_aniversario.strftime('%m-%d') == alvo_busca:
                        # Cálculo da idade
                        idade = ano_atual - data_aniversario.year
                        
                        foto = linha['Sua foto para postagem'] if linha['Sua foto para postagem'] else "Sem foto cadastrada"
                        
                        aniversariantes_encontrados.append({
                            'Nome': linha['Nome Completo'],
                            'Idade': idade,
                            'Telefone': linha['Telefone p/ contato'],
                            'Foto': foto
                        })
                except:
                    continue # Ignora linhas com erro de preenchimento na planilha

            # --------------------- Exibição dos Resultados ---------------------
            st.markdown(f"### 📋 Resultados para o dia {data_input}")
            
            if aniversariantes_encontrados:
                for pessoa in aniversariantes_encontrados:
                    # Cria um box visual limpo para cada aniversariante
                    with st.container():
                        st.success(f"🎂 **{pessoa['Nome']}**")
                        st.write(f"🎁 **Idade:** {pessoa['Idade']} anos")
                        st.write(f"📞 **Telefone:** {pessoa['Telefone']}")
                        
                        if pessoa['Foto'] != "Sem foto cadastrada" and pessoa['Foto'].startswith("http"):
                            st.write(f"📸 **Foto para postagem:** [Clique aqui para abrir]({pessoa['Foto']})")
                        else:
                            st.write("📸 *Sem foto cadastrada ou link inválido*")
                        st.markdown("---")
            else:
                st.info("Nenhum aniversariante encontrado para essa data. 🕊️")

        except ValueError:
            st.error("Formato incorreto! Lembre-se de usar duas casas para o dia e para o mês. Exemplo: **02/04**")
