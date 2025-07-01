from flask import Blueprint, request, jsonify , current_app, send_from_directory, render_template_string
import uuid
from werkzeug.security import generate_password_hash

usuarios_bp =Blueprint('/usuarios',__name__)

def UUIDD(): # Definimos una función UUIDD que nos servirá para usar el uuid con más facilidad
    return str(uuid.uuid4())


@usuarios_bp.route('/',methods=["POST"])
def regUsuario():
    if request.is_json:
            data = request.get_json() 
            
            campos_requeridos=["nombre","apellido","sexo","email","direccion","identificacion","contrasenia"]
            campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
            if campos_faltantes:
                return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
            
            nombre  = data.get("nombre")
            apellido  = data.get("apellido")
            sexo  = data.get("sexo")
            email  = data.get("email")
            direccion  = data.get("direccion")
            identificacion  = data.get("identificacion")
            rol="empleado"
            contrasenia     = data.get("contrasenia")
            con             = current_app.mysql.connection.cursor()
            try:     
                con.execute("INSERT INTO T_USUARIO (USU_NOMBRE,USU_APELLIDO,USU_SEXO,USU_EMAIL,USU_DIRECCION,USU_IDENTIFICACION,USU_ROL,USU_CONTRASENIA,UUID) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)",[nombre,apellido,sexo,email,direccion,identificacion,rol,generate_password_hash(contrasenia),UUIDD()])
                current_app.mysql.connection.commit()
                return jsonify({"mensaje":"Usuario  registrado"})
            except Exception as e:
                    current_app.mysql.connection.rollback()
                    return jsonify({"mensaje": f"Error al registrar Usuario: {str(e)}"}), 500
    else:    
        return jsonify({"mensaje": "Se esperaba un cuerpo de solicitud JSON"}), 400

@usuarios_bp.route('/',methods=["GET"])
def listado_usuario():
    # return jsonify({"mensaje":"hola"})
    cursor = current_app.mysql.connection.cursor()
    listado = []
    try:
        cursor.execute("SELECT USU_ID, USU_NOMBRE, USU_APELLIDO, USU_SEXO, USU_EMAIL, USU_DIRECCION, USU_IDENTIFICACION, USU_ROL,UUID FROM T_USUARIO")
        usuarios = cursor.fetchall()
        cursor.close()
        for u in usuarios:
            listado.append({"USU_ID":u[0], "USU_NOMBRE":u[1],"USU_APELLIDO":u[2],"USU_SEXO":u[3],"USU_EMAIL":u[4],"USU_DIRECCION":u[5],"USU_IDENTIFICACION":u[6],"USU_ROL":u[7],"UUID":u[8]})
        #gracias =D
        return jsonify(listado)
    except Exception as e:
         return jsonify({"error": f"Hubo un error al listar los usuarios en el servidor{e}"}),500
    #asegura que el cursor se cierre

@usuarios_bp.route("/<id>",methods=["DELETE"])
def eliUsuario(id):
    con     = current_app.mysql.connection.cursor()
    try:
        con.execute("DELETE FROM T_USUARIO WHERE UUID  = %s",[id])    
        if con.rowcount > 0: # Verifica si la operación de eliminación afectó alguna fila. Si rowcount es mayor que 0, significa que un catalogo fue eliminado.
          current_app.mysql.connection.commit()
          return jsonify({"mensaje":"Usuario eliminado"}), 200
        else :
            return  jsonify({"mensaje": "Usuario no encontrado"}), 404 # Si rowcount es 0, significa que el catalogo con ese ID no fue encontrado.
    except Exception as e:
            if con and current_app.mysql.connection:
                current_app.mysql.connection.rollback() # Hacer rollback en caso de error
                print(f"Error al intentar eliminar usuario: {e}")
    finally:
        if con:
            con.close()#ase

@usuarios_bp.route("/<id>",methods=["PUT"])
def actUsuaurio(id):
    data = request.get_json() 
    
    if not request.is_json:#verifica que la solicitud este en json
        return jsonify({"mensaje": "Se esperaba un cuerpo de solicitud JSON"}), 400
    
    campos_requeridos=["nombre","apellido","sexo","email","direccion","identificacion","rol","contrasenia"]
    campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
    if campos_faltantes:
        return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
        
    try :
        nombre          = data.get("nombre")
        apellido        = data.get("apellido")
        sexo            = data.get("sexo")
        email           = data.get("email")
        direccion       = data.get("direccion")
        identificacion  = data.get("identificacion")
        rol             = data.get("rol")
        contrasenia     = data.get("contrasenia")
        con             = current_app.mysql.connection.cursor()
        con.execute("""UPDATE T_USUARIO  SET USU_NOMBRE=  %s, USU_APELLIDO=  %s, USU_SEXO=  %s, USU_EMAIL=  %s, USU_DIRECCION=  %s, USU_IDENTIFICACION  =  %s,USU_ROL = %s,USU_CONTRASENIA  = %s WHERE UUID =  %s  """,[nombre,apellido,sexo,email,direccion,identificacion,rol,contrasenia,id])
        if con.rowcount > 0:
            current_app.mysql.connection.commit()
            return jsonify({"mensaje":"Usuario actualizado correctamente"}), 200
        else:
            current_app.mysql.connection.rollback() # No se encontró el usuario, no hay nada que actualizar. Rollback es opcional aquí pero seguro.
            return jsonify({"mensaje": "Usuario no encontrado para actualizar"}), 404
    except Exception as e:
         if con and current_app.mysql.connection:
            current_app.mysql.connection.rollback()
            print(f"Error al intentar actualizar usuario: {e}")
            return jsonify({"mensaje": f"Error interno del servidor al actualizar usuario: {str(e)}"}), 500
    finally:
        if con:
            con.close()#asegura que el cursor se cierre
    
@usuarios_bp.route('/swagger.json')
def swagger_json():
    return send_from_directory('.', 'swagger.json')

@usuarios_bp.route("/docs")
def swagger_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>API APRENDIZ</title>
      <link href="/static/swagger-ui/swagger-ui.css" rel="stylesheet" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
      <script>
        const ui = SwaggerUIBundle({
          url: "./swagger.json",
          dom_id: '#swagger-ui',
        });
      </script>
    </body>
    </html>
    """)


