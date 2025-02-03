from itertools import product
import customtkinter as ctk
from tkinter import messagebox, ttk, Toplevel, Entry, Label, Button, PhotoImage
from db_manager import get_connection
from PIL import Image, ImageTk
import os
import sqlite3
from reportlab.lib.pagesizes import letter,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

def obtener_iva():
    """Obtiene el valor del IVA desde la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT iva FROM productos LIMIT 1")
    iva = cursor.fetchone()[0]
    conn.close()
    return iva

def obtener_tasa_cambio():
    """Obtiene la tasa de cambio más reciente."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT tasa FROM tasa_cambio ORDER BY id DESC LIMIT 1")
        tasa = cursor.fetchone()
        return tasa[0] if tasa else None
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la tasa de cambio: {e}")
        return None
    finally:
        conn.close()

def verificar_y_agregar_columna():
    """Verifica si la columna 'inventario' existe en la tabla 'productos' y la agrega si no existe."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si la columna 'inventario' existe
    cursor.execute("PRAGMA table_info(productos)")
    columnas = cursor.fetchall()
    columnas_nombres = [columna[1] for columna in columnas]

    if 'inventario' not in columnas_nombres:
        # Agregar la columna 'inventario' a la tabla 'productos'
        cursor.execute("ALTER TABLE productos ADD COLUMN inventario INTEGER DEFAULT 0")
        conn.commit()

    conn.close()


def obtener_numero_factura():
    """Obtiene el número de factura desde un archivo y lo incrementa."""
    numero_factura_path = os.path.join(os.path.dirname(__file__), 'numero_factura.txt')
    if os.path.exists(numero_factura_path):
        with open(numero_factura_path, 'r') as file:
            numero_factura = int(file.read().strip())
    else:
        numero_factura = 0

    numero_factura += 1

    with open(numero_factura_path, 'w') as file:
        file.write(str(numero_factura))

    return numero_factura
def generar_factura(nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total, productos):
    """Genera una factura en formato PDF y la abre automáticamente para imprimir."""
    # Calcular la altura necesaria
    numero_factura = obtener_numero_factura()
    base_height = 100  # Altura base para el membrete y la información del cliente
    product_height = 10 * len(productos)  # Altura para la lista de productos
    total_height = base_height + product_height + 100  # Altura adicional para totales y otros datos

    # Crear el canvas con una altura inicial
    factura_path = os.path.join(os.path.dirname(__file__), f"factura_{cedula_rif}.pdf")
    c = canvas.Canvas(factura_path, pagesize=(57 * mm, total_height * mm))
    width, height = 57 * mm, total_height * mm

    # Membrete y logo
    c.setFont("Courier-Bold", 8)
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, (width - 40) / 2, height - 40, width=40, height=40)

    # Centrar el texto y hacerlo más pequeño
    text = "RIF: J-12345678-9"
    text_width = c.stringWidth(text, "Courier-Bold", 8)
    c.drawString((width - text_width) / 2, height - 80, text)

    text = "Family Supermarket"
    text_width = c.stringWidth(text, "Courier-Bold", 8)
    c.drawString((width - text_width) / 2, height - 70, text)

    text = f"RIF/C.I.: {cedula_rif}"
    c.drawString(10, height - 120, text)

    text = f"Razon Social: {nombre_cliente}"
    c.drawString(10, height - 110, text)

    # Espacio debajo de "Razón Social"
    y_position = height - 130

    # Título "FACTURA" centrado
    text = "FACTURA"
    text_width = c.stringWidth(text, "Courier-Bold", 8)
    c.drawString((width - text_width) / 2, y_position, text)

    # Texto "Factura:" a la izquierda y número de factura a la derecha
    y_position -= 10
    text = "Factura:"
    c.drawString(10, y_position, text)

    text = f"{numero_factura:03d}"
    text_width = c.stringWidth(text, "Courier-Bold", 8)
    c.drawString(width - text_width - 10, y_position, text)

    # Fecha debajo del texto "Factura:"
    y_position -= 10
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    c.setFont("Courier", 6)
    c.drawString(10, y_position, f"Fecha: {fecha_actual}")

    # Espacio antes de "Detalle de la Factura"
    y_position -= 20

    # Detalle de la factura
    c.setFont("Courier-Bold", 6)
    text = "Detalle de la Factura:"
    text_width = c.stringWidth(text, "Courier-Bold", 6)
    c.drawString((width - text_width) / 2, y_position, text)

    # Lista de productos
    y_position -= 10  # Ajustar la posición para que esté justo debajo del texto "Detalle de la Factura"
    c.setFont("Courier", 8)
    for producto in productos:
        id_producto, nombre, inventario, precio_unitario_bs, subtotal_bs = producto
        precio_unitario_bs = float(precio_unitario_bs)  # Asegúrate de que sea un número flotante
        c.drawString(10, y_position, f"{nombre} x{inventario} - {precio_unitario_bs:.2f} Bs")
        y_position -= 10

    # Totales
    c.setFont("Courier-Bold", 8)

    # Subtotal
    text = "Subtotal:"
    c.drawString(10, y_position - 10, text)
    text_value = f"{total_bs - iva_total:.2f} Bs"
    text_width = c.stringWidth(text_value, "Courier-Bold", 8)
    c.drawString(width - text_width - 10, y_position - 10, text_value)

    # IVA Total
    text = "IVA Total (Bs):"
    c.drawString(10, y_position - 20, text)
    text_value = f"{iva_total:.2f} Bs"
    text_width = c.stringWidth(text_value, "Courier-Bold", 8)
    c.drawString(width - text_width - 10, y_position - 20, text_value)

    # Total
    text = "Total:"
    c.drawString(10, y_position - 30, text)
    text_value = f"{total_bs:.2f} Bs"
    text_width = c.stringWidth(text_value, "Courier-Bold", 8)
    c.drawString(width - text_width - 10, y_position - 30, text_value)

    # Ajustar la altura del documento para que se corte justo después del total
    total_height = height - y_position + 40  # Ajustar según sea necesario
    c.setPageSize((57 * mm, total_height * mm))

    c.save()
    messagebox.showinfo("Factura", f"Factura generada correctamente: {factura_path}")

    # Abrir automáticamente la factura para imprimir
    os.startfile(factura_path, "print")

def limpiar_formulario():
    """Limpia el formulario después de finalizar la venta."""
    entry_nombre_cliente.delete(0, 'end')
    entry_cedula_rif.delete(0, 'end')
    for item in tree_carrito.get_children():
        tree_carrito.delete(item)
    label_total_bs.configure(text="0.00 Bs")
    label_total_divisas.configure(text="0.00 USD")
    label_iva_total.configure(text="0.00 Bs")

def obtener_productos():
    """Obtiene la lista de productos del carrito."""
    productos = []
    for item in tree_carrito.get_children():
        producto = tree_carrito.item(item)["values"]
        id_producto, nombre, inventario, precio_unitario_bs, subtotal_bs = producto
        productos.append((id_producto, nombre, inventario, float(precio_unitario_bs), float(subtotal_bs)))
    return productos

def finalizar_venta():
    """Finaliza la venta y guarda los datos en la base de datos."""
    nombre_cliente = entry_nombre_cliente.get().strip()
    cedula_rif = entry_cedula_rif.get().strip()

    if not nombre_cliente or not cedula_rif:
        messagebox.showerror("Error", "Por favor, ingrese el nombre del cliente y la cédula o RIF.")
        return

    try:
        total_bs = float(label_total_bs.cget("text").replace(" Bs", ""))
        total_divisas = float(label_total_divisas.cget("text").replace(" USD", ""))
        iva_total = float(label_iva_total.cget("text").replace(" Bs", ""))
    except ValueError:
        messagebox.showerror("Error", "Error al convertir los totales. Asegúrese de que los campos no estén vacíos.")
        return

    productos = []
    for item in tree_carrito.get_children():
        producto = tree_carrito.item(item)["values"]
        id_producto, nombre, cantidad, precio_unitario_bs, subtotal_bs = producto
        productos.append((id_producto, nombre, cantidad, float(precio_unitario_bs), float(subtotal_bs)))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO ventas (nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total))
        id_venta = cursor.lastrowid

        for producto in productos:
            id_producto, nombre, cantidad, precio_unitario_bs, subtotal_bs = producto
            precio_unitario_divisas = float(precio_unitario_bs) / tasa
            subtotal_divisas = float(subtotal_bs) / tasa
            cursor.execute("""
                INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario_bs, precio_unitario_divisas, subtotal_bs, subtotal_divisas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_venta, id_producto, cantidad, precio_unitario_bs, precio_unitario_divisas, subtotal_bs, subtotal_divisas))

        conn.commit()
    except sqlite3.OperationalError as e:
        messagebox.showerror("Error", f"Error al finalizar la venta: {e}")
    finally:
        conn.close()

    messagebox.showinfo("Éxito", "Venta finalizada correctamente.")
    generar_factura(nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total, productos)
    limpiar_formulario()

def interfaz_pos():
    """Interfaz para el punto de venta."""

    global entry_nombre_cliente, entry_cedula_rif, tree_carrito, label_total_bs, label_total_divisas, label_iva_total, tasa, frame_productos

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Punto de Venta")
    root.state('zoomed')  # Maximizar la ventana al iniciar

    # Establecer el icono del programa
    icon_path = os.path.join(os.path.dirname(__file__), 'icono.png')
    icon_image = PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image)  # Asegúrate de que el archivo icono.png esté en el mismo directorio

    # Configurar el grid
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # Contenedor principal
    frame_main = ctk.CTkFrame(root)
    frame_main.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    frame_main.grid_rowconfigure(1, weight=1)
    frame_main.grid_columnconfigure(1, weight=1)

    # Título principal
    ctk.CTkLabel(frame_main, text="Punto de Venta", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

    # Frame para lista de productos
    frame_productos = ctk.CTkFrame(frame_main)
    frame_productos.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")
    frame_productos.grid_rowconfigure(0, weight=1)
    frame_productos.grid_columnconfigure(0, weight=1)

    # Frame para carrito de compras
    frame_carrito = ctk.CTkFrame(frame_main)
    frame_carrito.grid(row=1, column=2, columnspan=2, pady=5, sticky="nsew")
    frame_carrito.grid_rowconfigure(0, weight=1)
    frame_carrito.grid_columnconfigure(0, weight=1)

    # Tabla de carrito de compras
    columnas_carrito = ("ID", "Nombre", "Cantidad", "Precio Unitario (Bs)", "Subtotal (Bs)")
    tree_carrito = ttk.Treeview(frame_carrito, columns=columnas_carrito, show="headings", height=10)
    for col in columnas_carrito:
        tree_carrito.heading(col, text=col)
        tree_carrito.column(col, width=80, anchor="center")
    tree_carrito.grid(row=0, column=0, sticky="nsew")

    # Añadir scrollbar a la tabla de carrito de compras
    scrollbar_carrito = ttk.Scrollbar(frame_carrito, orient="vertical", command=tree_carrito.yview)
    tree_carrito.configure(yscroll=scrollbar_carrito.set)
    scrollbar_carrito.grid(row=0, column=1, sticky="ns")

    # Frame de entrada de datos del cliente
    frame_cliente = ctk.CTkFrame(frame_main)
    frame_cliente.grid(row=2, column=0, columnspan=4, pady=5, padx=10, sticky="ew")

    ctk.CTkLabel(frame_cliente, text="Nombre del Cliente:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_nombre_cliente = ctk.CTkEntry(frame_cliente, width=120)
    entry_nombre_cliente.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_cliente, text="Cédula o RIF:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_cedula_rif = ctk.CTkEntry(frame_cliente, width=120)
    entry_cedula_rif.grid(row=0, column=3, padx=5, pady=5)

    # Frame para mostrar totales
    frame_totales = ctk.CTkFrame(frame_main)
    frame_totales.grid(row=3, column=0, columnspan=4, pady=5, padx=10, sticky="ew")

    ctk.CTkLabel(frame_totales, text="Total (Bs):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    label_total_bs = ctk.CTkLabel(frame_totales, text="", font=("Arial", 10))
    label_total_bs.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_totales, text="Total (Divisas):", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    label_total_divisas = ctk.CTkLabel(frame_totales, text="", font=("Arial", 10))
    label_total_divisas.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_totales, text="IVA Total (Bs):", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    label_iva_total = ctk.CTkLabel(frame_totales, text="", font=("Arial", 10))
    label_iva_total.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Botón para finalizar la venta
    ctk.CTkButton(frame_main, text="Finalizar Venta", command=finalizar_venta, font=("Arial", 10)).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

    # Botón para generar factura
    ctk.CTkButton(frame_main, text="Generar Factura", command=lambda: finalizar_venta(), font=("Arial", 10)).grid(row=4, column=2, columnspan=2, pady=5, sticky="ew")

    # Obtener tasa de cambio actual
    tasa = obtener_tasa_cambio()

    # Cargar productos en la tabla de productos
    cargar_productos(frame_productos)

    root.mainloop()

def cargar_productos(frame):
    """Carga los productos en el frame como botones con imágenes."""
    verificar_y_agregar_columna()  # Verificar y agregar la columna 'inventario' si es necesario

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, imagen, precio_venta_con_iva, precio_venta_con_iva_bs, inventario FROM productos")
    productos = cursor.fetchall()
    conn.close()

    for producto in productos:
        id_producto, nombre, imagen_path, precio_usd, precio_bs, inventario = producto
        if imagen_path and os.path.exists(imagen_path):
            imagen = Image.open(imagen_path)
            imagen = imagen.resize((100, 100), Image.LANCZOS)  # Ajustar el tamaño de la imagen
            imagen_ctk = ctk.CTkImage(light_image=imagen, dark_image=imagen)
            button = ctk.CTkButton(frame, image=imagen_ctk, text=f"{nombre}\nStock: {inventario}", command=lambda p=producto: seleccionar_cantidad(p))
            button.image = imagen_ctk  # Guardar referencia para evitar que la imagen sea recolectada por el GC
        else:
            button = ctk.CTkButton(frame, text=f"{nombre}\nStock: {inventario}", command=lambda p=producto: seleccionar_cantidad(p))
        button.pack(side="left", padx=2, pady=2)

def refrescar_productos():
    """Refresca la lista de productos en el frame de productos."""
    for widget in frame_productos.winfo_children():
        widget.destroy()
    cargar_productos(frame_productos)

def seleccionar_cantidad(producto):
    """Abre una ventana emergente para seleccionar la inventario del producto."""
    id_producto, nombre, imagen_path, precio_venta_con_iva, precio_venta_con_iva_bs, cantidad_stock = producto

    top = Toplevel()
    top.title(f"Seleccionar inventario para {nombre}")

    Label(top, text=f"Producto: {nombre}", font=("Arial", 10)).pack(pady=5)
    Label(top, text=f"Precio (Bs): {precio_venta_con_iva_bs}", font=("Arial", 10)).pack(pady=5)
    Label(top, text=f"Stock disponible: {cantidad_stock}", font=("Arial", 10)).pack(pady=5)

    Label(top, text="Cantidad:", font=("Arial", 10)).pack(pady=5)
    entry_cantidad = Entry(top, font=("Arial", 10))
    entry_cantidad.pack(pady=5)

    Button(top, text="Agregar al carrito", command=lambda: agregar_al_carrito(top, producto, entry_cantidad), font=("Arial", 10)).pack(pady=5)

def agregar_al_carrito(top, producto, entry_cantidad):
    """Agrega el producto al carrito con la inventario seleccionada."""
    id_producto, nombre, imagen_path, precio_venta_con_iva, precio_venta_con_iva_bs, cantidad_stock = producto
    inventario = int(entry_cantidad.get().strip())

    if inventario > cantidad_stock:
        messagebox.showerror("Error", "Cantidad solicitada excede el stock disponible.")
        return

    subtotal_bs = inventario * precio_venta_con_iva_bs

    tree_carrito.insert("", "end", values=(id_producto, nombre, inventario, precio_venta_con_iva_bs, subtotal_bs))

    # Actualizar el stock en la base de datos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET inventario = inventario - ? WHERE id = ?", (inventario, id_producto))
    conn.commit()
    conn.close()

    # Actualizar totales
    actualizar_totales()

    # Refrescar la lista de productos
    refrescar_productos()

    top.destroy()

def actualizar_totales():
    """Actualiza los totales de la venta."""
    total_bs = 0
    total_divisas = 0
    iva_total = 0

    iva = obtener_iva() / 100 # Suponiendo que el IVA está almacenado como porcentaje

    for item in tree_carrito.get_children():
        producto = tree_carrito.item(item)["values"]
        inventario = producto[2]
        precio_bs = float(producto[3])  # Convertir a float
        subtotal_bs = float(producto[4])  # Convertir a float
        iva_producto = precio_bs * iva

        total_bs += subtotal_bs
        total_divisas += subtotal_bs / tasa
        iva_total += iva_producto * inventario

    label_total_bs.configure(text=f"{total_bs:.2f} Bs")
    label_total_divisas.configure(text=f"{total_divisas:.2f} USD")
    label_iva_total.configure(text=f"{iva_total:.2f} Bs")


# Llamar a la interfaz
interfaz_pos()