import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from db_manager import get_connection
import os

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

def obtener_productos():
    """Obtiene todos los productos en inventario."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre, precio_usd, precio_bs, inventario FROM productos")
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los productos: {e}")
        return []
    finally:
        conn.close()

def agregar_producto(nombre, cantidad, costo_usd, tasa, imagen_path):
    """Agrega un nuevo producto al inventario."""
    if not nombre or not cantidad.isdigit() or not costo_usd.replace('.', '', 1).isdigit():
        messagebox.showerror("Error", "Por favor, ingresa todos los campos correctamente.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        costo_bs = float(costo_usd) * tasa

        # Si se seleccionó una imagen, la guardamos en la carpeta 'imagenes'
        imagen_guardada = None
        if imagen_path:
            imagen_guardada = os.path.join("imagenes", os.path.basename(imagen_path))
            Image.open(imagen_path).save(imagen_guardada)  # Guardamos la imagen

        cursor.execute("""
            INSERT INTO productos (nombre, imagen, precio_usd, precio_bs, inventario, tasa_cambio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, imagen_guardada, float(costo_usd), costo_bs, int(cantidad), tasa))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto agregado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")
    finally:
        conn.close()

def editar_producto(id_producto, nombre, cantidad, costo_usd, tasa, imagen_path):
    """Edita un producto existente."""
    if not nombre or not cantidad.isdigit() or not costo_usd.replace('.', '', 1).isdigit():
        messagebox.showerror("Error", "Por favor, ingresa todos los campos correctamente.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        costo_bs = float(costo_usd) * tasa

        # Si se seleccionó una imagen, la guardamos en la carpeta 'imagenes'
        imagen_guardada = None
        if imagen_path:
            imagen_guardada = os.path.join("imagenes", os.path.basename(imagen_path))
            Image.open(imagen_path).save(imagen_guardada)  # Guardamos la imagen

        cursor.execute("""
            UPDATE productos
            SET nombre = ?, inventario = ?, precio_usd = ?, precio_bs = ?, imagen = ?, tasa_cambio = ?
            WHERE id = ?
        """, (nombre, int(cantidad), float(costo_usd), costo_bs, imagen_guardada, tasa, id_producto))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")
    finally:
        conn.close()

def seleccionar_imagen():
    """Permite seleccionar una imagen para el producto."""
    imagen_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.gif")])
    return imagen_path

def mostrar_ficha_producto(id_producto, root):
    """Muestra la ficha de un producto específico."""
    producto = obtener_producto(id_producto)
    if producto:
        # Desempaquetar solo los 5 valores que devuelve la consulta
        nombre, imagen, precio_usd, precio_bs, inventario = producto
        
        # Mostrar imagen del producto
        imagen_producto = Image.open(imagen) if imagen else None
        imagen_producto = imagen_producto.resize((100, 100)) if imagen_producto else None
        imagen_tk = ImageTk.PhotoImage(imagen_producto) if imagen_producto else None
        label_imagen = ctk.CTkLabel(root, image=imagen_tk, text="No hay imagen")
        label_imagen.image = imagen_tk  # Guardar la referencia de la imagen
        label_imagen.pack(pady=10)

        # Mostrar datos del producto
        ctk.CTkLabel(root, text=f"Nombre: {nombre}").pack(pady=5)
        ctk.CTkLabel(root, text=f"Precio (USD): {precio_usd}").pack(pady=5)
        ctk.CTkLabel(root, text=f"Precio (Bs): {precio_bs}").pack(pady=5)
        ctk.CTkLabel(root, text=f"Inventario: {inventario}").pack(pady=5)

def mostrar_lista_productos(root):
    """Muestra una lista de todos los productos disponibles para editar o seleccionar."""
    productos = obtener_productos()
    for producto in productos:
        id_producto, nombre, precio_usd, precio_bs, inventario = producto
        button_producto = ctk.CTkButton(
            root, text=f"{nombre} - {precio_usd} USD", 
            command=lambda id=id_producto: mostrar_ficha_producto(id, root)
        )
        button_producto.pack(pady=5)

def interfaz_inventario():
    """Interfaz para agregar, editar y mostrar productos en inventario."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Gestión de Inventario")
    root.geometry("800x600")

    # Título principal
    ctk.CTkLabel(root, text="Gestión de Inventario", font=("Arial", 20, "bold")).pack(pady=10)

    # Mostrar lista de productos
    mostrar_lista_productos(root)

    # Entrada para agregar/editar producto
    frame_input = ctk.CTkFrame(root)
    frame_input.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(frame_input, text="Nombre del Producto:").pack(side="left", padx=10)
    entry_nombre = ctk.CTkEntry(frame_input)
    entry_nombre.pack(side="left", padx=10, fill="x", expand=True)

    ctk.CTkLabel(frame_input, text="Cantidad:").pack(side="left", padx=10)
    entry_cantidad = ctk.CTkEntry(frame_input)
    entry_cantidad.pack(side="left", padx=10, fill="x", expand=True)

    ctk.CTkLabel(frame_input, text="Costo (USD):").pack(side="left", padx=10)
    entry_costo_usd = ctk.CTkEntry(frame_input)
    entry_costo_usd.pack(side="left", padx=10, fill="x", expand=True)

    # Botón para seleccionar imagen
    imagen_path = None
    def seleccionar_y_guardar_imagen():
        nonlocal imagen_path
        imagen_path = seleccionar_imagen()

    ctk.CTkButton(
        frame_input,
        text="Seleccionar Imagen",
        command=seleccionar_y_guardar_imagen
    ).pack(side="left", padx=10)

    # Obtener tasa de cambio actual
    tasa = obtener_tasa_cambio()

    if not tasa:
        messagebox.showerror("Error", "No se pudo obtener la tasa de cambio.")
        return

    # Botón para agregar producto
    ctk.CTkButton(
        root,
        text="Agregar Producto",
        command=lambda: agregar_producto(entry_nombre.get(), entry_cantidad.get(), entry_costo_usd.get(), tasa, imagen_path)
    ).pack(pady=10)

    # Botón para editar producto (por ejemplo, editar el producto con ID 1)
    ctk.CTkButton(
        root,
        text="Editar Producto",
        command=lambda: editar_producto(1, entry_nombre.get(), entry_cantidad.get(), entry_costo_usd.get(), tasa, imagen_path)
    ).pack(pady=10)

    root.mainloop()

# Llamar a la interfaz
interfaz_inventario()
