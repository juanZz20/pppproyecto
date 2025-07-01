from flask import Blueprint, request, jsonify , current_app
from werkzeug.security import check_password_hash
import jwt
import datetime
from datetime import timezone, timedelta

login_bp = Blueprint("login",__name__)

JWT_SECRET_KEY = "papas_fritas_123"
JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 60

@login_bp.route("/",methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json()
        campos_requeridos=["email","contrasenia"]
        campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
        if campos_faltantes:
            return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})

        email = data["email"]
        contrasenia = data["contrasenia"]
        con = current_app.mysql.connection.cursor()
        try:
            con.execute("""SELECT * FROM T_USUARIO
                        WHERE USU_EMAIL = %s """, (email,))

            usuario = con.fetchone()
            #print(usuario)
            if not usuario:
                return jsonify({"mensaje":"Algo esta incorrecto"}), 401

            #print(type(contrasenia))
            user_id         = usuario[0]
            stored_email    = usuario[4]
            user_role       = usuario[6]
            hashed_password = usuario[8]

            verificar_contrasenia = check_password_hash(hashed_password, contrasenia)
            if verificar_contrasenia == False:
                return jsonify({"mensaje":"Usuario/password incorrecta"}), 401
            payload = {
                'user_id': user_id,
                'rol': user_role,
                'sub': stored_email,
                'exp': datetime.datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRES_MINUTES),
                'iat': datetime.datetime.now(timezone.utc) # Momento en que fue emitido el token
            }

            #u = {"USU_ID": usuario[0], "USU_NOMBRE": usuario[1], "USU_APELLIDO" : usuario[2]}
            #return jsonify(u)

            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
            return jsonify({"mensaje": "Login exitoso", "access_token": token}), 200
        except Exception as e:
        # En caso de cualquier otro error (ej. problema de base de datos)
            con.connection.rollback()
            print(f"Error en el login: {e}") # Para depuración en el servidor
            return jsonify({"mensaje": f"Error interno del servidor: {str(e)}"}), 500
        finally:
            if con:
                con.close() # Asegura que el cursor se cierre
    else:
        return jsonify({"mensaje": "Se esperaba un cuerpo de solicitud JSON"}), 400