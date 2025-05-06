from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message
from mimetypes import guess_type

app = Flask(__name__)

# CONFIGURAÇÃO DE EMAIL
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teste.copias@redesc-edu.org.br'
app.config['MAIL_PASSWORD'] = '1234@csc'
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# CONFIGURAÇÃO DE UPLOAD
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1 GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        arquivos = request.files.getlist('arquivo')
        if not arquivos or not any(allowed_file(a.filename) for a in arquivos):
            return 'Nenhum arquivo válido enviado.'

        filenames = []
        for arquivo in arquivos:
            if allowed_file(arquivo.filename):
                filename = secure_filename(arquivo.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                arquivo.save(caminho)
                filenames.append((filename, caminho))

        # Coleta dados do formulário
        tipo = request.form.get('tipo') or 'Não especificado'
        data_entrega_raw = request.form.get('data_entrega')
        try:
            data_entrega_formatada = datetime.strptime(data_entrega_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            data_entrega_formatada = data_entrega_raw

        dados = {
            'setor': request.form.get('setor'),
            'turma': request.form.get('turma'),
            'tipo': tipo,
            'copias': request.form.get('copias'),
            'tamanho': request.form.get('tamanho'),
            'papel': request.form.get('papel'),
            'frente_verso': 'Sim' if request.form.get('frente_verso') else 'Não',
            'encadernacao': 'Sim' if request.form.get('encadernacao') else 'Não',
            'plastificacao': 'Sim' if request.form.get('plastificacao') else 'Não',
            'nome': request.form.get('nome'),
            'email': request.form.get('email'),
            'data_entrega': data_entrega_formatada,
            'coloridas_paginas': request.form.get('coloridas_paginas') if tipo == 'Parcialmente colorida' else 'N/A'
        }

        # Corpo do e-mail
        corpo = f"""Olá {dados['nome']},

Seu pedido de impressão foi recebido com sucesso. Aqui estão os detalhes:

Setor: {dados['setor']}
Turma: {dados['turma']}
Tipo de Impressão: {dados['tipo']}
Páginas coloridas: {dados['coloridas_paginas']}
Quantidade de cópias: {dados['copias']}
Tamanho do papel: {dados['tamanho']}
Tipo de folha: {dados['papel']}
Frente e Verso: {dados['frente_verso']}
Encadernação: {dados['encadernacao']}
Plastificação: {dados['plastificacao']}
Data desejada para entrega: {dados['data_entrega']}


Arquivos enviados:"""

        for fname, _ in filenames:
            corpo += f"\n- {fname}"

        corpo += "\n\nVocê será notificado assim que estiver pronto."

        try:
            msg = Message(
                subject="Novo Pedido de Impressão",
                recipients=['roqueiago@outlook.com'],
                body=corpo
            )

            # Anexa os arquivos
            for fname, path in filenames:
                with open(path, 'rb') as f:
                    file_data = f.read()
                    mime_type, _ = guess_type(path)
                    main_type, sub_type = mime_type.split('/', 1) if mime_type else ('application', 'octet-stream')
                    msg.attach(fname, f"{main_type}/{sub_type}", file_data)

            mail.send(msg)
            print("E-mail enviado com sucesso com anexo!")

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

        return render_template('sucesso.html', nome=dados['nome'])

    return render_template('form.html')
# RODANDO O APP
if __name__ == '__main__':
    print("Servidor Flask iniciado em http://127.0.0.1:5000")
    app.run(debug=True)
