import sqlite3

# 1. Definir el nombre del archivo de la base de datos
DB_NAME = 'contactos.db'

def crear_base_de_datos():
    """
    Crea la conexión a la base de datos y define la tabla 'agenda'
    si no existe.
    """
    try:
        # 2. Conectar a la base de datos (la crea si no existe)
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        print(f"Conexión a la base de datos '{DB_NAME}' establecida con éxito.")

        # 3. Definir el esquema SQL para la tabla 'agenda'
        # - PRIMARY KEY AUTOINCREMENT: Se usa una columna 'id' como clave primaria
        #   y se incrementa automáticamente para identificar de forma única cada registro.
        # - NOT NULL: Asegura que los campos obligatorios no queden vacíos.
        # - TEXT: Tipo de dato para todas las columnas de texto.
        # - CHECK: Limita los valores posibles para 'etiqueta'.
        
        sql_creacion_tabla = """
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            etiqueta TEXT CHECK(etiqueta IN ('Familia', 'Trabajo', 'Amigos', 'Otro')),
            notas TEXT
        );
        """
        
        # 4. Ejecutar el comando de creación de la tabla
        cursor.execute(sql_creacion_tabla)
        
        # 5. Confirmar los cambios
        conexion.commit()
        print("Tabla 'agenda' creada o ya existente.")

    except sqlite3.Error as e:
        print(f"Ocurrió un error de SQLite: {e}")
        
    finally:
        # 6. Cerrar la conexión
        if conexion:
            conexion.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    crear_base_de_datos()