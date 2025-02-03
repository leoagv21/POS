import tkinter as tk
from tkinter import ttk
import os
import threading
from PIL import Image, ImageTk

# Funciones para abrir las diferentes páginas en hilos separados
def open_gestion_inventario():
    threading.Thread(target=lambda: os.system('python gestion_inventario.py')).start()

def open_pos():
    threading.Thread(target=lambda: os.system('python pos.py')).start()

def open_tasa_cambio():
    threading.Thread(target=lambda: os.system('python tasa_cambio.py')).start()

# Crear la ventana principal
root = tk.Tk()
root.title("Sistema de Gestión de Inventario")

# Maximizar la ventana
root.state('zoomed')

# Estilo
style = ttk.Style()
style.theme_use('clam')  # Usar un tema moderno
style.configure("TButton", font=("Helvetica", 12), padding=10, background="#4CAF50", foreground="white")
style.map("TButton", background=[('active', '#45a049')])
style.configure("TFrame", background="#f0f0f0")

# Crear la barra de menú
menubar = tk.Menu(root)
root.config(menu=menubar)

# Crear el menú de Inventario
inventory_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Inventario", menu=inventory_menu)
inventory_menu.add_command(label="Gestor de Inventario", command=open_gestion_inventario)

# Crear el menú de Punto de Venta
pos_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Punto de Venta", menu=pos_menu)
pos_menu.add_command(label="Sistema POS", command=open_pos)

# Crear el menú de Moneda
currency_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Moneda", menu=currency_menu)
currency_menu.add_command(label="Tasa de Cambio", command=open_tasa_cambio)

# Función para redimensionar la imagen de fondo
def resize_image(event):
    new_width = event.width
    new_height = event.height - 40  # Ajustar para la barra de menú y la barra de derechos de autor
    if new_width > 0 and new_height > 0:
        image = background_image.resize((new_width, new_height))
        background_photo = ImageTk.PhotoImage(image)
        background_label.config(image=background_photo)
        background_label.image = background_photo

# Cargar la imagen de fondo
background_image = Image.open("Fondo.png")
background_photo = ImageTk.PhotoImage(background_image)

# Crear un widget de etiqueta para la imagen de fondo
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

# Vincular el evento de redimensionamiento de la ventana a la función de redimensionamiento de la imagen
root.bind('<Configure>', resize_image)

# Crear una barra de derechos de autor
copyright_frame = ttk.Frame(root, padding="5 5 5 5", style="TFrame")
copyright_frame.place(relwidth=1, rely=1.0, anchor='sw')
copyright_label = ttk.Label(copyright_frame, text="© 2025 leoagv21. Todos los derechos reservados. Diseñado por Leonardo González.", style="TLabel")
copyright_label.pack(fill='x')

# Ejecutar la aplicación
root.mainloop()