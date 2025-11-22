import base64
import ctypes
import io
import os
import random
import threading
import time
import webbrowser
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import Tk, Label

import keyboard
import pyautogui
import pystray
from PIL import Image, ImageDraw, ImageTk
import winsound

import config
from config import *
from sound_player import schedule_test_sound


# --- Globale Variablen ---
buffer = ""
running = True
last_mouse_pos = pyautogui.position()
last_rickroll_trigger = 0.0

YOUTUBE_KEYWORDS = (
    "youtube.com",
    "youtu.be",
    "youtube",
)
RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
RICKROLL_COOLDOWN_SECONDS = 30

# --- Globale Variablen für Sound ---
sound_probability = 100.0  # Startwahrscheinlichkeit in %
sound_interval = 1 * 6  # 10 Minuten in Sekunden


# --- Kek-Bild anzeigen ---
def show_random_image():
    """Zeigt eines der in config definierten Base64-Bilder als zentriertes Popup."""
    try:
        b64_img = random.choice(config.IMAGE_B64_LIST)
        img_data = base64.b64decode(b64_img)
        img = Image.open(io.BytesIO(img_data))

        root = Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=tk_img)
        label._img_ref = tk_img     # type: ignore
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
    """Aktualisiert den Eingabepuffer und prüft auf 'kek'."""
    global buffer
    buffer += c.lower()
    if len(buffer) > config.BUFFER_MAX:
        buffer = buffer[-config.BUFFER_MAX:]

    if "kek" in buffer:
        if random.randint(0, 99) < config.KEK_SHOW_PERCENT:
            show_random_image()
        buffer = ""

    maybe_redirect_youtube()


def maybe_redirect_youtube():
    """Öffnet automatisch den Rickroll-Link, wenn YouTube getippt wird."""
    global buffer, last_rickroll_trigger
    lower_buffer = buffer.lower()

    if not any(keyword in lower_buffer for keyword in YOUTUBE_KEYWORDS):
        return

    now = time.time()
    if now - last_rickroll_trigger < RICKROLL_COOLDOWN_SECONDS:
        return

    try:
        webbrowser.open(RICKROLL_URL, new=2)
        last_rickroll_trigger = now
        buffer = ""
        print("[INFO] YouTube-Aufruf erkannt – Rickroll geöffnet.")
    except Exception as exc:
        print(f"[ERROR] Konnte Rickroll nicht öffnen: {exc}")


# --- Keyboard Callback ---
def on_key_event(event):
    """Intercepted Key Events: ersetzt 'n' zufällig durch 'm'."""
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
    """Startet Keyboard-Hook."""
    keyboard.hook(on_key_event)
    while running:
        time.sleep(0.1)


# --- Tray-App ---
def create_tray_app():
    """Erstellt Tray-Icon mit Beenden-Option."""
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
    """Bewegt die Maus zufällig oder springt in die Ecke."""
    global last_mouse_pos, running
    while running:
        time.sleep(config.MOUSE_CHECK_INTERVAL)
        current_pos = pyautogui.position()

        if (current_pos.x, current_pos.y) != (last_mouse_pos.x, last_mouse_pos.y):
            if random.randint(0, 99) < config.MOUSE_RANDOM_MOVE_PERCENT:
                dx = random.choice([-1, 1]) * random.randint(*config.MOUSE_RANDOM_MOVE_RANGE)
                dy = random.choice([-1, 1]) * random.randint(*config.MOUSE_RANDOM_MOVE_RANGE)
                new_x = max(0, min(pyautogui.size().width - 1, current_pos.x + dx))
                new_y = max(0, min(pyautogui.size().height - 1, current_pos.y + dy))
                pyautogui.moveTo(new_x, new_y)

            if random.randint(0, 99) < config.MOUSE_JUMP_BOTTOMRIGHT_PERCENT:
                screen_w, screen_h = pyautogui.size()
                pyautogui.moveTo(screen_w - 1, screen_h - 1)

        last_mouse_pos = current_pos


# --- Popup-Troll ---
def popup_troll():
    """Zeigt nach Zufallsintervall Popup-Meldungen."""
    print("Popup-Troll: Warte 10 Minuten vor Start...")
    time.sleep(6)

    if random.random() >= (config.POPUP_INITIAL_PROBABILITY / 100.0):
        print("Popup-Troll: Nicht aktiviert (Chance verpasst).")
        return

    print("Popup-Troll: Aktiviert! Es werden Popups angezeigt.")
    count = 0

    while count < config.POPUP_MAX_COUNT and running:
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

def play_sound_if_triggered():
    """Prüft in Intervallen, ob Sound abgespielt werden soll, und passt Wahrscheinlichkeit an."""
    global sound_probability, sound_interval
    while running:
        roll = random.uniform(0, 100)
        print(
            f"[DEBUG] Warte {sound_interval/60:.0f} min | "
            f"Chance: {sound_probability:.2f}% | Roll: {roll:.2f}"
        )
        time.sleep(sound_interval)

        if not running:
            break

        if roll < sound_probability:
            print("[INFO] Sound wird abgespielt!")
            play_sound()
        else:
            sound_probability = min(100, sound_probability * 2)
            sound_interval = 20 * 60 if sound_probability < 30 else 10 * 60


def play_sound():
    """Dekodiert und spielt den Base64-kodierten Sound aus der config."""
    try:
        sound_data = base64.b64decode(SOUND_B64)
        temp_file = "temp_sound.wav"
        with open(temp_file, "wb") as f:
            f.write(sound_data)
        winsound.PlaySound(temp_file, winsound.SND_FILENAME)
        os.remove(temp_file)
    except Exception as e:
        print(f"[ERROR] Konnte Sound nicht abspielen: {e}")
            
                    
# --- Main ---
if __name__ == "__main__":
    create_tray_app()
    

    threading.Thread(target=popup_troll, daemon=True).start()
    threading.Thread(target=mouse_troll_thread, daemon=True).start()
    threading.Thread(target=start_hook, daemon=True).start()
    threading.Thread(target=play_sound_if_triggered, daemon=True).start()

    # GUI Hauptloop (leeres Fenster vermeiden)
    tk_root = tk.Tk()
    tk_root.withdraw()  # Kein Hauptfenster anzeigen
    tk_root.mainloop()

    print("✅ Pytroll gestartet. Tray-Icon verfügbar.")
    while running:
        time.sleep(0.5)
