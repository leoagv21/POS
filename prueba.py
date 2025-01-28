import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

# Simulación de funciones para la gestión de productos y tasas de cambio.
def obtener_tasa_cambio():
    # Simulamos obtener la tasa de cambio de USD a Bs
    return 36.90  # Ejemplo de tasa de cambio

def seleccionar_imagen():
    # Simulación de la selección de una imagen
    return filedialog.askopenfilename(filetypes=[("Imagenes", "*.jpg;*.png;*.jpeg")])

def agregar_producto(nombre, cantidad, costo_usd, tasa, imagen_path):
    # Función para agregar el producto al inventario (simulación)
    print(f"Producto agregado: {nombre}, Cantidad: {cantidad}, Costo en USD: {costo_usd}, Costo en Bs: {float(costo_usd) * tasa}, Imagen: {imagen_path}")

def editar_producto(producto_id, nombre, cantidad, costo_usd, tasa, imagen_path):
    # Función para editar un producto (simulación)
    print(f"Producto editado: ID {producto_id}, Nombre: {nombre}, Cantidad: {cantidad}, Costo en USD: {costo_usd}, Costo en Bs: {float(costo_usd) * tasa}, Imagen: {imagen_path}")

def eliminar_producto(producto_id):
    # Función para eliminar un producto (simulación)
    print(f"Producto eliminado: ID {producto_id}")

def obtener_productos():
    # Simulación de obtener una lista de productos desde una base de datos
    return [
        {'id': 1, 'nombre': 'Producto 1', 'cantidad': 100, 'costo_usd': 10, 'imagen': 'imagen1.jpg'},
        {'id': 2, 'nombre': 'Producto 2', 'cantidad': 200, 'costo_usd': 20, 'imagen': 'imagen2.jpg'},
        {'id': 3, 'nombre': 'Producto 3', 'cantidad': 150, 'costo_usd': 15, 'imagen': 'imagen3.jpg'}
    ]

def mostrar_ficha_producto(producto_id, root):
    """ Muestra la información de un producto específico en la interfaz. """
    productos = obtener_productos()
    producto = next((p for p in productos if p['id'] == producto_id), None)
    if producto:
        frame_detalles = ctk.CTkFrame(root)
        frame_detalles.pack(pady=20)

        # Nombre del producto
        ctk.CTkLabel(frame_detalles, text=f"Nombre: {producto['nombre']}").pack()

        # Cantidad en inventario
        ctk.CTkLabel(frame_detalles, text=f"Cantidad: {producto['cantidad']}").pack()

        # Precio en USD y Bs
        tasa = obtener_tasa_cambio()
        ctk.CTkLabel(frame_detalles, text=f"Precio en USD: {producto['costo_usd']}").pack()
        ctk.CTkLabel(frame_detalles, text=f"Precio en Bs: {float(producto['costo_usd']) * tasa}").pack()

        # Imagen del producto (Si tiene imagen)
        if producto['imagen']:
            try:
                img = Image.open(producto['imagen'])
                img.thumbnail((100, 100))
                img = ImageTk.PhotoImage(img)
                ctk.CTkLabel(frame_detalles, image=img).pack()
            except Exception as e:
                ctk.CTkLabel(frame_detalles, text="Imagen no disponible").pack()

        # Botones para editar y eliminar
        ctk.CTkButton(frame_detalles, text="Editar Producto", command=lambda: editar_producto(producto_id, producto['nombre'], producto['cantidad'], producto['costo_usd'], tasa, producto['imagen'])).pack(pady=10)
        ctk.CTkButton(frame_detalles, text="Eliminar Producto", command=lambda: eliminar_producto(producto_id)).pack(pady=10)

def interfaz_inventario():
    """ Interfaz para agregar, editar y mostrar productos en inventario. """
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Gestión de Inventario")
    root.geometry("800x600")

    # Título principal
    ctk.CTkLabel(root, text="Gestión de Inventario", font=("Arial", 20, "bold")).pack(pady=10)

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

    # Mostrar lista de productos
    productos = obtener_productos()
    ctk.CTkLabel(root, text="Productos Existentes").pack(pady=10)

    frame_lista = ctk.CTkFrame(root)
    frame_lista.pack(pady=10)

    for producto in productos:
        ctk.CTkButton(frame_lista, text=producto['nombre'], command=lambda producto_id=producto['id']: mostrar_ficha_producto(producto_id, root)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    interfaz_inventario()
