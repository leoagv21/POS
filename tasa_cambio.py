import customtkinter as ctk
from tkinter import messagebox
from db_manager import get_connection
import os
from PIL import Image, ImageTk

def obtener_tasas():
    """Obtiene todas las tasas de cambio de la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, tasa, fecha FROM tasa_cambio ORDER BY id DESC")
        tasas = cursor.fetchall()
        return tasas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener las tasas de cambio: {e}")
        return []
    finally:
        conn.close()

def actualizar_tasa_cambio(nueva_tasa, combo_tasas):
    """Actualiza la tasa de cambio en la base de datos."""
    if not nueva_tasa or not nueva_tasa.replace('.', '', 1).isdigit():
        messagebox.showerror("Error", "Por favor, introduce una tasa válida.")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tasa_cambio (tasa) VALUES (?)", (float(nueva_tasa),))
        conn.commit()
        messagebox.showinfo("Éxito", "Tasa de cambio actualizada correctamente.")
        refrescar_lista(combo_tasas)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la tasa de cambio: {e}")
    finally:
        conn.close()

def seleccionar_tasa(combo_tasas, entry_tasa):
    """Selecciona una tasa de la lista y la coloca en el campo de entrada."""
    seleccion = combo_tasas.get()
    if seleccion:
        try:
            tasa = seleccion.split(" - Tasa: ")[1].split(" ")[0]
            entry_tasa.delete(0, 'end')
            entry_tasa.insert(0, tasa)
        except IndexError:
            messagebox.showerror("Error", "Selecciona una tasa válida de la lista.")

def refrescar_lista(combo_tasas):
    """Actualiza la lista de tasas en la interfaz."""
    tasas = obtener_tasas()
    combo_tasas.set("Seleccione una tasa")  # Reset the combo box default text
    combo_tasas.configure(values=[f"ID {id_tasa} - Tasa: {tasa} Bs/USD - Fecha: {fecha}" for id_tasa, tasa, fecha in tasas])

def interfaz_tasa_cambio():
    """Crea la interfaz para gestionar la tasa de cambio."""
    ctk.set_appearance_mode("light")  # Modo claro
    ctk.set_default_color_theme("blue")  # Tema de color

    root = ctk.CTk()
    root.title("Gestionar Tasa de Cambio")
    root.geometry("800x600")

    # Cambiar el icono de la ventana
    icon_path = os.path.join(os.path.dirname(__file__), 'icono.ico')  # Cambia 'nuevo_icono.ico' por el nombre de tu nuevo icono
    root.iconbitmap(icon_path)

    # Título principal
    ctk.CTkLabel(root, text="Gestión de Tasa de Cambio", font=("Arial", 24, "bold")).grid(row=1, column=0, columnspan=2, pady=20)

    # Entrada para la tasa actual
    frame_input = ctk.CTkFrame(root)
    frame_input.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="ew")

    ctk.CTkLabel(frame_input, text="Tasa de Cambio Actual (Bs/USD):", font=("Arial", 14)).grid(row=0, column=0, padx=10)
    entry_tasa = ctk.CTkEntry(frame_input, placeholder_text="Introduce la tasa actual", font=("Arial", 14))
    entry_tasa.grid(row=0, column=1, padx=10, sticky="ew")

    # Botón para actualizar la tasa
    ctk.CTkButton(
        root,
        text="Actualizar Tasa",
        command=lambda: actualizar_tasa_cambio(entry_tasa.get(), combo_tasas),
        font=("Arial", 14)
    ).grid(row=3, column=0, columnspan=2, pady=20)

    # Título para la lista de tasas
    ctk.CTkLabel(root, text="Tasas de Cambio Anteriores:", font=("Arial", 18)).grid(row=4, column=0, columnspan=2, pady=10)

    # ComboBox para mostrar y seleccionar tasas
    frame_lista = ctk.CTkFrame(root)
    frame_lista.grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

    combo_tasas = ctk.CTkComboBox(frame_lista, width=400, font=("Arial", 14))
    combo_tasas.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    # Botón para seleccionar una tasa
    ctk.CTkButton(
        root,
        text="Seleccionar Tasa",
        command=lambda: seleccionar_tasa(combo_tasas, entry_tasa),
        font=("Arial", 14)
    ).grid(row=6, column=0, columnspan=2, pady=20)

    # Ajustar el tamaño de las columnas
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(5, weight=1)

    # Cargar la lista inicial de tasas
    refrescar_lista(combo_tasas)

    root.mainloop()

if __name__ == "__main__":
    interfaz_tasa_cambio()