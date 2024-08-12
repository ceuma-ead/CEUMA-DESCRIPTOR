import sys
sys.path.append(".")
from flask import Blueprint, render_template, request, redirect, url_for, session

# Criar um Registro para subir apenas rotas Apps.
rotas_app = Blueprint('main', __name__, template_folder="./Templates")

@rotas_app.route('/painel')
def audio():
    return render_template('Audios/index.html')

@rotas_app.route('/audio')
def gravar():
    return render_template('Gravar/index.html')

@rotas_app.route('/')
def home():
    return render_template('Home/index.html')
