# db_manager.py
import sqlite3

def get_connection():
    db_path = "database.db"
    conn = sqlite3.connect(db_path)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla productos
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        imagen TEXT,  -- Ruta de la imagen (opcional)
        precio_usd REAL NOT NULL,
        precio_bs REAL,  -- Precio en bolívares, calculado según tasa de cambio
        inventario INTEGER NOT NULL,
        tasa_cambio REAL NOT NULL,  -- La tasa de cambio utilizada para convertir el precio en USD a BS
        fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Crear tabla tasa_cambio
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS tasa_cambio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tasa REAL NOT NULL,
        fecha DATE NOT NULL DEFAULT CURRENT_DATE
    )
    ''')

    conn.commit()
    conn.close()

create_tables()
