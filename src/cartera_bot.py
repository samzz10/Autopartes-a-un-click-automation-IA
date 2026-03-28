import logging
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio

ALEGRA_TOKEN     = "0d9e3617130df4ec9b11"
ALEGRA_EMAIL     = "autopartesaunclickcol@gmail.com"
TELEGRAM_TOKEN   = "8619419567:AAHS07uaZSrCOhVGjECF3azU1U1XLnaFyV8"
CHAT_ID_PAPA     = 8492722057
EMAIL_EMPRESA    = "autopartesaunclickcol@gmail.com"
PASSWORD_APP     = "vijq vxzb naos ifld"  # Contraseña de aplicación Gmail
NOMBRE_EMPRESA   = "Autopartes a un Click"

# Mensajes según nivel de alerta
def obtener_nivel(dias):
    if dias <= 1:
        return "leve"
    elif 2 <= dias <= 6:
        return "medio"
    elif dias > 7:
        return "urgente"
    return None

def obtener_facturas_alegra():
    url   = "https://api.alegra.com/api/v1/invoices"
    auth  = (ALEGRA_EMAIL, ALEGRA_TOKEN)
    hoy   = date.today()
    todas = []
    start = 0

    while True:
        params = {
            "status": "open",
            "limit":  30,
            "start":  start,
            "fields": "id,numberTemplate,dueDate,status,client,total"
        }
        try:
            r = requests.get(url, auth=auth, params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return [], f"Error consultando Alegra: {e}"

        if not data:
            break
        todas.extend(data)
        if len(data) < 30:
            break
        start += 30

    resultado = []
    for f in todas:
        try:
            due  = datetime.strptime(f["dueDate"], "%Y-%m-%d").date()
            dias = (hoy - due).days
            if dias < 1:
                continue
            nivel = obtener_nivel(dias)
            if not nivel:
                continue
            resultado.append({
                "numero":  f.get("numberTemplate", {}).get("fullNumber", "—"),
                "cliente": f.get("client", {}).get("name", "—"),
                "valor":   f"${float(f.get('total', 0)):,.0f}",
                "dias":    dias,
                "nivel":   nivel
            })
        except Exception:
            continue

    return resultado, None
def formatear_reporte(facturas):
    hoy    = date.today().strftime("%d/%m/%Y")
    iconos = {"leve": "🟡", "medio": "🟠", "urgente": "🔴"}

    # Agrupar por cliente
    clientes = {}
    for f in facturas:
        nombre = f["cliente"]
        if nombre not in clientes:
            clientes[nombre] = []
        clientes[nombre].append(f)

    lineas = [f"📊 *Reporte de cartera — {hoy}*\n"]

    for cliente, lista in sorted(clientes.items()):
        lineas.append(f"👤 *{cliente}*")
        for f in sorted(lista, key=lambda x: x["dias"], reverse=True):
            icono = iconos[f["nivel"]]
            lineas.append(
                f"  {icono} #{f['numero']} · {f['dias']} días · {f['valor']}"
            )
        lineas.append("")

    total   = len(facturas)
    leve    = sum(1 for f in facturas if f["nivel"] == "leve")
    medio   = sum(1 for f in facturas if f["nivel"] == "medio")
    urgente = sum(1 for f in facturas if f["nivel"] == "urgente")

    lineas.append(
        f"📌 *Total:* {total} facturas vencidas\n"
        f"🟡 Leve: {leve} · 🟠 Medio: {medio} · 🔴 Urgente: {urgente}"
    )
    return "\n".join(lineas)

async def enviar_telegram(mensaje):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID_PAPA,
        text=mensaje,
        parse_mode="Markdown"
    )
def revisar_cartera():
    print("Consultando cartera...")
    facturas, error = obtener_facturas_alegra()

    if error:
        asyncio.run(enviar_telegram(
            f"⚠️ *Error al obtener facturas:*\n{error}"))
        return 
    if not facturas:
        asyncio.run(enviar_telegram(
            "✅ *Reporte de cartera*\n\nNo hay facturasvencidas en los ultimos 6 meses."))
        return
    
    reporte = formatear_reporte(facturas)
    asyncio.run(enviar_telegram(reporte))
    print("Reporte enviado a Telegram.")

def recordatorio():
    asyncio.run(enviar_telegram(
        "⏰ *Seguimiento de cartera*\n\n."
        "Hace 3 días se envió el reporte de facturas vencidas.\n"
        "¿Cómo va el cobro con los clientes?"
    ))

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Soy el bot de cartera de *Autopartes a un Clic*.\n\n"
        "Comandos:\n"
        "/reporte — consultar cartera ahora\n"
        "/start — ver este mensaje",
        parse_mode="Markdown"
    )

async def reporte_ahora(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Consultando Alegra, un momento...")
    await asyncio.to_thread(revisar_cartera)

# ── Arrancar ─────────────────────────────────────────────────
def main():

      # Arrancar scheduler en hilo aparte
    hilo = threading.Thread(target=iniciar_scheduler, daemon=True)
    hilo.start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reporte", reporte_ahora))
    print("🤖 Bot corriendo...")
    print("📅 Reporte automático: todos los lunes a la 1pm")
    print("⏰ Recordatorio: todos los jueves a la 1pm")
    app.run_polling()

import threading
import schedule
import time

def iniciar_scheduler():
    schedule.every().monday.at("13:00").do(revisar_cartera)
    schedule.every().thursday.at("13:00").do(recordatorio)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
