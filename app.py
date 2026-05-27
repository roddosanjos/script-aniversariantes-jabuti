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

# Estilização CSS Festiva combinando com as cores do Clube (Verdes e Laranja)
st.markdown("""
    <style>
        /* Fundo da aplicação com efeito sutil de confetes festivos */
        .stApp {
            background-color: #F4F7F4;
            background-image: radial-gradient(rgba(255, 87, 34, 0.15) 1px, transparent 0), 
                              radial-gradient(rgba(142, 229, 63, 0.2) 1px, transparent 0);
            background-size: 24px 24px;
            background-position: 0 0, 12px 12px;
        }
        
        /* Título Principal */
        .titulo-principal {
            color: #114716; /* Verde Escuro da logo */
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 800;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 2px;
        }
        
        /* Subtítulo */
        .subtitulo {
            color: #444444;
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        /* Customização do Botão de Busca - Estilo Festivo */
        div.stButton > button {
            background: linear-gradient(135deg, #228B22 0%, #114716 100%) !important;
            color: white !important;
            border-radius: 20px !important; /* Mais arredondado/moderno */
            border: none !important;
            font-weight: bold !important;
            padding: 12px 30px !important;
            box-shadow: 0 4px 10px rgba(34, 139, 34, 0.3) !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #FF5722 0%, #E64A19 100%) !important; /* Muda para Laranja Festivo */
            box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Card do Aniversariante - Estilo Festa 🎉 */
        .card-aniversariante {
            background-color: #FFFFFF;
            border-left: 6px solid #FF5722; /* Laranja Festivo */
            border-right: 2px solid #8EE53F; /* Detalhe em Verde Limão */
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.06);
            position: relative;
            overflow: hidden;
        }
        
        /* Balões decorativos de fundo no card */
        .card-aniversariante::after {
            content: "🎈";
            position: absolute;
            right: 15px;
            top: 15px;
            font-size: 1.8rem;
            opacity: 0.3;
        }
        
        .nome-aniversariante {
            color: #114716; 
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 8px;
            border-bottom: 1px dashed #E0E0E0;
            padding-bottom: 4px;
        }
        
        .info-linha {
            font-size: 1.05rem;
            color: #333333;
            margin: 6px 0;
        }
        
        /* Link da foto como um botão comemorativo */
        .link-foto {
            display: inline-block;
            margin-top: 10px;
            background-color: #FBEBE6;
            color: #FF5722;
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            transition: background 0.2s;
        }
        .link-foto:hover {
            background-color: #FF5722;
            color: white;
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

# CORREÇÃO DA LOGO: Alterado de logo.png para logo.jpg conforme o seu repositório
if os.path.exists("logo.jpg"):
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.image("logo.jpg", use_container_width=True)

# Título e Subtítulo
st.markdown('<h1 class="titulo-principal">Jabuti do Lavrado</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">🎂 Painel Festivo de Aniversariantes 🎈</p>', unsafe_allow_html=True)

# Bloco de input
data_input = st.text_input("Qual data deseja festejar? (Exemplo: 31/05)", placeholder="DD/MM")

if st.button("✨ Buscar Aniversariantes ✨", use_container_width=True):
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

            st.markdown(f"#### 🥳 Aniversariantes do dia {data_input}:")
            st.write("") 
            
            if aniversariantes_encontrados:
                for pessoa in aniversariantes_encontrados:
                    foto_html = ""
                    if pessoa['Foto'] != "Sem foto cadastrada" and pessoa['Foto'].startswith("http"):
                        foto_html = f'<a class="link-foto" href="{pessoa["Foto"]}" target="_blank">📸 Ver foto para postagem</a>'
                    else:
                        foto_html = '<span style="color: #999999; font-style: italic; display:block; margin-top:10px;">📸 Sem foto cadastrada</span>'

                    st.markdown(f"""
                        <div class="card-aniversariante">
                            <div class="nome-aniversariante">🎉 {pessoa['Nome']}</div>
                            <div class="info-linha">🎁 <b>Idade:</b> {pessoa['Idade']} anos</div>
                            <div class="info-linha">📞 <b>Telefone:</b> {pessoa['Telefone']}</div>
                            {foto_html}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum integrante do clube faz aniversário nessa data. 🏃‍♂️💨")

        except ValueError:
            st.error("Formato inválido! Por favor, utilize o padrão Dia/Mês com dois dígitos (Ex: 05/08).")
