from flask import Flask, render_template, url_for, flash, request, redirect
import pymysql
import shortuuid

# endpoint
endpoint = 'https://short-url-flask-app.herokuapp.com'

# inicializamos app
app = Flask(__name__)
PORT = 5000
DEBUG = False

# Conexión MySql
def connection():
    s = 'XXXXXXXXXXX'
    d = 'XXXXXXXXXXX' 
    u = 'XXXXXXXXXXX'
    p = 'XXXXXXXXXXX'
    conn = pymysql.connect(host=s, user=u, password=p, database=d)
    return conn

# llave secrea para user mensajes flash
app.secret_key = "XXXXXXXXX"

# Ruta Inicial
@app.route('/', methods=['GET'])
def inicio():
    try:
        return render_template('index.html'), 200
    except:
        return render_template('404.html'), 404

# Ruta para Crear Enlace Corto y Almacenar en la Base de Datos
@app.route('/crear_enlace_corto', methods=['POST'])
def crear_enlace_corto():
    try:
        if request.method == 'POST':
            # Capturamos la url
            url = request.form['url']
            conn = connection()
            cursor = conn.cursor()

            # Ciclo para validar enlace corto que no se duplique
            while True:
                # Generamos el enlace corto
                enlace_corto = shortuuid.ShortUUID().random(length=7)
                # Consultamos a la Base de Datos si existe enlace corto
                cursor.execute(
                    "SELECT * FROM enlaces WHERE enlace_corto = BINARY %s", (enlace_corto,))

                if not cursor.fetchone():
                    break

            # Consultamos si en la base de datos existe URL
            cursor.execute(
                "SELECT enlace_corto FROM enlaces WHERE url = BINARY %s", (url,))
            data = cursor.fetchone()
            if data:
                flash(endpoint + '/'+data[0])
                return redirect(url_for('inicio')), 302

            # Ingresamos en la base de datos la url enviada
            cursor.execute(
                "INSERT INTO enlaces (url, enlace_corto) VALUES (%s,%s)", (url, enlace_corto))

            # Guardamos cambios en Base de Datos
            conn.commit()

            # Cerramos la conexión de la base de datos
            conn.close()
            nuevo_enlace = endpoint + '/'+enlace_corto
            flash(nuevo_enlace)
            return redirect(url_for('inicio')), 302
    except:
        return render_template('404.html'), 404

# Ruta para ir a URL de Base de Datos
@app.route('/<id>')
def obtener_url(id):
    try:
        conn = connection()
        cursor = conn.cursor()

        # Buscamos en la base de datos la dirección URL
        cursor.execute(
            "SELECT url FROM enlaces WHERE enlace_corto = BINARY %s", (id,))

        # Guardamos en variable el resultado
        data = cursor.fetchone()

        # Cerrar Conexión de la Base de Datos
        conn.close()
        return render_template('ads.html', url=data[0]), 200
    except:
        return render_template('404.html'), 404

# corremos app
if __name__ == "__main__":
    app.run(port=PORT, debug=True)
