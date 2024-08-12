from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import sqlite3
import whisper

rotas_api = Blueprint('rotas_api', __name__, template_folder="./Templates")

UPLOAD_FOLDER = './sounds'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

# Conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criação da tabela se não existir
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcription TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcription TEXT
        );
    ''')
    conn.commit()
    conn.close()

create_table()


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@rotas_api.route('/upload_audio', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            
            conn = get_db_connection()
            conn.execute('INSERT INTO audios (filename) VALUES (?)', (unique_filename,))
            conn.commit()
            conn.close()
            
            flash('Upload feito com sucesso')
            return redirect(url_for('rotas_api.upload'))
    return render_template('Home/index.html')

@rotas_api.route('/list_audio', methods=['GET'])
def list_audio():
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM audios').fetchall()
    conn.close()
    return jsonify([dict(file) for file in files])

@rotas_api.route('/sounds/<filename>', methods=['GET'])
def sounds(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(directory=UPLOAD_FOLDER, path=filename)
    else:
        return jsonify({"error": "Arquivo não encontrado"}), 404


@rotas_api.route('/delete_audio/<filename>', methods=['POST'])
def delete_audio(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
        conn = get_db_connection()
        conn.execute('DELETE FROM audios WHERE filename = ?', (filename,))
        conn.commit()
        conn.close()
        
        flash('Arquivo excluído com sucesso')
    else:
        flash('Arquivo não encontrado')
    return redirect(url_for('rotas_api.upload'))

@rotas_api.route('/transcribe_audio/<filename>', methods=['POST'])
def transcribe_audio(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Arquivo não encontrado"}), 404

    model = whisper.load_model("base")
    result = model.transcribe(file_path,fp16=False)
    transcription_text = result["text"]

    conn = get_db_connection()
    conn.execute('UPDATE audios SET transcription = ? WHERE filename = ?', (transcription_text, filename))
    conn.commit()
    conn.close()

    return jsonify({"filename": filename, "transcription": transcription_text})


