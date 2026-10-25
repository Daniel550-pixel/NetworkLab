import ast
import os
import threading
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

NETWORKLAB_APPS = [
    ("Client", "http://127.0.0.1:8510"),
    ("Management", "http://127.0.0.1:8511"),
    ("Infrastructure API", "http://127.0.0.1:8512"),
]

def check_networklab_url(url, timeout=2):
    """Geeft ONLINE terug bij een HTTP-respons; anders OFFLINE of FOUT."""
    try:
        request = urllib.request.Request(
            url, method="GET",
            headers={"User-Agent": "NetworkLab-GUI-HealthCheck"}
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "ONLINE" if 200 <= response.status < 400 else "FOUT"
    except urllib.error.HTTPError:
        # Een HTTP-fout bewijst dat de server bereikbaar is.
        return "ONLINE"
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return "OFFLINE"
    except Exception:
        return "FOUT"

def open_networklab_status_window(parent):
    """Opent een apart venster zonder bestaande WiFi-functionaliteit te wijzigen."""
    window = tk.Toplevel(parent)
    window.title("NetworkLab — Webappstatus")
    window.geometry("760x300")
    window.minsize(650, 250)

    ttk.Label(
        window, text="NetworkLab — Webappstatus",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=14, pady=(14, 8))

    ttk.Label(
        window,
        text="Lokale HTTP-bereikbaarheid; dit is geen volledige gezondheidstest."
    ).pack(anchor="w", padx=14, pady=(0, 10))

    table = ttk.Frame(window)
    table.pack(fill="both", expand=True, padx=14)

    for col, heading in enumerate(("Webapp", "URL", "Status", "Actie")):
        ttk.Label(table, text=heading, font=("Segoe UI", 9, "bold")).grid(
            row=0, column=col, sticky="w", padx=5, pady=4
        )

    status_vars = []
    for row, (name, url) in enumerate(NETWORKLAB_APPS, start=1):
        status = tk.StringVar(value="NOG NIET GECONTROLEERD")
        status_vars.append(status)

        ttk.Label(table, text=name).grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Label(table, text=url).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        ttk.Label(table, textvariable=status).grid(
            row=row, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Button(
            table, text="Open",
            command=lambda address=url: webbrowser.open(address)
        ).grid(row=row, column=3, padx=5, pady=5)

    controls = ttk.Frame(window)
    controls.pack(fill="x", padx=14, pady=12)

    def refresh_statuses():
        refresh_button.configure(state="disabled")
        for status in status_vars:
            status.set("CONTROLEREN...")

        def worker():
            results = [
                check_networklab_url(url)
                for _, url in NETWORKLAB_APPS
            ]

            def update_gui():
                if not window.winfo_exists():
                    return
                for status, result in zip(status_vars, results):
                    status.set(result)
                refresh_button.configure(state="normal")

            try:
                window.after(0, update_gui)
            except tk.TclError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    refresh_button = ttk.Button(
        controls, text="Controleer verbindingen",
        command=refresh_statuses
    )
    refresh_button.pack(side="left")

    ttk.Button(
        controls, text="Sluiten", command=window.destroy
    ).pack(side="right")

    return window

def main():
    root = tk.Tk()
    root.title("NetworkLab — Webappstatus")
    root.geometry("760x300")
    open_networklab_status_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
