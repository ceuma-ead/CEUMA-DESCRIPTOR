import sys
import os
from flask import Flask
sys.path.append(".")
from router.router import rotas_app
from api.router import rotas_api



def criar_aplicacao():
    app = Flask(__name__)

    app.secret_key = '123'

    # Configurar diretório estático
    # app.static_folder = 'Assets'
    app.static_folder = 'assets'
    app.static_url_path = '/static'

    # Registrar blueprints
    app.register_blueprint(rotas_app)
    app.register_blueprint(rotas_api, url_prefix='/api')


    return app

# if __name__ == "__main__":
#     app = criar_aplicacao()
#     app.run(debug=True)