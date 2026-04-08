from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__, template_folder='templates')

# 🔐 USAR VARIABLE DE ENTORNO (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔗 CONEXIÓN
def conectar_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print("❌ Error de conexión:", e)
        return None


# ➕ INSERTAR
def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO personas (dni, nombre, apellido, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (dni, nombre, apellido, direccion, telefono))
        conn.commit()
        cursor.close()
        conn.close()


# 📋 LISTAR
def obtener_registros():
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas ORDER BY apellido")
        registros = cursor.fetchall()
        cursor.close()
        conn.close()
        return registros
    return []


# 🏠 HOME
@app.route('/')
def index():
    return render_template('index.html')


# 📝 REGISTRAR
@app.route('/registrar', methods=['POST'])
def registrar():
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    direccion = request.form['direccion']
    telefono = request.form['telefono']

    crear_persona(dni, nombre, apellido, direccion, telefono)
    return redirect(url_for('index'))


# 📊 ADMINISTRAR
@app.route('/administrar')
def administrar():
    registros = obtener_registros()
    return render_template('administrar.html', registros=registros)


# ❌ ELIMINAR
@app.route('/eliminar/<int:id>')
def eliminar_registro(id):
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('administrar'))


# 🚀 RUN
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)