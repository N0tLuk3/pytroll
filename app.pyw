import random
import threading
import ctypes
import io
import base64
from tkinter import Tk, Label
from PIL import Image, ImageTk, ImageDraw
import keyboard
import pystray
import sys
import config
import time
import pyautogui
import random



# --- Globale Variablen ---
buffer = ""
running = True  # Stop-Flag für Keyboard-Hook

# --- Kek-Bild anzeigen ---
def show_random_image():
    try:
        b64_data = random.choice(config.IMAGE_B64_LIST)
        img_data = base64.b64decode(b64_data)
        img = Image.open(io.BytesIO(img_data))

        root = Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        tk_img = ImageTk.PhotoImage(img)
        label = Label(root, image=tk_img)
        label.image = tk_img
        label.pack()

        root.update_idletasks()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w - img.width) // 2
        y = (screen_h - img.height) // 2
        root.geometry(f"{img.width}x{img.height}+{x}+{y}")

        root.after(1500, root.destroy)
        root.mainloop()
    except Exception as e:
        pass  # Fehler ignorieren

# --- Buffer aktualisieren ---
def update_buffer(c):
    global buffer
    buffer += c.lower()
    if len(buffer) > config.BUFFER_MAX:
        buffer = buffer[-config.BUFFER_MAX:]

    if "kek" in buffer:
        if random.randint(0, 99) < config.KEK_SHOW_PERCENT:
            show_random_image()
        buffer = ""  # Puffer zurücksetzen, damit nicht sofort erneut getriggert wird

# --- Callback für Tastendruck ---
def on_key_event(event):
    global buffer
    c = event.name

    if len(c) == 1 and c.lower() == 'n':
        if random.randint(0, 99) < config.N_TO_M_PERCENT:
            shift_pressed = keyboard.is_pressed('shift')
            caps_lock = ctypes.windll.user32.GetKeyState(0x14) & 0xffff != 0
            upper = shift_pressed ^ caps_lock

            if upper:
                if not shift_pressed:
                    keyboard.press('shift')
                    keyboard.write('m')
                    keyboard.release('shift')
                else:
                    keyboard.write('M')
            else:
                keyboard.write('m')

            update_buffer('M' if upper else 'm')
            return

    update_buffer(c)

# --- Keyboard Hook starten ---
def start_hook():
    keyboard.hook(on_key_event)
    while running:
        time.sleep(0.1)  # Kurzes Sleep, nicht blockierend

# --- Maus Movement ---
last_mouse_pos = pyautogui.position()

def mouse_troll_thread():
    global last_mouse_pos, running
    while running:
        time.sleep(config.MOUSE_CHECK_INTERVAL)
        current_pos = pyautogui.position()

        # Prüfen, ob Maus bewegt wurde
        if (current_pos.x, current_pos.y) != (last_mouse_pos.x, last_mouse_pos.y):
            # Maus bewegt sich → Wahrscheinlichkeiten prüfen
            # 5% Zufallsbewegung
            if random.randint(0, 99) < config.MOUSE_RANDOM_MOVE_PERCENT:
                dx = random.choice([-1, 1]) * random.randint(*config.MOUSE_RANDOM_MOVE_RANGE)
                dy = random.choice([-1, 1]) * random.randint(*config.MOUSE_RANDOM_MOVE_RANGE)
                new_x = max(0, min(pyautogui.size().width - 1, current_pos.x + dx))
                new_y = max(0, min(pyautogui.size().height - 1, current_pos.y + dy))
                pyautogui.moveTo(new_x, new_y)

            # 1% Sprung in untere rechte Ecke
            if random.randint(0, 99) < config.MOUSE_JUMP_BOTTOMRIGHT_PERCENT:
                screen_w, screen_h = pyautogui.size()
                pyautogui.moveTo(screen_w - 1, screen_h - 1)

        last_mouse_pos = current_pos

# --- Tray-App ---
def create_tray_app():
    icon_image = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(icon_image)
    d.text((10, 20), "N→M", fill='white')

    def on_exit(icon, item):
        global running
        running = False  # Hook-Thread beenden
        keyboard.unhook_all()
        icon.stop()
        sys.exit()

    menu = pystray.Menu(pystray.MenuItem('Beenden', on_exit))
    icon = pystray.Icon("NtoMModifier", icon_image, "N zu M Modifier", menu)
    threading.Thread(target=icon.run, daemon=True).start()

# --- Main ---
if __name__ == "__main__":
    create_tray_app()

    # Keyboard-Hook Thread
    hook_thread = threading.Thread(target=start_hook, daemon=True)
    hook_thread.start()

    # Maus-Troll Thread
    mouse_thread = threading.Thread(target=mouse_troll_thread, daemon=True)
    mouse_thread.start()

    hook_thread.join()