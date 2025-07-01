from flask import Blueprint, request, jsonify , current_app
import uuid

catalogo_bp =Blueprint('/catalogo',__name__)

def UUIDD(): # Definimos una función UUIDD que nos servirá para usar el uuid con más facilidad
    return str(uuid.uuid4())

@catalogo_bp.route("/",methods=["POST"])
def regCatalogo(): #Verifica si el tipo de contenido de la solicitud es JSON.
   
    if request.is_json:
        data = request.get_json() 
        
        campos_requeridos=["colores","hebilla","materialCinturon","idR"]
        campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
        
        if campos_faltantes:
            return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
            
        colores             = data.get("colores")
        hebilla             = data.get("hebilla")
        materialCinturon    = data.get("materialCinturon")
#        talla               = data.get("talla")
        idR                 = data.get("idR")
        


        con = current_app.mysql.connection.cursor() # Crea un objeto cursor, que permite ejecutar comandos SQL en la base de datos.
        try: #
        
            con.execute("""
            INSERT INTO T_CATALOGO (CAT_COLORES, CAT_TIPOHEBILLA,CAT_MATERIALCINTURON,CAT_ID_REP,UUID )
            VALUES (%s, %s, %s,  %s,%s)
            """, [ colores,hebilla, materialCinturon,idR,UUIDD()])
        
            current_app.mysql.connection.commit() #  Confirma los cambios en la base de datos, haciendo que la inserción sea permanente.
            return jsonify({"mensaje": "Catálogo registrado"}), 201
          
        except Exception as e: # Si cualquier tipo de error ocurre en el código de arriba (en el try), 
                #captura ese error y guárdalo en la variable e para que podamos hacer algo con él.

                current_app.mysql.connection.rollback() # Si ocurrió un error, deshaz todos los cambios  
                                            # que se intentaron hacer en la base de datos desde la última vez que se hizo un commit o rollback
                return jsonify({"mensaje": f"Error al registrar catálogo: {str(e)}"}), 404
        finally:
                con.close()
    else: # Si el nombre no está presente o el cuerpo no es JSON, se devuelven respuestas con códigos 400
            return jsonify({"mensaje": "El parámetro [colores] no está definido"}), 400
    

@catalogo_bp.route("/",methods=["GET"])
def listado_catalogo():
    cursor = current_app.mysql.connection.cursor() # Cursor que retorna diccionarios
    listado = []
    try: #este try nos ayuda a que si algo sale mal se ejecute otra linea de codigo 

        # Ejecuta una consulta SELECT para obtener todos los catalogos.
        cursor.execute("SELECT CAT_ID, CAT_COLORES, CAT_TIPOHEBILLA, CAT_MATERIALCINTURON , CAT_ID_REP, UUID FROM T_CATALOGO")
        catalogo = cursor.fetchall() # Obtiene todas las filas resultantes de la consulta.
        for u in catalogo:
            listado.append({"CAT_ID":u[0], "CAT_COLORES":u[1], "CAT_TIPOHEBILLA" :u[2],"CAT_MATERIALCINTURON":u[3],"CAT_ID_REP":u[4]})
        return jsonify(listado), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al listar catálogo: {str(e)}"}), 500
    finally:
        cursor.close()


@catalogo_bp.route("/<id>",methods=["DELETE"])
def eliCatalogo(id):
    con = current_app.mysql.connection.cursor()
    try:
        #Ejecuta una consulta DELETE para eliminar un catalogo  por su USU_ID.
        con.execute("DELETE FROM T_CATALOGO WHERE UUID = %s", [id])
        if con.rowcount > 0: # Verifica si la operación de eliminación afectó alguna fila. Si rowcount es mayor que 0, significa que un catalogo fue eliminado.
            current_app.mysql.connection.commit()
            return jsonify({"mensaje": "Catálogo eliminado"}), 200
        else:
            return jsonify({"mensaje": "Catálogo no encontrado"}), 404 # Si rowcount es 0, significa que el catalogo con ese ID no fue encontrado.
    except Exception as e:
        current_app.mysql.connection.rollback()
        return jsonify({"mensaje": f"Error al eliminar catálogo: {str(e)}"}), 500
    finally:
        con.close()





@catalogo_bp.route("/<id>",methods=["PUT"])
def actCatalogo(id):
    if request.is_json:
        
        data = request.get_json()
        campos_requeridos=["colores","hebilla","materialCinturon","talla","idR"]
        campos_faltantes = [ x for x in campos_requeridos if x not in data  ]
        
        if campos_faltantes:
            return jsonify({"mensaje":f"Los siguientes parametros son obliga....{campos_faltantes}"})
    
        
        try :
            colores             = data.get("colores")
            hebilla             = data.get("hebilla")
            materialCinturon    = data.get("materialCinturon")
            talla               = data.get("talla")
            idR                 = data.get("idR")


            con             = current_app.mysql.connection.cursor()
            con.execute("""UPDATE T_CATALOGO  SET CAT_COLORES=  %s, CAT_TIPOHEBILLA=  %s, CAT_MATERIALCINTURON=  %s, TALLA=  %s, CAT_ID_REP= %s WHERE UUID  =  %s """,[colores,hebilla, materialCinturon,talla,idR,id])
            if con.rowcount > 0:
                current_app.mysql.connection.commit()
                return jsonify({"mensaje":"catalogo actualizado correctamente"}), 200
            else:
                current_app.mysql.connection.rollback() # No se encontró el catalogo, no hay nada que actualizar. Rollback es opcional aquí pero seguro.
                return jsonify({"mensaje": "catalogo no encontrado para actualizar"}), 404
        except Exception as e:
            if con and current_app.mysql.connection:
                current_app.mysql.connection.rollback()
                print(f"Error al intentar actualizar catalogo: {e}")
                return jsonify({"mensaje": f"Error interno del servidor al actualizar catalogo: {str(e)}"}), 500
        finally:
            if con:
                con.close()#asegura que el cursor se cierregura que el cursor se cierre