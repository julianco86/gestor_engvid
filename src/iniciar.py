import os
import sys
import threading
import time
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

from src.api import app

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def abrir_navegador():
    time.sleep(1.5)
    webbrowser.open(URL)


def main():
    print("=" * 52)
    print("  EngVid Learning Tracker")
    print(f"  Abriendo el navegador en {URL}")
    print("  Presiona Ctrl+C para detener el servidor")
    print("=" * 52)
    threading.Thread(target=abrir_navegador, daemon=True).start()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
