from flask import Flask, render_template, request # type: ignore
import os
from werkzeug.utils import secure_filename # type: ignore

app = Flask(__name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1 GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Verifica se o arquivo tem extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        
        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "Obrigado por sua solicitação! Sua requisição foi recebida com sucesso e entrou na fila de impressão.Você será notificado por e-mail assim que o material estiver pronto para retirada ou uso."
        else:
            return 'Tipo de arquivo não permitido.'

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)