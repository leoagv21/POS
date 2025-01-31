import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from tkinter import PhotoImage  # Importar PhotoImage desde tkinter
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

def agregar_producto(nombre, cantidad, costo_usd, tasa, imagen_path, unidad, precio_venta_sin_iva, iva):
    """Agrega un nuevo producto al inventario."""
    if not nombre or not unidad:
        messagebox.showerror("Error", "Por favor, ingresa todos los campos correctamente.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        costo_bs = float(costo_usd) * tasa
        precio_bs_und = costo_bs / cantidad
        precio_venta_con_iva = precio_venta_sin_iva * (1 + iva / 100)
        precio_venta_con_iva_bs = precio_venta_con_iva * tasa

        # Si se seleccionó una imagen, la guardamos en la carpeta 'imagenes'
        imagen_guardada = None
        if imagen_path:
            os.makedirs("imagenes", exist_ok=True)
            imagen_guardada = os.path.join("imagenes", os.path.basename(imagen_path))
            Image.open(imagen_path).save(imagen_guardada)  # Guardamos la imagen

        cursor.execute("""
            INSERT INTO productos (nombre, imagen, precio_usd, precio_bs, inventario, tasa_cambio, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_venta_con_iva_bs, precio_bs_und)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, imagen_guardada, float(costo_usd), costo_bs, int(cantidad), tasa, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_venta_con_iva_bs, precio_bs_und))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto agregado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")
    finally:
        conn.close()
        
def editar_producto(id_producto, nombre, cantidad, costo_usd, tasa, imagen_path, unidad, precio_venta_sin_iva, iva):
    """Edita un producto existente."""
    if not nombre or not unidad:
        messagebox.showerror("Error", "Por favor, ingresa todos los campos correctamente.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        costo_bs = float(costo_usd) * tasa
        precio_bs_und = costo_bs / cantidad
        precio_venta_con_iva = precio_venta_sin_iva * (1 + iva / 100)
        precio_venta_con_iva_bs = precio_venta_con_iva * tasa

        # Si se seleccionó una imagen, la guardamos en la carpeta 'imagenes'
        imagen_guardada = None
        if imagen_path:
            os.makedirs("imagenes", exist_ok=True)
            imagen_guardada = os.path.join("imagenes", os.path.basename(imagen_path))
            Image.open(imagen_path).save(imagen_guardada)  # Guardamos la imagen

        cursor.execute("""
            UPDATE productos
            SET nombre = ?, inventario = ?, precio_usd = ?, precio_bs = ?, imagen = ?, tasa_cambio = ?, unidad = ?, precio_venta_sin_iva = ?, iva = ?, precio_venta_con_iva = ?, precio_venta_con_iva_bs = ?, precio_bs_und = ?
            WHERE id = ?
        """, (nombre, int(cantidad), float(costo_usd), costo_bs, imagen_guardada, tasa, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_venta_con_iva_bs, precio_bs_und, id_producto))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")
    finally:
        conn.close()

def cargar_productos(tree):
    """Carga los productos en la tabla Treeview."""
    for row in tree.get_children():
        tree.delete(row)
    
    productos = obtener_productos()
    for producto in productos:
        tree.insert("", "end", values=producto)

def validar_editar():
    try:
        nombre = entry_nombre.get().strip()
        cantidad = int(entry_cantidad.get().strip())
        costo_usd = float(entry_costo_usd.get().strip())
        unidad = entry_unidad.get().strip()



        if not nombre or not unidad:
            raise ValueError("El nombre y la unidad no pueden estar vacíos.")

        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            id_producto = item['values'][0]
            editar_producto(id_producto, nombre, cantidad, costo_usd, tasa, imagen_path, unidad, tree)
            cargar_productos(tree)  # Recargar productos en la tabla
            messagebox.showinfo("Éxito", "Producto editado correctamente.")
    except ValueError as e:
        messagebox.showerror("Error", f"Datos inválidos: {e}")

def seleccionar_imagen():
    """Permite seleccionar una imagen para el producto."""
    imagen_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.gif")])
    return imagen_path

def mostrar_ficha_producto(id_producto, root, label_imagen, label_nombre, label_precio_usd, label_precio_bs, label_inventario, label_unidad, label_precio_venta_sin_iva, label_iva, label_precio_venta_con_iva, label_precio_bs_und, label_precio_venta_con_iva_bs):
    """Muestra la ficha de un producto específico."""
    producto = obtener_producto(id_producto)
    if producto:
        # Desempaquetar los valores que devuelve la consulta
        nombre, imagen, precio_usd, precio_bs, inventario, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_bs_und, precio_venta_con_iva_bs = producto
        
        # Mostrar imagen del producto
        if imagen:
            imagen_producto = Image.open(imagen)
            imagen_producto = imagen_producto.resize((100, 100))
            imagen_tk = ctk.CTkImage(light_image=imagen_producto, size=(100, 100))
            label_imagen.configure(image=imagen_tk, text="")
            label_imagen.image = imagen_tk  # Guardar la referencia de la imagen
        else:
            label_imagen.configure(image='', text="No hay imagen")

        # Mostrar datos del producto
        label_nombre.configure(text=f"Nombre: {nombre}")
        label_precio_usd.configure(text=f"Precio (USD): {precio_usd:.2f}")
        label_precio_bs.configure(text=f"Precio (Bs): {precio_bs:.2f}")
        label_inventario.configure(text=f"Inventario: {inventario}")
        label_unidad.configure(text=f"Unidad: {unidad}")
        label_precio_venta_sin_iva.configure(text=f"Precio Venta Sin IVA: {precio_venta_sin_iva:.2f}")
        label_iva.configure(text=f"IVA: {iva:.2f}%")
        label_precio_venta_con_iva.configure(text=f"Precio Venta Con IVA: {precio_venta_con_iva:.2f}")
        label_precio_bs_und.configure(text=f"Precio Unitario Sin IVA (Bs): {precio_bs_und:.2f}")
        label_precio_venta_con_iva_bs.configure(text=f"Precio Venta Con IVA (Bs): {precio_venta_con_iva_bs:.2f}")
       
        # Actualizar campos de entrada para edición
        entry_nombre.delete(0, 'end')
        entry_nombre.insert(0, nombre)
        entry_cantidad.delete(0, 'end')
        entry_cantidad.insert(0, inventario)
        entry_costo_usd.delete(0, 'end')
        entry_costo_usd.insert(0, precio_usd)
        entry_unidad.delete(0, 'end')
        entry_unidad.insert(0, unidad)
        entry_precio_venta_sin_iva.delete(0, 'end')
        entry_precio_venta_sin_iva.insert(0, precio_venta_sin_iva)
        entry_iva.delete(0, 'end')
        entry_iva.insert(0, iva)


def obtener_producto(id_producto):
    """Obtiene un producto específico por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, imagen, precio_usd, precio_bs, inventario, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_bs_und, precio_venta_con_iva_bs FROM productos WHERE id = ?", (id_producto,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def obtener_productos():
    """Obtiene una lista de todos los productos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio_usd, precio_bs, inventario, unidad, precio_venta_sin_iva, iva, precio_venta_con_iva, precio_bs_und, precio_venta_con_iva_bs FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def mostrar_lista_productos(root):
    """Muestra una lista de todos los productos disponibles para editar o seleccionar."""
    productos = obtener_productos()
    for producto in productos:
        id_producto, nombre, precio_usd, precio_bs, inventario, unidad = producto
        button_producto = ctk.CTkButton(
            root, text=f"{nombre} - {precio_usd} USD - {unidad}", 
            command=lambda id_producto=id_producto: mostrar_ficha_producto(id_producto, root)
        )
        button_producto.pack(pady=5)

def eliminar_producto(id_producto, tree):
    """Elimina un producto del inventario."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
        # Recargar la lista de productos
        cargar_productos(tree)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")
    finally:
        conn.close()

def interfaz_inventario():
    """Interfaz mejorada para la gestión de inventario."""

    global entry_nombre, entry_cantidad, entry_costo_usd, entry_unidad, tasa, imagen_path, tree, entry_precio_venta_sin_iva, entry_iva, label_precio_bs, label_precio_venta_con_iva_usd, label_precio_venta_con_iva_bs, label_precio_bs_und

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Gestión de Inventario")
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
    frame_main.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    frame_main.grid_rowconfigure(1, weight=1)
    frame_main.grid_columnconfigure(1, weight=1)

    # Título principal
    ctk.CTkLabel(frame_main, text="Gestión de Inventario", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

    # Frame para lista de productos
    frame_lista = ctk.CTkFrame(frame_main)
    frame_lista.grid(row=1, column=1, columnspan=3, pady=10, sticky="nsew")
    frame_lista.grid_rowconfigure(0, weight=1)
    frame_lista.grid_columnconfigure(0, weight=1)

    # Tabla de productos
    columnas = ("ID", "Nombre", "Precio (USD)", "Precio (Bs)", "Inventario", "Unidad", "Precio Venta Sin IVA", "IVA", "Precio Venta Con IVA", "Precio Unitario (Bs)")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=8)
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    tree.grid(row=0, column=0, sticky="nsew")

    # Añadir scrollbar a la tabla
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Cargar productos en la tabla
    cargar_productos(tree)

    # Frame de entrada
    frame_input = ctk.CTkFrame(frame_main)
    frame_input.grid(row=2, column=1, columnspan=3, pady=10, padx=20, sticky="ew")

    ctk.CTkLabel(frame_input, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_nombre = ctk.CTkEntry(frame_input, width=150)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_input, text="Cantidad:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_cantidad = ctk.CTkEntry(frame_input, width=80)
    entry_cantidad.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(frame_input, text="Costo (USD):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_costo_usd = ctk.CTkEntry(frame_input, width=80)
    entry_costo_usd.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_input, text="Unidad:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    entry_unidad = ctk.CTkEntry(frame_input, width=80)
    entry_unidad.grid(row=1, column=3, padx=5, pady=5)

    ctk.CTkLabel(frame_input, text="Precio Venta Sin IVA (USD):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_precio_venta_sin_iva = ctk.CTkEntry(frame_input, width=80)
    entry_precio_venta_sin_iva.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_input, text="IVA (%):").grid(row=2, column=2, padx=5, pady=5, sticky="e")
    entry_iva = ctk.CTkEntry(frame_input, width=80)
    entry_iva.grid(row=2, column=3, padx=5, pady=5)
    entry_iva.insert(0, "16")  # Valor por defecto del IVA

    # Campos para mostrar los precios calculados
    ctk.CTkLabel(frame_input, text="Precio Sin IVA (Bs):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    label_precio_bs = ctk.CTkLabel(frame_input, text="")
    label_precio_bs.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_input, text="Precio Unitario (Bs):").grid(row=3, column=2, padx=5, pady=5, sticky="e")
    label_precio_bs_und = ctk.CTkLabel(frame_input, text="")
    label_precio_bs_und.grid(row=3, column=3, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_input, text="Precio Venta Con IVA (USD):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    label_precio_venta_con_iva_usd = ctk.CTkLabel(frame_input, text="")
    label_precio_venta_con_iva_usd.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_input, text="Precio Venta Con IVA (Bs):").grid(row=4, column=2, padx=5, pady=5, sticky="e")
    label_precio_venta_con_iva_bs = ctk.CTkLabel(frame_input, text="")
    label_precio_venta_con_iva_bs.grid(row=4, column=3, padx=5, pady=5, sticky="w")

    # Botón para seleccionar imagen
    imagen_path = None
    def seleccionar_y_guardar_imagen():
        global imagen_path
        imagen_path = seleccionar_imagen()
        if imagen_path:
            messagebox.showinfo("Imagen seleccionada", f"Imagen cargada: {imagen_path}")

    ctk.CTkButton(frame_input, text="Seleccionar Imagen", command=seleccionar_y_guardar_imagen).grid(row=5, column=0, columnspan=4, padx=5, pady=5)

    # Obtener tasa de cambio actual
    tasa = obtener_tasa_cambio()
    if not tasa:
        messagebox.showerror("Error", "No se pudo obtener la tasa de cambio.")
        return

    # Función para calcular precios automáticamente
    def calcular_precios(event=None):
        try:
            cantidad = int(entry_cantidad.get().strip())
            costo_usd = float(entry_costo_usd.get().strip())
            precio_venta_sin_iva = float(entry_precio_venta_sin_iva.get().strip())
            iva = float(entry_iva.get().strip())

            precio_unitario_usd = costo_usd / cantidad
            precio_unitario_bs = precio_unitario_usd * tasa
            precio_total_bs = costo_usd * tasa
            precio_venta_con_iva_usd = precio_venta_sin_iva * (1 + iva / 100)
            precio_venta_con_iva_bs = precio_venta_con_iva_usd * tasa

            label_precio_bs.configure(text=f"{precio_total_bs:.2f} Bs")
            label_precio_bs_und.configure(text=f"{precio_unitario_bs:.2f} Bs")
            label_precio_venta_con_iva_usd.configure(text=f"{precio_venta_con_iva_usd:.2f} USD")
            label_precio_venta_con_iva_bs.configure(text=f"{precio_venta_con_iva_bs:.2f} Bs")
        except ValueError:
            pass

    # Vincular la función de cálculo a los eventos de entrada
    entry_cantidad.bind("<KeyRelease>", calcular_precios)
    entry_costo_usd.bind("<KeyRelease>", calcular_precios)
    entry_precio_venta_sin_iva.bind("<KeyRelease>", calcular_precios)
    entry_iva.bind("<KeyRelease>", calcular_precios)

    # Frame para mostrar detalles del producto
    frame_detalles = ctk.CTkFrame(frame_main)
    frame_detalles.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky="n")

    label_imagen = ctk.CTkLabel(frame_detalles, text="No hay imagen", width=100, height=100)
    label_imagen.pack(pady=10)

    label_nombre = ctk.CTkLabel(frame_detalles, text="Nombre: ")
    label_nombre.pack(pady=5)

    label_precio_usd = ctk.CTkLabel(frame_detalles, text="Precio (USD): ")
    label_precio_usd.pack(pady=5)

    label_precio_bs = ctk.CTkLabel(frame_detalles, text="Precio (Bs): ")
    label_precio_bs.pack(pady=5)

    label_inventario = ctk.CTkLabel(frame_detalles, text="Inventario: ")
    label_inventario.pack(pady=5)

    label_unidad = ctk.CTkLabel(frame_detalles, text="Unidad: ")
    label_unidad.pack(pady=5)

    label_precio_venta_sin_iva = ctk.CTkLabel(frame_detalles, text="Precio Venta Sin IVA: ")
    label_precio_venta_sin_iva.pack(pady=5)

    label_iva = ctk.CTkLabel(frame_detalles, text="IVA: ")
    label_iva.pack(pady=5)

    label_precio_venta_con_iva = ctk.CTkLabel(frame_detalles, text="Precio Venta Con IVA: ")
    label_precio_venta_con_iva.pack(pady=5)

    label_precio_bs_und = ctk.CTkLabel(frame_detalles, text="Precio Unitario (Bs): ")
    label_precio_bs_und.pack(pady=5)

    label_precio_venta_con_iva_bs = ctk.CTkLabel(frame_detalles, text="Precio Venta Con IVA (Bs): ")
    label_precio_venta_con_iva_bs.pack(pady=5)

    # Función para limpiar el formulario
    def limpiar_formulario():
        entry_nombre.delete(0, 'end')
        entry_cantidad.delete(0, 'end')
        entry_costo_usd.delete(0, 'end')
        entry_unidad.delete(0, 'end')
        entry_precio_venta_sin_iva.delete(0, 'end')
        entry_iva.delete(0, 'end')
        label_precio_bs.configure(text="")
        label_precio_bs_und.configure(text="")
        label_precio_venta_con_iva_usd.configure(text="")
        label_precio_venta_con_iva_bs.configure(text="")

    # Función para validar y agregar producto
    def validar_agregar():
        try:
            nombre = entry_nombre.get().strip()
            cantidad = int(entry_cantidad.get().strip())
            costo_usd = float(entry_costo_usd.get().strip())
            unidad = entry_unidad.get().strip()
            precio_venta_sin_iva = float(entry_precio_venta_sin_iva.get().strip())
            iva = float(entry_iva.get().strip())

            if not nombre or not unidad:
                raise ValueError("El nombre y la unidad no pueden estar vacíos.")

            agregar_producto(nombre, cantidad, costo_usd, tasa, imagen_path, unidad, precio_venta_sin_iva, iva)
            cargar_productos(tree)  # Recargar productos en la tabla
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            limpiar_formulario()  # Limpiar el formulario después de agregar el producto
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")

    # Botón para agregar producto
    ctk.CTkButton(frame_main, text="Agregar Producto", command=validar_agregar).grid(row=3, column=1, pady=10, sticky="ew")

    # Botón para editar producto (se requiere un ID válido)
    def validar_editar():
        try:
            nombre = entry_nombre.get().strip()
            cantidad = int(entry_cantidad.get().strip())
            costo_usd = float(entry_costo_usd.get().strip())
            unidad = entry_unidad.get().strip()
            precio_venta_sin_iva = float(entry_precio_venta_sin_iva.get().strip())
            iva = float(entry_iva.get().strip())

            if not nombre or not unidad:
                raise ValueError("El nombre y la unidad no pueden estar vacíos.")

            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                id_producto = item['values'][0]
                editar_producto(id_producto, nombre, cantidad, costo_usd, tasa, imagen_path, unidad, precio_venta_sin_iva, iva)
                cargar_productos(tree)  # Recargar productos en la tabla
                messagebox.showinfo("Éxito", "Producto editado correctamente.")
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {e}")

    ctk.CTkButton(frame_main, text="Editar Producto", command=validar_editar).grid(row=3, column=2, columnspan=1, pady=10, sticky="ew")

    # Botón para eliminar producto (se requiere un ID válido)
    def validar_eliminar():
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            id_producto = item['values'][0]
            eliminar_producto(id_producto, tree)
            cargar_productos(tree)  # Recargar productos en la tabla

    ctk.CTkButton(frame_main, text="Eliminar Producto", command=validar_eliminar).grid(row=3, column=3, columnspan=1, pady=10, sticky="ew")

    # Evento para seleccionar producto en la tabla
    def on_tree_select(event):
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            id_producto = item['values'][0]
            mostrar_ficha_producto(id_producto, root, label_imagen, label_nombre, label_precio_usd, label_precio_bs, label_inventario, label_unidad, label_precio_venta_sin_iva, label_iva, label_precio_venta_con_iva, label_precio_bs_und, label_precio_venta_con_iva_bs)

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    root.mainloop()

# Llamar a la interfaz
interfaz_inventario()