import ctypes
import random
import threading
import time
from tkinter import Tk, Label, PhotoImage, messagebox
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk, ImageDraw
import keyboard
import pystray
import io
import base64
import pyautogui
import requests
import config  # deine config.py

# --- Globale Variablen ---
buffer = ""
running = True
last_mouse_pos = pyautogui.position()

# --- Kek-Bild anzeigen ---
def show_random_image():
    try:
        b64_img = random.choice(config.IMAGE_B64_LIST)
        img_data = base64.b64decode(b64_img)
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
        print(f"Fehler beim Anzeigen des Bildes: {e}")

# --- Buffer aktualisieren ---
def update_buffer(c):
    global buffer
    buffer += c.lower()
    if len(buffer) > config.BUFFER_MAX:
        buffer = buffer[-config.BUFFER_MAX:]

    if "kek" in buffer:
        if random.randint(0, 99) < config.KEK_SHOW_PERCENT:
            show_random_image()
        buffer = ""

# --- Keyboard Callback ---
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

def start_hook():
    keyboard.hook(on_key_event)
    while running:
        time.sleep(0.1)

# --- Tray-App ---
def create_tray_app():
    icon_image = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(icon_image)
    d.text((10, 20), "N→M", fill='white')

    def on_exit(icon, item):
        global running
        running = False
        keyboard.unhook_all()
        icon.stop()

    menu = pystray.Menu(pystray.MenuItem('Beenden', on_exit))
    icon = pystray.Icon("NtoMModifier", icon_image, "N zu M Modifier", menu)
    threading.Thread(target=icon.run, daemon=True).start()

# --- Maus-Trolling ---
def mouse_troll_thread():
    global last_mouse_pos, running
    while running:
        time.sleep(config.MOUSE_CHECK_INTERVAL)
        current_pos = pyautogui.position()

        # Prüfen, ob Maus bewegt wurde
        if (current_pos.x, current_pos.y) != (last_mouse_pos.x, last_mouse_pos.y):
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

# --- Popup-Troll ---
def popup_troll():
    # Beim Start prüfen, ob Popup-Troll aktiviert wird
    if random.random() >= (config.POPUP_INITIAL_PROBABILITY / 100.0):
        # Nicht aktiviert → Funktion beendet sich
        print("Popup-Troll: Nicht aktiviert (Chance verpasst).")
        return

    print("Popup-Troll: Aktiviert! Es werden Popups angezeigt.")
    count = 0
    while count < config.POPUP_MAX_COUNT:
        time.sleep(config.POPUP_INTERVAL_SECONDS)
        message = random.choice(config.POPUP_MESSAGES)
        try:
            root = Tk()
            root.withdraw()
            messagebox.showinfo("Pytroll", message)
            root.destroy()
            count += 1
        except Exception as e:
            print(f"Fehler beim Anzeigen des Popups: {e}")
            break

if __name__ == "__main__":
    create_tray_app()

    threading.Thread(target=popup_troll, daemon=True).start()
    threading.Thread(target=mouse_troll_thread, daemon=True).start()
    start_hook()

    # Keep main thread alive
    while running:
        time.sleep(0.5)
