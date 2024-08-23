import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import psutil
import pygetwindow as gw
import ctypes
import threading
import keyboard
import time
import tkinter as tk

# Variables globales para almacenar el handle de la ventana seleccionada y su PID
selected_window_handle = None
selected_process_pid = None

# Lista de títulos de ventanas a excluir
excluded_windows = ['Microsoft Text Input Application', 'Setup', 'Calculator', 
                    'Program Manager', 'Windows Shell Experience Host', 'Settings']

# Función para cambiar la opacidad de una ventana
def set_window_opacity(hwnd, opacity):
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, opacity, 0x2)

# Función para hacer las ventanas seleccionadas invisibles (opacidad 0%)
def darken_windows():
    global selected_window_handle
    if selected_window_handle:
        set_window_opacity(selected_window_handle, 0)  # 0% de opacidad

# Función para restaurar la opacidad de las ventanas seleccionadas al 100%
def restore_windows():
    global selected_window_handle
    if selected_window_handle:
        set_window_opacity(selected_window_handle, 255)  # 100% de opacidad

# Función para mostrar una ventana emergente con el mensaje "Creado por"
def show_message():
    # Crear una ventana de tkinter
    window = tk.Tk()
    window.title("Información")
    window.geometry("200x100")  # Dimensiones de la ventana

    # Agregar una etiqueta con el mensaje
    label = tk.Label(window, text="Creado por Eric Bravo", font=("Arial", 12))
    label.pack(expand=True)

    # Función para cerrar la ventana al presionar Esc
    def close_on_escape(event):
        window.destroy()

    # Vincular la tecla Esc para cerrar la ventana
    window.bind('<Escape>', close_on_escape)

    # Ejecutar la ventana
    window.mainloop()

# Función que crea un item del menú para cada ventana
def create_menu_item(window_title):
    return item(window_title, lambda: select_window(window_title))

# Función para seleccionar la ventana y obtener el proceso asociado
def select_window(window_title):
    global selected_window_handle, selected_process_pid

    # Obtener la ventana seleccionada por su título
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        selected_window_handle = windows[0]._hWnd  # Obtener el handle de la ventana
        selected_process_pid = windows[0].processId  # Obtener el PID asociado a la ventana
        print(f"Ventana seleccionada: {window_title}, PID: {selected_process_pid}")

# Función para generar dinámicamente el menú de ventanas abiertas, excluyendo ciertas ventanas
def get_open_windows_menu():
    windows = gw.getAllTitles()
    # Filtrar ventanas sin título o que están en la lista de exclusión
    windows = [win for win in windows if win.strip() and win not in excluded_windows]

    # Crear un submenú dinámico con las ventanas abiertas
    menu_items = [create_menu_item(window) for window in windows]
    
    return tuple(menu_items)

# Crear un icono en la bandeja del sistema
def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((0, 0, width, height), fill="black")
    return image

# Crear el menú de la bandeja del sistema
def setup_tray_icon():
    icon = pystray.Icon("transparency", create_image(), "Transparency Control")

    # Función para actualizar el menú regularmente solo cuando no está abierto
    def update_menu():
        while True:
            if not icon.visible:  # Solo actualiza cuando el menú no está siendo usado
                icon.menu = pystray.Menu(
                    *get_open_windows_menu(),
                    item('Salir', lambda: icon.stop())
                )
            time.sleep(5)  # Verificar cada 5 segundos

    # Iniciar el hilo de actualización del menú
    update_thread = threading.Thread(target=update_menu)
    update_thread.daemon = True
    update_thread.start()

    icon.run()

# Manejo de teclas para cambiar la opacidad
def handle_keyboard_events():
    # Flecha abajo: hace la ventana seleccionada invisible (0% de opacidad)
    keyboard.add_hotkey('down', darken_windows)

    # Flecha arriba: restaura la opacidad de la ventana seleccionada al 100% (255)
    keyboard.add_hotkey('up', restore_windows)

    # Flecha derecha: mostrar el mensaje "Creado por"
    keyboard.add_hotkey('right', show_message)

    # Mantener el script en ejecución hasta que se presione la tecla "esc"
    keyboard.wait('esc')

# Configurar el icono de la bandeja en un hilo separado
def run_tray():
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.daemon = True
    tray_thread.start()

# Iniciar la aplicación
if __name__ == "__main__":
    # Ejecutar la bandeja del sistema
    run_tray()

    # Manejar eventos del teclado en el hilo principal
    handle_keyboard_events()
