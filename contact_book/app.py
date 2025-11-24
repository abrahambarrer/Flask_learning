import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_mensajes_flash'  # Necesario para 'flash'
DB_NAME = 'contactos.db'

# Validacion de datos

def validar_datos(datos):
    """
    Valida los datos contra las reglas estrictas del negocio.
    Retorna: (booleano, mensaje_error)
    """
    # 1. Validar Nombre: Letras, espacios, acentos. 1-80 chars.
    nombre = datos.get('nombre', '').strip()
    if not (1 <= len(nombre) <= 80):
        return False, "El nombre debe tener entre 1 y 80 caracteres."
    # Regex anclada (^...$)
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
        return False, "El nombre solo puede contener letras y espacios."

    # 2. Validar Correo: Formato estándar, <= 120 chars.
    correo = datos.get('correo', '').strip()
    if len(correo) > 120:
        return False, "El correo excede los 120 caracteres."
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo):
        return False, "Formato de correo inválido."

    # 3. Validar Teléfono: Dígitos, espacios, +. 7-15 dígitos efectivos.
    telefono = datos.get('telefono', '').strip()
    if not telefono:
        return False, "El teléfono es obligatorio."
    if not re.match(r'^[0-9\s+]+$', telefono):
        return False, "El teléfono tiene caracteres inválidos."
    # Contar dígitos efectivos
    digitos = re.sub(r'\D', '', telefono)
    if not (7 <= len(digitos) <= 15):
        return False, f"El teléfono debe tener entre 7 y 15 dígitos (tiene {len(digitos)})."

    # 4. Validar Etiqueta: Lista blanca estricta.
    etiqueta = datos.get('etiqueta', '')
    whitelist_etiquetas = ['familia', 'trabajo', 'amigos', 'otro', '']
    if etiqueta not in whitelist_etiquetas:
        return False, "Etiqueta no válida."

    # 5. Validar Notas: Texto plano, <= 500 chars, sin HTML (< o >).
    notas = datos.get('notas', '').strip()
    if len(notas) > 500:
        return False, "Las notas no pueden exceder 500 caracteres."
    if re.search(r'[<>]', notas):
        return False, "Las notas no pueden contener caracteres HTML (< >)."

    return True, None

# Conexion a SQLite

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Routes

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        # Consulta segura: solo lectura
        contactos = conn.execute('SELECT * FROM agenda').fetchall()
        conn.close()
        return render_template('index.html', contactos=contactos)
    except sqlite3.Error as e:
        app.logger.error(f"Error DB: {e}") 
        abort(500)

@app.route('/crear', methods=('GET', 'POST'))
def crear():
    if request.method == 'POST':
        datos = {
            'nombre': request.form['nombre'],
            'correo': request.form['correo'],
            'telefono': request.form['telefono'],
            'etiqueta': request.form.get('etiqueta'), # .get evita KeyError si falta
            'notas': request.form['notas']
        }
        
        es_valido, error = validar_datos(datos)
        
        if not es_valido:
            flash(error, 'error') # Mensaje breve al usuario
            return render_template('formulario.html', contacto=datos, accion="Crear")

        try:
            conn = get_db_connection()
            # CONSULTA PARAMETRIZADA (Evita Inyección SQL)
            conn.execute(
                'INSERT INTO agenda (nombre, correo, telefono, etiqueta, notas) VALUES (?, ?, ?, ?, ?)',
                (datos['nombre'].strip(), datos['correo'].strip(), datos['telefono'].strip(), 
                 datos['etiqueta'], datos['notas'].strip())
            )
            conn.commit()
            conn.close()
            flash('Contacto creado exitosamente.', 'exito')
            return redirect(url_for('index'))
        except sqlite3.Error as e:
            app.logger.error(f"Error al insertar: {e}")
            abort(500)

    return render_template('formulario.html', contacto={}, accion="Crear")

@app.route('/editar/<int:id>', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    contacto_db = conn.execute('SELECT * FROM agenda WHERE id = ?', (id,)).fetchone()
    
    if contacto_db is None:
        conn.close()
        abort(404)

    if request.method == 'POST':
        datos = {
            'nombre': request.form['nombre'],
            'correo': request.form['correo'],
            'telefono': request.form['telefono'],
            'etiqueta': request.form.get('etiqueta'),
            'notas': request.form['notas']
        }

        es_valido, error = validar_datos(datos)

        if not es_valido:
            flash(error, 'error')
            # Renderizamos con los datos del formulario (no de la DB) para no perder lo escrito
            return render_template('formulario.html', contacto=datos, accion="Editar")

        try:
            # CONSULTA PARAMETRIZADA DE ACTUALIZACIÓN
            conn.execute("""
                UPDATE agenda 
                SET nombre = ?, correo = ?, telefono = ?, etiqueta = ?, notas = ?
                WHERE id = ?
            """, (datos['nombre'].strip(), datos['correo'].strip(), datos['telefono'].strip(), 
                  datos['etiqueta'], datos['notas'].strip(), id))
            conn.commit()
            conn.close()
            flash('Contacto actualizado.', 'exito')
            return redirect(url_for('index'))
        except sqlite3.Error as e:
            app.logger.error(f"Error al actualizar: {e}")
            abort(500)

    conn.close()
    # Convertimos sqlite3.Row a dict para manipularlo en template si es necesario
    return render_template('formulario.html', contacto=dict(contacto_db), accion="Editar")

@app.route('/eliminar/<int:id>', methods=('POST',))
def eliminar(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM agenda WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('Contacto eliminado.', 'exito')
        return redirect(url_for('index'))
    except sqlite3.Error as e:
        app.logger.error(f"Error al eliminar: {e}")
        abort(500)

# Error generico
@app.errorhandler(500)
def internal_error(error):
    return "<h1>Ocurrió un error interno. Por favor intente más tarde.</h1>", 500

if __name__ == '__main__':
    app.run(debug=True) 
    # Nota: debug=True muestra trazas en desarrollo. 
    # En producción se debe poner en False para cumplir el requisito de "sin trazas".