#!/usr/bin/env python3
"""
WiFi Profile Manager — Windows-only Tkinter utility.

Lists saved WLAN profiles using Windows' built-in netsh command and displays
profile/security details on explicit user request. Passwords are hidden by
default and are never written to disk or logs.
"""
from __future__ import annotations

import locale
import re
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional


APP_TITLE = "WiFi Profile Manager"
NETSH = ["netsh", "wlan"]


def run_netsh(args: list[str], timeout: int = 12) -> subprocess.CompletedProcess[str]:
    """Run netsh without a shell and return decoded output."""
    if __import__("os").name != "nt":
        raise RuntimeError("Deze toepassing werkt alleen op Windows.")
    return subprocess.run(
        NETSH + args,
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=timeout,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def output_text(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + (("\n" + result.stderr) if result.stderr else "")


def parse_profile_names(text: str) -> list[str]:
    """Extract profile names from common English/Dutch netsh output labels."""
    names: list[str] = []
    # netsh output is localized. Match the label before the colon instead of
    # relying on one exact English phrase.
    labels = (
        "All User Profile", "User Profile", "Alle gebruikersprofielen",
        "Gebruikersprofiel", "Alle gebruikersprofiel",
    )
    for line in text.splitlines():
        if ":" not in line:
            continue
        label, value = line.split(":", 1)
        normalized = " ".join(label.strip().casefold().split())
        if any(normalized == " ".join(x.casefold().split()) for x in labels):
            value = value.strip()
            if value and value not in names:
                names.append(value)
    return sorted(names, key=str.casefold)


def profile_summary(text: str, reveal_key: bool) -> str:
    """Hide key material unless the user explicitly chooses to reveal it."""
    lines = text.splitlines()
    result: list[str] = []
    for line in lines:
        if ":" in line:
            label, value = line.split(":", 1)
            label_norm = label.strip().casefold()
            if label_norm in {"key content", "sleutelinhoud", "sleutelinhoud"}:
                if not reveal_key:
                    line = f"{label}: [verborgen — gebruik 'Toon wachtwoord' om dit lokaal te bekijken]"
        result.append(line)
    return "\n".join(result).strip()


class WifiProfileManager(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x650")
        self.minsize(760, 500)
        self.profiles: list[str] = []
        self.selected_profile: Optional[str] = None
        self.key_revealed = False
        self._build_ui()
        self.after(150, self.refresh_profiles)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)

        heading = ttk.Label(outer, text=APP_TITLE, font=("Segoe UI", 18, "bold"))
        heading.pack(anchor="w")
        ttk.Label(
            outer,
            text="Bekijk opgeslagen wifi-profielen op deze Windows-computer. "
                 "Wachtwoorden blijven standaard verborgen.",
            wraplength=850,
        ).pack(anchor="w", pady=(3, 12))

        main = ttk.Panedwindow(outer, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main, padding=(0, 0, 10, 0))
        right = ttk.Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=3)

        ttk.Label(left, text="Opgeslagen profielen", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.profile_list = tk.Listbox(left, exportselection=False, activestyle="dotbox")
        self.profile_list.pack(fill="both", expand=True, pady=(6, 8))
        self.profile_list.bind("<<ListboxSelect>>", self._on_select)

        left_buttons = ttk.Frame(left)
        left_buttons.pack(fill="x")
        ttk.Button(left_buttons, text="Vernieuwen", command=self.refresh_profiles).pack(side="left")
        ttk.Button(left_buttons, text="Wifi-informatie", command=self.show_interfaces).pack(side="left", padx=(6, 0))

        ttk.Label(right, text="Profielgegevens", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.details = tk.Text(right, wrap="word", height=20, state="disabled", font=("Consolas", 10))
        self.details.pack(fill="both", expand=True, pady=(6, 8))
        self.details.tag_configure("warning", foreground="#9a3412")

        actions = ttk.Frame(right)
        actions.pack(fill="x")
        ttk.Button(actions, text="Details vernieuwen", command=self.inspect_selected).pack(side="left")
        self.reveal_button = ttk.Button(actions, text="Toon wachtwoord", command=self.toggle_key)
        self.reveal_button.pack(side="left", padx=(6, 0))
        ttk.Button(actions, text="Verberg wachtwoord", command=self.hide_key).pack(side="left", padx=(6, 0))
        ttk.Button(actions, text="Verwijder profiel…", command=self.delete_profile).pack(side="right")

        self.status = tk.StringVar(value="Klaar.")
        ttk.Label(outer, textvariable=self.status, relief="sunken", anchor="w", padding=5).pack(fill="x", pady=(10, 0))

        ttk.Label(
            outer,
            text="Privacy: gegevens worden alleen lokaal opgevraagd. Deze app maakt geen netwerkverbinding "
                 "en slaat geen wachtwoorden op.",
            wraplength=850,
        ).pack(anchor="w", pady=(8, 0))

    def _set_details(self, text: str, warning: bool = False) -> None:
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        if warning and text:
            self.details.tag_add("warning", "1.0", "end")
        self.details.configure(state="disabled")

    def refresh_profiles(self) -> None:
        self.status.set("Wifi-profielen ophalen…")
        try:
            result = run_netsh(["show", "profiles"])
            text = output_text(result)
            if result.returncode != 0:
                self._set_details(text or "Windows kon de wifi-profielen niet ophalen.", True)
                self.status.set(f"netsh eindigde met code {result.returncode}.")
                return
            self.profiles = parse_profile_names(text)
            self.profile_list.delete(0, "end")
            for name in self.profiles:
                self.profile_list.insert("end", name)
            if self.profiles:
                self.profile_list.selection_set(0)
                self.profile_list.event_generate("<<ListboxSelect>>")
                self.status.set(f"{len(self.profiles)} profiel(len) gevonden.")
            else:
                self.selected_profile = None
                self._set_details(
                    "Geen opgeslagen wifi-profielen gevonden.\n\n"
                    "Controleer of wifi is ingeschakeld en of Windows profielen voor deze gebruiker heeft opgeslagen."
                )
                self.status.set("Geen profielen gevonden.")
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            self._set_details(f"Fout bij ophalen van profielen:\n{exc}", True)
            self.status.set("Ophalen mislukt.")

    def _on_select(self, _event=None) -> None:
        selection = self.profile_list.curselection()
        if not selection:
            return
        self.selected_profile = self.profile_list.get(selection[0])
        self.key_revealed = False
        self.reveal_button.configure(text="Toon wachtwoord")
        self.inspect_selected()

    def inspect_selected(self) -> None:
        name = self.selected_profile
        if not name:
            messagebox.showinfo(APP_TITLE, "Selecteer eerst een wifi-profiel.")
            return
        self.key_revealed = False
        self.reveal_button.configure(text="Toon wachtwoord")
        self.status.set(f"Gegevens ophalen voor: {name}")
        try:
            result = run_netsh(["show", "profile", f"name={name}", "key=clear"])
            text = output_text(result)
            if result.returncode != 0:
                self._set_details(text or "Windows kon de profielgegevens niet ophalen.", True)
                self.status.set("Profielgegevens niet beschikbaar.")
                return
            self._set_details(profile_summary(text, reveal_key=False))
            self.status.set(f"Profiel geladen: {name}. Wachtwoord verborgen.")
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            self._set_details(f"Fout bij ophalen van profielgegevens:\n{exc}", True)
            self.status.set("Ophalen mislukt.")

    def toggle_key(self) -> None:
        if not self.selected_profile:
            messagebox.showinfo(APP_TITLE, "Selecteer eerst een wifi-profiel.")
            return
        if self.key_revealed:
            self.hide_key()
            return
        confirmed = messagebox.askyesno(
            "Wachtwoord zichtbaar maken",
            "Het opgeslagen wifi-wachtwoord kan gevoelige informatie zijn.\n\n"
            "Toon het wachtwoord tijdelijk op dit scherm?",
            icon="warning",
        )
        if not confirmed:
            return
        try:
            result = run_netsh(["show", "profile", f"name={self.selected_profile}", "key=clear"])
            text = output_text(result)
            if result.returncode != 0:
                self._set_details(text or "Windows kon de profielgegevens niet ophalen.", True)
                return
            self.key_revealed = True
            self.reveal_button.configure(text="Verberg wachtwoord")
            self._set_details(profile_summary(text, reveal_key=True))
            self.status.set("Wachtwoord tijdelijk zichtbaar. Verberg het na gebruik.")
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            messagebox.showerror(APP_TITLE, f"Kon het wachtwoord niet ophalen:\n{exc}")

    def hide_key(self) -> None:
        if self.selected_profile:
            self.inspect_selected()

    def show_interfaces(self) -> None:
        try:
            result = run_netsh(["show", "interfaces"])
            text = output_text(result)
            self._set_details(text or "Geen interface-informatie beschikbaar.")
            self.status.set("Wifi-interface-informatie weergegeven.")
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            self._set_details(f"Fout:\n{exc}", True)

    def delete_profile(self) -> None:
        name = self.selected_profile
        if not name:
            messagebox.showinfo(APP_TITLE, "Selecteer eerst een wifi-profiel.")
            return
        if not messagebox.askyesno(
            "Wifi-profiel verwijderen",
            f"Weet je zeker dat je het opgeslagen profiel '{name}' wilt verwijderen?\n\n"
            "Windows kan automatisch opnieuw verbinden met dit netwerk niet meer doen totdat het profiel opnieuw is ingesteld.",
            icon="warning",
        ):
            return
        try:
            result = run_netsh(["delete", "profile", f"name={name}"])
            text = output_text(result).strip()
            if result.returncode == 0:
                messagebox.showinfo(APP_TITLE, f"Profiel verwijderd: {name}")
                self.refresh_profiles()
            else:
                messagebox.showerror(APP_TITLE, text or "Windows kon het profiel niet verwijderen.")
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            messagebox.showerror(APP_TITLE, f"Verwijderen mislukt:\n{exc}")


if __name__ == "__main__":
    try:
        app = WifiProfileManager()
        # NetworkLab-statusvenster geïntegreerd
        from networklab_status import open_networklab_status_window
        import tkinter as _networklab_tk
        _networklab_status_button = _networklab_tk.Button(
            app,
            text='NetworkLab-webapps',
            command=lambda: open_networklab_status_window(app)
        )
        _networklab_status_button.pack(padx=8, pady=6)
        app.mainloop()
    except Exception as exc:
        messagebox.showerror(APP_TITLE, f"De toepassing kon niet starten:\n{exc}")
