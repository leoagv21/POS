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
        fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        precio_venta_sin_iva REAL,
        iva REAL,
        precio_venta_con_iva REAL,
        precio_venta_con_iva_bs REAL,
        precio_bs_und REAL
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

    # Crear tabla ventas
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_cliente TEXT NOT NULL,
        cedula_rif TEXT NOT NULL,
        total_bs REAL NOT NULL,
        total_divisas REAL NOT NULL,
        iva_total REAL NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Crear tabla detalle_ventas
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario_bs REAL NOT NULL,
        precio_unitario_divisas REAL NOT NULL,
        subtotal_bs REAL NOT NULL,
        subtotal_divisas REAL NOT NULL,
        FOREIGN KEY (id_venta) REFERENCES ventas(id),
        FOREIGN KEY (id_producto) REFERENCES productos(id)
    )
    ''')

    conn.commit()
    conn.close()

create_tables()