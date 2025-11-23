# --- Chrome/Rickroll Trigger ---
# Exakter Pfad zur Chrome-Executable. Leer lassen, um Standard-Browser zu nutzen.
CHROME_EXECUTABLE = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
# Einzelne Hotkeys oder Tastenkombinationen, die Chrome mit dem Rickroll-Link starten sollen.
# Bei Kombinationen ist der letzte Wert die auslösende Taste (z.B. "ctrl+alt+r").
CHROME_TRIGGER_KEYS = ["ctrl+alt+r"]
# Tastensequenz, die Chrome ebenfalls starten darf (Reihenfolge muss genau passen).
CHROME_SEQUENCE = ["c", "h", "r", "o", "m", "e"]
# Minimale Sekunden zwischen zwei Chrome-Starts, um Spam zu vermeiden.
CHROME_TRIGGER_COOLDOWN_SECONDS = 5

