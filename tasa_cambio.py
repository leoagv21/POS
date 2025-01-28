import customtkinter as ctk
from tkinter import messagebox
from db_manager import get_connection

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
    root.geometry("700x500")

    # Título principal
    ctk.CTkLabel(root, text="Gestión de Tasa de Cambio", font=("Arial", 20, "bold")).pack(pady=10)

    # Entrada para la tasa actual
    frame_input = ctk.CTkFrame(root)
    frame_input.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(frame_input, text="Tasa de Cambio Actual (Bs/USD):").pack(side="left", padx=10)
    entry_tasa = ctk.CTkEntry(frame_input, placeholder_text="Introduce la tasa actual")
    entry_tasa.pack(side="left", padx=10, fill="x", expand=True)

    # Botón para actualizar la tasa
    ctk.CTkButton(
        root,
        text="Actualizar Tasa",
        command=lambda: actualizar_tasa_cambio(entry_tasa.get(), combo_tasas)
    ).pack(pady=10)

    # Título para la lista de tasas
    ctk.CTkLabel(root, text="Tasas de Cambio Anteriores:", font=("Arial", 14)).pack(pady=10)

    # ComboBox para mostrar y seleccionar tasas
    frame_lista = ctk.CTkFrame(root)
    frame_lista.pack(pady=10, padx=20, fill="both", expand=True)

    combo_tasas = ctk.CTkComboBox(frame_lista, width=300, font=("Arial", 12))
    combo_tasas.pack(side="left", padx=10, pady=10, fill="x", expand=True)

    # Botón para seleccionar una tasa
    ctk.CTkButton(
        root,
        text="Seleccionar Tasa",
        command=lambda: seleccionar_tasa(combo_tasas, entry_tasa)
    ).pack(pady=10)

    # Cargar la lista inicial de tasas
    refrescar_lista(combo_tasas)

    root.mainloop()

if __name__ == "__main__":
    interfaz_tasa_cambio()
