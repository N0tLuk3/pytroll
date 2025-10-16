import ctypes
import random
import threading
import time
from tkinter import Tk, Label, PhotoImage
import keyboard  # pip install keyboard
from PIL import Image, ImageTk  # pip install pillow

# --- Globale Variablen ---
buffer = ""
BUFFER_MAX = 50

# --- Funktion zum Anzeigen des Kek-Bildes ---
def show_kek_image():
    try:
        root = Tk()
        root.overrideredirect(True)  # Kein Fensterrahmen
        root.attributes("-topmost", True)

        img = Image.open("kek.png")  # Stelle sicher, dass kek.png im gleichen Ordner ist
        tk_img = ImageTk.PhotoImage(img)
        label = Label(root, image=tk_img)
        label.pack()

        # Fenster zentrieren
        root.update_idletasks()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        x = (w - img.width) // 2
        y = (h - img.height) // 2
        root.geometry(f"{img.width}x{img.height}+{x}+{y}")

        # Timer, um das Bild nach 1,5 Sekunden zu schließen
        root.after(1500, root.destroy)
        root.mainloop()
    except Exception as e:
        print(f"Fehler beim Anzeigen des Bildes: {e}")

# --- Buffer aktualisieren ---
def update_buffer(c):
    global buffer
    buffer += c.lower()
    if len(buffer) > BUFFER_MAX:
        buffer = buffer[-BUFFER_MAX:]
    if "kek" in buffer:
        show_kek_image()
        buffer = ""

# --- Callback für Tastendruck ---
def on_key_event(event):
    global buffer
    c = event.name

    if len(c) == 1 and c.lower() == 'n':
        if random.randint(0, 99) < 5:
            shift_pressed = keyboard.is_pressed('shift')
            caps_lock = ctypes.windll.user32.GetKeyState(0x14) & 0xffff != 0
            upper = shift_pressed ^ caps_lock
            c = 'M' if upper else 'm'
            keyboard.write(c)
            update_buffer(c)
            return  # Event "verbraucht"
    
    update_buffer(c)

# --- Keyboard Hook starten ---
def start_hook():
    keyboard.on_press(on_key_event)
    keyboard.wait()  # Blockiert, bis das Programm beendet wird

# --- Tray-App (Windows) ---
def create_tray_app():
    import pystray
    from PIL import ImageDraw

    # Einfaches Icon erstellen
    icon_image = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(icon_image)
    d.text((10, 20), "N→M", fill='white')

    def on_exit(icon, item):
        icon.stop()
        keyboard.unhook_all()

    menu = pystray.Menu(pystray.MenuItem('Beenden', on_exit))
    icon = pystray.Icon("NtoMModifier", icon_image, "N zu M Modifier", menu)
    threading.Thread(target=icon.run, daemon=True).start()

# --- Main ---
if __name__ == "__main__":
    create_tray_app()
    start_hook()
