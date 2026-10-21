import logging
import os
import re
import subprocess
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

ALLOWED_IDS = {
    int(value.strip())
    for value in os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if value.strip().isdigit()
}

NETWORKLAB_URL = "http://127.0.0.1:8501/"
VBOXMANAGE = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

EXPECTED_VMS = [
    "NetworkLab-VM01-MGMT",
    "NetworkLab-VM02-INFRA",
    "NetworkLab-VM03-CLIENT",
]


def authorized(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id in ALLOWED_IDS


def get_running_vms():
    """Read the names of VMs that VirtualBox currently reports as running."""
    if not os.path.isfile(VBOXMANAGE):
        return None, f"VBoxManage niet gevonden: {VBOXMANAGE}"

    try:
        result = subprocess.run(
            [VBOXMANAGE, "list", "runningvms"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )

        if result.returncode != 0:
            detail = result.stderr.strip() or "Onbekende VirtualBox-fout"
            return None, detail

        running = set()
        for line in result.stdout.splitlines():
            match = re.match(r'^"(.+)"\s+\{', line.strip())
            if match:
                running.add(match.group(1))

        return running, None

    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f"{type(error).__name__}: {error}"


def get_web_status() -> str:
    request = Request(
        NETWORKLAB_URL,
        headers={"User-Agent": "NetworkLab-Telegram-Bridge/2.0"},
    )

    try:
        with urlopen(request, timeout=5) as response:
            return f"Webapp: BEREIKBAAR (HTTP {response.status})"
    except (URLError, HTTPError, TimeoutError, OSError) as error:
        return (
            "Webapp: NIET BEREIKBAAR\n"
            f"Fouttype: {type(error).__name__}"
        )


def get_vm_status() -> str:
    running, error = get_running_vms()

    if error:
        return (
            "VirtualBox-status: CONTROLE MISLUKT\n"
            f"Reden: {error}"
        )

    lines = ["VirtualBox-VM's:"]
    for name in EXPECTED_VMS:
        state = "ACTIEF" if name in running else "NIET ACTIEF"
        lines.append(f"- {name}: {state}")

    active_count = sum(name in running for name in EXPECTED_VMS)
    lines.append(
        f"Resultaat: {active_count}/{len(EXPECTED_VMS)} "
        "NetworkLab-VM's actief."
    )
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.effective_message.reply_text("Geen toegang.")
        return

    await update.effective_message.reply_text(
        "NetworkLab Telegram Bridge is actief.\n\n"
        "/status - Controleer webapp en VM's\n"
        "/vms - Controleer alleen de VM-statussen\n"
        "/id - Toon jouw Telegram-gebruikers-ID\n"
        "/help - Toon beschikbare commando's"
    )


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is not None:
        await update.effective_message.reply_text(
            f"Jouw Telegram-gebruikers-ID: {user.id}"
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not authorized(update):
        await update.effective_message.reply_text("Geen toegang.")
        return

    await update.effective_message.reply_text(
        "/start - Startinformatie\n"
        "/status - Controleer webapp en VM's\n"
        "/vms - Controleer alleen de VM-statussen\n"
        "/id - Toon jouw Telegram-gebruikers-ID\n"
        "/help - Toon deze uitleg"
    )


async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not authorized(update):
        await update.effective_message.reply_text("Geen toegang.")
        return

    reply = (
        "NetworkLab-status\n\n"
        + get_web_status()
        + "\n\n"
        + get_vm_status()
    )
    await update.effective_message.reply_text(reply)


async def vms(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not authorized(update):
        await update.effective_message.reply_text("Geen toegang.")
        return

    await update.effective_message.reply_text(get_vm_status())


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.effective_message.reply_text("Geen toegang.")
        return

    await update.effective_message.reply_text(
        "Bericht ontvangen. Gebruik /status of /vms."
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN ontbreekt in deze PowerShell-sessie."
        )

    if not ALLOWED_IDS:
        raise RuntimeError(
            "TELEGRAM_ALLOWED_USER_IDS ontbreekt of is ongeldig."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("vms", vms))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    )

    logging.info("NetworkLab Telegram Bridge gestart.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()