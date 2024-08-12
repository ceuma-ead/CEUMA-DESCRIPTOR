# main.py
import sys
sys.path.append(".")
from app import criar_aplicacao

# Criando uma instância da aplicação Flask
app = criar_aplicacao()

# Iniciando o servidor
if __name__ == "__main__":
    app.run(host='127.0.0.1',port='8080',debug=True)