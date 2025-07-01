from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from Routes  import registrar_rutas
from flask_cors import CORS
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

mysql = MySQL(app)

app.mysql = mysql

registrar_rutas(app)
if __name__== "__main__": # Este bloque asegura que el código dentro de él solo se ejecute cuando el script se ejecuta directamente (no cuando se importa como un módulo).
    #Inicia el servidor de desarrollo de Flask .
    app.run(debug=True,host="0.0.0.0")
