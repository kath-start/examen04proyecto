from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__, template_folder='templates')

# 🔐 USAR VARIABLE DE ENTORNO (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔗 CONEXIÓN
def conectar_db():
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL no está configurada.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print("❌ Error de conexión:", e)
        return None


# 🛠️ INICIALIZAR BASE DE DATOS
def init_db():
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id SERIAL PRIMARY KEY,
                dni VARCHAR(20) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                direccion TEXT,
                telefono VARCHAR(20)
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabla 'personas' creada o ya existe.")
    else:
        print("❌ No se pudo conectar a la base de datos para inicializar.")


@app.before_first_request
def ensure_db():
    init_db()


# ➕ INSERTAR
def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO personas (dni, nombre, apellido, direccion, telefono)
                VALUES (%s, %s, %s, %s, %s)
            """, (dni, nombre, apellido, direccion, telefono))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error al insertar persona:", e)
            conn.close()
            return False
    print("❌ No hay conexión para guardar persona.")
    return False


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

    success = crear_persona(dni, nombre, apellido, direccion, telefono)
    if not success:
        print("❌ No se pudo guardar el registro. Revisa DATABASE_URL y los logs.")
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
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)