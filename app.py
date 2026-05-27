import streamlit as st
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------- Configuração Visual da Página ---------------------
st.set_page_config(
    page_title="Aniversariantes - Jabuti do Lavrado", 
    page_icon="🎉", 
    layout="centered"
)

# Estilização CSS para aplicar o padrão de cores moderno (Verdes e Laranja)
st.markdown("""
    <style>
        /* Cor de fundo da aplicação */
        .stApp {
            background-color: #F7F9F7;
        }
        
        /* Título Principal */
        .titulo-principal {
            color: #114716; /* Verde Escuro da logo */
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 800;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        
        /* Subtítulo */
        .subtitulo {
            color: #666666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }
        
        /* Customização do Botão de Busca */
        div.stButton > button {
            background-color: #228B22 !important; /* Verde oficial */
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #FF5722 !important; /* Transição para Laranja no Hover */
            color: white !important;
            transform: scale(1.02);
        }
        
        /* Card do Aniversariante */
        .card-aniversariante {
            background-color: #FFFFFF;
            border-left: 6px solid #8EE53F; /* Verde Limão da Camiseta/Logo */
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .nome-aniversariante {
            color: #FF5722; /* Laranja de destaque da logo */
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .info-linha {
            font-size: 1rem;
            color: #333333;
            margin: 4px 0;
        }
        
        /* Link da foto estilizado como botão discreto */
        .link-foto {
            display: inline-block;
            margin-top: 8px;
            color: #228B22;
            text-decoration: none;
            font-weight: bold;
        }
        .link-foto:hover {
            color: #FF5722;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------- Autenticação com o Google Sheets ---------------------
@st.cache_data(ttl=300)
def carregar_dados():
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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

# Adiciona e centraliza a logo do clube no topo (busca o arquivo logo.png do repositório)
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1.2, 1]) # Cria colunas para centralizar a imagem
    with col2:
        st.image("logo.png", use_container_width=True)

# Título estilizado
st.markdown('<h1 class="titulo-principal">Jabuti do Lavrado</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Consulte os aniversariantes do clube inserindo o dia e o mês</p>', unsafe_allow_html=True)

# Bloco de input
data_input = st.text_input("Data de consulta (Exemplo: 31/05)", placeholder="DD/MM")

if st.button("Buscar Aniversariantes", use_container_width=True):
    if not data_input:
        st.warning("Por favor, preencha uma data para realizar a busca.")
    else:
        try:
            data_objeto = datetime.strptime(data_input, '%d/%m')
            alvo_busca = data_objeto.strftime('%m-%d')
            
            aniversariantes_encontrados = []
            ano_atual = datetime.now().year

            for linha in dados:
                try:
                    data_aniversario = datetime.strptime(linha['Data de Nascimento'], '%d/%m/%Y')
                    if data_aniversario.strftime('%m-%d') == alvo_busca:
                        idade = ano_atual - data_aniversario.year
                        foto = linha['Sua foto para postagem'] if linha['Sua foto para postagem'] else "Sem foto cadastrada"
                        
                        aniversariantes_encontrados.append({
                            'Nome': linha['Nome Completo'],
                            'Idade': idade,
                            'Telefone': linha['Telefone p/ contato'],
                            'Foto': foto
                        })
                except:
                    continue

            st.markdown(f"#### 📋 Resultados para o dia {data_input}:")
            st.write("") 
            
            if aniversariantes_encontrados:
                for pessoa in aniversariantes_encontrados:
                    foto_html = ""
                    if pessoa['Foto'] != "Sem foto cadastrada" and pessoa['Foto'].startswith("http"):
                        foto_html = f'<a class="link-foto" href="{pessoa[\'Foto\']}" target="_blank">📸 Abrir foto para postagem</a>'
                    else:
                        foto_html = '<span style="color: #999999; font-style: italic;">📸 Sem foto cadastrada</span>'

                    st.markdown(f"""
                        <div class="card-aniversariante">
                            <div class="nome-aniversariante">🏃‍♂️ {pessoa['Nome']}</div>
                            <div class="info-linha">🎁 <b>Idade:</b> {pessoa['Idade']} anos</div>
                            <div class="info-linha">📞 <b>Telefone:</b> {pessoa['Telefone']}</div>
                            {foto_html}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum integrante do clube faz aniversário nessa data. 🏃‍♂️💨")

        except ValueError:
            st.error("Formato inválido! Por favor, utilize o padrão Dia/Mês com dois dígitos (Ex: 05/08).")
