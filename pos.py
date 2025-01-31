import customtkinter as ctk
from tkinter import messagebox, ttk, Toplevel, Entry, Label, Button
from db_manager import get_connection
from PIL import Image, ImageTk
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

def generar_factura(nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total):
    """Genera una factura en formato PDF."""
    factura_path = os.path.join(os.path.dirname(__file__), f"factura_{cedula_rif}.pdf")
    c = canvas.Canvas(factura_path, pagesize=letter)
    width, height = letter

    # Membrete y logo
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Nombre del Local")
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 450, height - 100, width=100, height=100)

    # Información del cliente
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, f"Nombre del Cliente: {nombre_cliente}")
    c.drawString(50, height - 170, f"Cédula o RIF: {cedula_rif}")
    c.drawString(50, height - 190, f"Tasa de Cambio: {tasa:.2f} BCV")
    
    # Detalle de la factura
    c.setFont("Helvetica-Bold", 14)
    

    # Totales
    c.drawString(50, height - 230, f"Subtotal: {total_bs - iva_total:.2f}")
    c.drawString(50, height - 250, f"IVA Total (Bs): {iva_total:.2f}")
    c.drawString(50, height - 270, f"Total: {total_bs:.2f}")
   

    c.save()
    messagebox.showinfo("Factura", f"Factura generada correctamente: {factura_path}")

def finalizar_venta():
    """Finaliza la venta y guarda los datos en la base de datos."""
    nombre_cliente = entry_nombre_cliente.get().strip()
    cedula_rif = entry_cedula_rif.get().strip()

    if not nombre_cliente or not cedula_rif:
        messagebox.showerror("Error", "Por favor, ingrese el nombre del cliente y la cédula o RIF.")
        return

    total_bs = float(label_total_bs.cget("text").replace(" Bs", ""))
    total_divisas = float(label_total_divisas.cget("text").replace(" USD", ""))
    iva_total = float(label_iva_total.cget("text").replace(" Bs", ""))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO ventas (nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total)
        VALUES (?, ?, ?, ?, ?)
        """, (nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total))
        id_venta = cursor.lastrowid

        for item in tree_carrito.get_children():
            producto = tree_carrito.item(item)["values"]
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
    generar_factura(nombre_cliente, cedula_rif, total_bs, total_divisas, iva_total)
    limpiar_formulario()

def interfaz_pos():
    """Interfaz para el punto de venta."""

    global entry_nombre_cliente, entry_cedula_rif, tree_carrito, label_total_bs, label_total_divisas, label_iva_total, tasa

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Punto de Venta")
    root.state('zoomed')  # Maximizar la ventana al iniciar

    # Establecer el icono del programa
    icon_path = os.path.join(os.path.dirname(__file__), 'icono.png')
    icon_image = ImageTk.PhotoImage(file=icon_path)
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

    # Botón para generar factura sin finalizar la venta
    ctk.CTkButton(frame_main, text="Generar Factura", command=lambda: generar_factura(entry_nombre_cliente.get().strip(), entry_cedula_rif.get().strip(), float(label_total_bs.cget("text").replace(" Bs", "")), float(label_total_divisas.cget("text").replace(" USD", "")), float(label_iva_total.cget("text").replace(" Bs", ""))), font=("Arial", 10)).grid(row=4, column=2, columnspan=2, pady=5, sticky="ew")

    # Obtener tasa de cambio actual
    tasa = obtener_tasa_cambio()

    # Cargar productos en la tabla de productos
    cargar_productos(frame_productos)

    root.mainloop()

def cargar_productos(frame):
    """Carga los productos en el frame como botones con imágenes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, imagen, precio_venta_con_iva, precio_venta_con_iva_bs FROM productos")
    productos = cursor.fetchall()
    conn.close()

    for producto in productos:
        id_producto, nombre, imagen_path, precio_usd, precio_bs = producto
        if imagen_path and os.path.exists(imagen_path):
            imagen = Image.open(imagen_path)
            imagen = imagen.resize((50, 50), Image.LANCZOS)
            imagen = ImageTk.PhotoImage(imagen)
            button = ctk.CTkButton(frame, image=imagen, text="", command=lambda p=producto: seleccionar_cantidad(p))
            button.image = imagen  # Guardar referencia para evitar que la imagen sea recolectada por el GC
        else:
            button = ctk.CTkButton(frame, text=nombre, command=lambda p=producto: seleccionar_cantidad(p))
        button.pack(side="left", padx=2, pady=2)

def seleccionar_cantidad(producto):
    """Abre una ventana emergente para seleccionar la cantidad del producto."""
    id_producto, nombre, imagen_path, precio_venta_con_iva, precio_venta_con_iva_bs = producto

    top = Toplevel()
    top.title(f"Seleccionar cantidad para {nombre}")

    Label(top, text=f"Producto: {nombre}", font=("Arial", 10)).pack(pady=5)
    Label(top, text=f"Precio (Bs): {precio_venta_con_iva_bs}", font=("Arial", 10)).pack(pady=5)

    Label(top, text="Cantidad:", font=("Arial", 10)).pack(pady=5)
    entry_cantidad = Entry(top, font=("Arial", 10))
    entry_cantidad.pack(pady=5)

    Button(top, text="Agregar al carrito", command=lambda: agregar_al_carrito(top, producto, entry_cantidad), font=("Arial", 10)).pack(pady=5)

def agregar_al_carrito(top, producto, entry_cantidad):
    """Agrega el producto al carrito con la cantidad seleccionada."""
    id_producto, nombre, imagen_path, precio_venta_con_iva, precio_venta_con_iva_bs = producto
    cantidad = int(entry_cantidad.get().strip())
    subtotal_bs = cantidad * precio_venta_con_iva_bs

    tree_carrito.insert("", "end", values=(id_producto, nombre, cantidad, precio_venta_con_iva_bs, subtotal_bs))

    # Actualizar totales
    actualizar_totales()

    top.destroy()

def actualizar_totales():
    """Actualiza los totales de la venta."""
    total_bs = 0
    total_divisas = 0
    iva_total = 0

    iva = obtener_iva() / 100 # Suponiendo que el IVA está almacenado como porcentaje

    for item in tree_carrito.get_children():
        producto = tree_carrito.item(item)["values"]
        cantidad = producto[2]
        precio_bs = float(producto[3])  # Convertir a float
        subtotal_bs = float(producto[4])  # Convertir a float
        iva_producto = precio_bs * iva

        total_bs += subtotal_bs
        total_divisas += subtotal_bs / tasa
        iva_total += iva_producto * cantidad

    label_total_bs.configure(text=f"{total_bs:.2f} Bs")
    label_total_divisas.configure(text=f"{total_divisas:.2f} USD")
    label_iva_total.configure(text=f"{iva_total:.2f} Bs")

def limpiar_formulario():
    """Limpia el formulario después de finalizar la venta."""
    entry_nombre_cliente.delete(0, 'end')
    entry_cedula_rif.delete(0, 'end')
    for item in tree_carrito.get_children():
        tree_carrito.delete(item)
    label_total_bs.configure(text="")
    label_total_divisas.configure(text="")
    label_iva_total.configure(text="")

# Llamar a la interfaz
interfaz_pos()