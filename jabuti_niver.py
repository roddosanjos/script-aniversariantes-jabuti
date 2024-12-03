import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------------Autenticação com o Google Sheets------------------------------------
# Definir o escopo de acesso
escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carregar as credenciais do Google Cloud a partir da variável de ambiente
credenciais_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

# Verifique se a variável de ambiente foi configurada corretamente
if credenciais_json is None:
    raise ValueError("As credenciais do Google Cloud não foram configuradas no GitHub Secrets.")

# Verificar se a variável não está vazia
if not credenciais_json:
    raise ValueError("A variável de ambiente 'GOOGLE_CREDENTIALS_JSON' está vazia ou não foi configurada corretamente.")

# Exibir o conteúdo para depuração (cuidado para não exibir informações sensíveis)
print("Conteúdo das credenciais JSON:", credenciais_json)

# Converter a variável de ambiente JSON em um dicionário
credenciais = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(credenciais_json), escopo)

# Autenticar e acessar o Google Sheets
cliente = gspread.authorize(credenciais)

# Abrir a planilha pelo nome
planilha = cliente.open('Aniversariantes Jabuti do Lavrado').sheet1  # Substitua pelo nome da sua planilha

# Obter todos os dados da planilha
dados = planilha.get_all_records()

# Exibir os dados para verificar se carregou corretamente
print(dados)

# ---------------------Verificar aniversariantes do dia------------------------------------
# Obter a data de hoje no formato (dia-mês)
hoje = datetime.today().strftime('%m-%d')  # No formato 'MM-DD'

# Filtrar aniversariantes de hoje
aniversariantes_hoje = []
for linha in dados:
    # Converter a data de nascimento para o formato datetime usando o formato correto
    data_aniversario = datetime.strptime(linha['Data de Nascimento'], '%d/%m/%Y')
    aniversario_formatado = data_aniversario.strftime('%m-%d')  # Formatar como 'MM-DD'
    
    # Comparar a data do aniversário (sem o ano) com a data de hoje
    if aniversario_formatado == hoje:
        # Calcular a idade
        hoje_date = datetime.today()
        idade = hoje_date.year - data_aniversario.year
        if hoje_date.month < data_aniversario.month or (hoje_date.month == data_aniversario.month and hoje_date.day < data_aniversario.day):
            idade -= 1  # Se ainda não fez aniversário este ano, subtrair 1
        
        # Adicionar o aniversariante com nome, idade e telefone
        aniversariantes_hoje.append({
            'Nome': linha['Nome Completo'],
            'Idade': idade,
            'Telefone': linha['Telefone p/ contato']
        })

# ---------------------Criar a mensagem para E-mail------------------------------------
# Criar a mensagem
if aniversariantes_hoje:
    # Se houver aniversariantes, cria a lista
    mensagem = "Lista de aniversariantes de hoje:\n\n"
    for aniversariante in aniversariantes_hoje:
        mensagem += f"Nome: {aniversariante['Nome']}, Idade: {aniversariante['Idade']}, Telefone: {aniversariante['Telefone']}\n"
    mensagem += "\nFeliz aniversário a todos! 🎉🎂"
else:
    # Se não houver aniversariantes
    mensagem = "Hoje não há aniversariantes. 🎉"

# ---------------------Função para enviar E-mail------------------------------------
def enviar_email(remetente, senha, destinatarios, mensagem):
    # Configuração do servidor SMTP do Gmail
    servidor = 'smtp.gmail.com'
    porta = 587  # Porta para enviar e-mails via TLS

    # Criar a estrutura do e-mail
    email = MIMEMultipart()
    email['From'] = remetente
    email['Subject'] = "Aniversariantes do dia"
    
    # Definir 'To' com um valor genérico ou vazio
    email['To'] = remetente  # Pode ser o seu e-mail ou um e-mail genérico
    
    # Corpo do e-mail
    corpo = MIMEText(mensagem, 'plain')
    email.attach(corpo)

    # Conectar ao servidor SMTP e enviar o e-mail
    try:
        with smtplib.SMTP(servidor, porta) as server:
            server.starttls()  # Usar conexão segura
            server.login(remetente, senha)  # Logar no servidor SMTP
            email['Bcc'] = ', '.join(destinatarios)  # Enviar para todos os destinatários no Bcc
            server.sendmail(remetente, destinatarios, email.as_string())  # Enviar o e-mail
            print(f"E-mail enviado para {', '.join(destinatarios)}.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# ---------------------Informações para envio de E-mail------------------------------------
# Defina seu e-mail e a senha de aplicativo de 16 caracteres
remetente_email = "rdgdosanjos@gmail.com"  # Substitua com seu e-mail
senha_email = os.getenv('GMAIL_PASSWORD')  # Obtendo a senha do Gmail dos GitHub Secrets

# Lista de destinatários de e-mail
destinatarios_email = [
    "rdgdosanjos@gmail.com",  # Substitua pelos e-mails para os quais deseja enviar
    "sthefanny_chris@icloud.com"
]

# Enviar o e-mail com a lista de aniversariantes
enviar_email(remetente_email, senha_email, destinatarios_email, mensagem)
