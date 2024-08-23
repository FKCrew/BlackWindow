import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import pygetwindow as gw
import ctypes
import threading
import keyboard
import time

# Variable global para almacenar la ventana seleccionada
selected_window = None

# Lista de títulos de ventanas a excluir
excluded_windows = ['Microsoft Text Input Application', 'Setup', 'Calculator', 
                    'Program Manager', 'Windows Shell Experience Host', 'Settings']

# Función para cambiar la opacidad de una ventana
def set_window_opacity(hwnd, opacity):
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, opacity, 0x2)

# Función para oscurecer la ventana seleccionada
def darken_window():
    global selected_window
    if selected_window:
        windows = gw.getWindowsWithTitle(selected_window)
        if windows:
            hwnd = windows[0]._hWnd
            set_window_opacity(hwnd, 0)  # 0% de opacidad

# Función para restaurar la opacidad de la ventana seleccionada
def restore_window():
    global selected_window
    if selected_window:
        windows = gw.getWindowsWithTitle(selected_window)
        if windows:
            hwnd = windows[0]._hWnd
            set_window_opacity(hwnd, 255)  # 100% de opacidad

# Función que crea un item del menú para cada ventana
def create_menu_item(window_title):
    return item(window_title, lambda: select_window(window_title))

# Función para seleccionar la ventana desde el menú
def select_window(window_title):
    global selected_window
    selected_window = window_title

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
    icon = pystray.Icon("transparency", create_image(), "Black Window")

    # Función para actualizar el menú regularmente
    def update_menu():
        while True:
            icon.menu = pystray.Menu(
                *get_open_windows_menu(),
                item('Salir', lambda: icon.stop())
            )
            icon.update_menu()
            time.sleep(5)  # Actualizar cada 5 segundos

    # Iniciar el hilo de actualización del menú
    update_thread = threading.Thread(target=update_menu)
    update_thread.daemon = True
    update_thread.start()

    icon.run()

# Manejo de teclas para cambiar la opacidad
def handle_keyboard_events():
    # Flecha abajo: hace la ventana seleccionada opaca
    keyboard.add_hotkey('down', darken_window)

    # Flecha arriba: restaura la opacidad de la ventana seleccionada
    keyboard.add_hotkey('up', restore_window)

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
