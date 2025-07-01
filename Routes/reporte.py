from flask import Blueprint, request, jsonify , current_app
import uuid

reporte_bp =Blueprint('/reporte',__name__)

def UUIDD(): # Definimos una función UUIDD que nos servirá para usar el uuid con más facilidad
    return str(uuid.uuid4())


@reporte_bp.route("/",  methods=["POST"])
def regReporte():   
    if request.is_json:
        data = request.get_json() 
        
        campos_requeridos=["gananciaTotal","pago","materialUsado","cantidadVentas","idA"]
        campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
        
        if campos_faltantes:
            return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
            
        gananciaTotal            = data.get("gananciaTotal")
        pago                     = data.get("pago")
        materialUsado            = data.get("materialUsado")
        cantidadVentas           = data.get("cantidadVentas")
        idA                      = data.get("idA")


        con = current_app.mysql.connection.cursor() # Crea un objeto cursor, que permite ejecutar comandos SQL en la base de datos.
        try: #
        
            con.execute("""
            INSERT INTO T_REPORTE (REP_GANANCIAST, REP_PAGO ,REP_MATERIALUSADO,REP_CANTIDADVENTA,REP_ID_ADM,UUID )
            VALUES (%s, %s, %s, %s,%s,%s)
            """, [ gananciaTotal,pago, materialUsado,cantidadVentas,idA,UUIDD()])
        
            current_app.mysql.connection.commit() #  Confirma los cambios en la base de datos, haciendo que la inserción sea permanente.
            return jsonify({"mensaje": "Reporte registrado"}), 201
          
        except Exception as e: # Si cualquier tipo de error ocurre en el código de arriba (en el try), 
                #captura ese error y guárdalo en la variable e para que podamos hacer algo con él.

                current_app.mysql.connection.rollback() # Si ocurrió un error, deshaz todos los cambios  
                                            # que se intentaron hacer en la base de datos desde la última vez que se hizo un commit o rollback
                return jsonify({"mensaje": f"Error al registrar reporte: {str(e)}"}), 500
        finally:
                con.close()
    else: # Si el nombre no está presente o el cuerpo no es JSON, se devuelven respuestas con códigos 400
            return jsonify({"mensaje": "El parámetro [e] no está definido"}), 400
    
   
#
# LISTADO DE REPORTES
@reporte_bp.route("/", methods=['GET'])
def listado_reporte():
    cursor = current_app.mysql.connection.cursor()
    listado = []
    try:
        cursor.execute("SELECT* FROM T_REPORTE")
        reportes = cursor.fetchall()
        for u in reportes:
            listado.append({"REP_ID_ADM":u[5], "REP_GANANCIASTOTALES":u[1], "REP_PAGO":u[2],"REP_MATERIALUSADO":u[3],"REP_CANTIDADVENTA":u[4],"REP_ID":u[0],"UUID":u[6] })
        #gracias =D
        return jsonify(listado)
    except:
        return print("noseque poner pero salio mal"),500
    finally:
        cursor.close()
#SARAY :
# ELIMINACIÓN DE REPORTES 
 #Va a eliminar un reporte por su id 
@reporte_bp.route("/<id>", methods=["DELETE"])
def eliReporte(id):
    con     = current_app.mysql.connection.cursor()
    try :  #Ejecuta una consulta DELETE para eliminar un reporte  por su REP_ID.
        con.execute("DELETE FROM T_REPORTE WHERE UUID  = %s",[id])
        if con.rowcount > 0: # Verifica si la operación de eliminación afectó alguna fila. Si rowcount es mayor que 0, significa que un catalogo fue eliminado.
          current_app.mysql.connection.commit()
          return jsonify({"mensaje":"Reporte eliminado"}), 200
        else :
            return  jsonify({"mensaje": "Reporte no encontrado"}), 404 # Si rowcount es 0, significa que el catalogo con ese ID no fue encontrado.
    except Exception as e:
        current_app.mysql.connection.rollback()
        return jsonify({"mensaje": f"Error al eliminar reporte: {str(e)}"}), 500
    finally:
        con.close()
        
        
# EDICION DE REPORTES 
#Va a actualizar un reporte parcialmente 
@reporte_bp.route("/<id>", methods=["PUT"])
def actReporte(id):
     if request.is_json:
        
        data = request.get_json()
        campos_requeridos=["gananciaTotal","pago","materialUsado","cantidadVentas"]
        campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
        
        if campos_faltantes:
            return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
    
        
        try :
            gananciaTotal             = data.get("gananciaTotal")
            pago                     = data.get("pago")
            materialUsado            = data.get("materialUsado")
            cantidadVentas           = data.get("cantidadVentas")



            con             = current_app.mysql.connection.cursor()
            con.execute("""UPDATE T_REPORTE  SET REP_GANANCIAST=  %s,  REP_PAGO=  %s, REP_MATERIALUSADO=  %s, REP_CANTIDADVENTA=  %s WHERE UUID  =  %s """,[gananciaTotal,pago, materialUsado,cantidadVentas,id])
            if con.rowcount > 0:
                current_app.mysql.connection.commit()
                return jsonify({"mensaje":"reporte actualizado correctamente"}), 200
            else:
                current_app.mysql.connection.rollback() # No se encontró el reporte, no hay nada que actualizar. Rollback es opcional aquí pero seguro.
                return jsonify({"mensaje": "reporte no encontrado para actualizar"}), 404
        except Exception as e:
            if con and current_app.mysql.connection:
                current_app.mysql.connection.rollback()
                print(f"Error al intentar actualizar reporte: {e}")
                return jsonify({"mensaje": f"Error interno del servidor al actualizar reporte: {str(e)}"}), 500
        finally:
            if con:
                con.close()#asegura que el cursor se cierre