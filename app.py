#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename

# No es necesario instalar, es parte del sistema standard de Python
import os
import time
#--------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS instructores (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            nomyap VARCHAR(255) NOT NULL,
            actividad VARCHAR(255) NOT NULL,
            tarifa DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255),
            localidad VARCHAR(255))''')
        self.conn.commit()
        
        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_instructores(self):
        self.cursor.execute("SELECT * FROM instructores")
        instructores = self.cursor.fetchall()
        return instructores
    
    def consultar_instructores(self, codigo):
        # Consultamos un instructor a partir de su código
        self.cursor.execute(f"SELECT * FROM instructores WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def mostrar_instructores(self, codigo):
        # Mostramos los datos de un instructor a partir de su código
        instructores = self.consultar_instructores(codigo)
        if instructores:
            print("-" * 40)
            print(f"codigo.....: {instructores['codigo']}")
            print(f"nomyap.....: {instructores['nomyap']}")
            print(f"actividad..: {instructores['actividad']}")
            print(f"tarifa.....: {instructores['tarifa']}")
            print(f"imagen.....: {instructores['imagen_url']}")
            print(f"localidad..: {instructores['localidad']}")
            print("-" * 40)
        else:
            print("Instructor no encontrado.")

    # Agregar un instructor (create)
    def agregar_instructores(self, nomyap, actividad, tarifa, imagen, localidad):
        
        sql = "INSERT INTO instructores (nomyap, actividad, tarifa, imagen_url, localidad) VALUES (%s, %s, %s, %s, %s)"
        valores = (nomyap, actividad, tarifa, imagen, localidad)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid

    def modificar_instructores(self, codigo, nuevo_nomyap, nueva_actividad, nueva_tarifa, nueva_imagen, nueva_localidad):
        sql = "UPDATE instructores SET nomyap = %s, actividad = %s, tarifa = %s, imagen_url = %s, localidad = %s WHERE codigo = %s"
        valores = (nuevo_nomyap, nueva_actividad, nueva_tarifa, nueva_imagen, nueva_localidad, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_instructores(self, codigo):
        # Eliminamos un instructor de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM instructores WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='maralep1974.mysql.pythonanywhere-services.com', user='maralep1974', password='210510Popochis',
database='maralep1974$miapp')
# Carpeta para guardar las imagenes
ruta_destino = '/ inicio / maralep1974 / mi sitio / estático /imágenes'

@app.route("/instructores", methods=["GET"])
def listar_instructores():
    instructores = catalogo.listar_instructores()
    return jsonify(instructores)

@app.route("/instructores/<int:codigo>", methods=["GET"])
def mostrar_instructores(codigo):
    instructores = catalogo.consultar_instructores(codigo)
    if instructores:
        return jsonify(instructores), 200
    else:
        return "Instructor no encontrado", 404

@app.route("/instructores", methods=["POST"])
def agregar_instructores():
    #Recojo los datos del form
    nomyap = request.form['nomyap']
    actividad = request.form['actividad']
    tarifa = request.form['tarifa']
    imagen = request.files['imagen']
    localidad = request.form['localidad']  
    nombre_imagen = ""
    
    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

    nuevo_codigo = catalogo.agregar_instructores(nomyap, actividad, tarifa, nombre_imagen, localidad)
    if nuevo_codigo:    
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Instructor agregado correctamente.", "codigo": nuevo_codigo, "imagen_url": nombre_imagen}), 200
    else:
        return jsonify({"mensaje": "Error al agregar el instructor."}), 500

@app.route("/instructores/<int:codigo>", methods=["PUT"])
def modificar_instructores(codigo):
    #Se recuperan los nuevos datos del formulario
    nuevo_nomyap = request.form.get("nomyap")
    nueva_actividad = request.form.get("actividad")
    nueva_tarifa = request.form.get("tarifa")
    nueva_localidad = request.form.get("localidad")
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        
        # Busco el instructor guardado
        instructores = catalogo.consultar_instructores(codigo)
        if instructores: # Si existe el instructor...
            imagen_vieja = instructores["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:     
        instructores = catalogo.consultar_instructores(codigo)
        if instructores:
            nombre_imagen = instructores["imagen_url"]

   # Se llama al método modificar_instructores pasando el codigo del instructor y los nuevos datos.
    if catalogo.modificar_instructores (codigo, nuevo_nomyap, nueva_actividad, nueva_tarifa, nombre_imagen, nueva_localidad):
        return jsonify({"mensaje": "Instructor modificado"}), 200
    else:
        return jsonify({"mensaje": "Instructor no encontrado"}), 403

@app.route("/instructores/<int:codigo>", methods=["DELETE"])
def eliminar_instructores (codigo):
    # Primero, obtiene la información del instructor para encontrar la imagen
    instructores = catalogo.consultar_instructores (codigo)
    if instructores:
        # Eliminar la imagen asociada si existe
        ruta_imagen = os.path.join(ruta_destino, instructores['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el instructor del catálogo
        if catalogo.eliminar_instructores (codigo):
            return jsonify({"mensaje": "Instructor eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el instructor"}), 500
    else:
        return jsonify({"mensaje": "Instructor no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)