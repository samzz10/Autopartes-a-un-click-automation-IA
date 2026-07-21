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
import threading
import schedule
import time
from remisiones import obtener_remisiones_pendientes, generar_excel
from conciliacion import get_conciliacion_handler
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde .env para mayor seguridad
ALEGRA_TOKEN     = os.getenv("ALEGRA_TOKEN")
ALEGRA_EMAIL     = os.getenv("ALEGRA_EMAIL")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
NOMBRE_EMPRESA   = "Autopartes a un click"

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
        }
        try:
            r = requests.get(url, auth=auth, params=params, timeout=30)
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
                "valor":   f"${float(f.get('balance', 0)):,.0f}",
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
        "/remisiones — ver remisiones pendientes\n"
        "/conciliacion — conciliación bancaria vs Alegra\n"
        "/start — ver este mensaje",
        parse_mode="Markdown"
    )
async def remisiones_cmd(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Consultando remisiones pendientes...")
    try:
        datos = obtener_remisiones_pendientes()
        if not datos:
            await update.message.reply_text("✅ No hay remisiones pendientes.")
            return
        excel_bytes = generar_excel(datos)
        total = sum(r["total"] for r in datos)
        num   = len(datos)
        await update.message.reply_text(
            f"📋 *Remisiones Pendientes*\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y')}  |  Último mes\n\n"
            f"🔢 Sin facturar: *{num}*\n"
            f"💰 Total: *${total:,.0f}*".replace(",", "."),
            parse_mode="Markdown"
        )
        await update.message.reply_document(
            document=excel_bytes,
            filename=f"Remisiones_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            caption="📊 Detalle completo"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def reporte_ahora(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Consultando Alegra, un momento...")
    facturas, error = await asyncio.to_thread(obtener_facturas_alegra)
    if error:
        await update.message.reply_text(f"⚠️ Error:\n{error}")
        return
    if not facturas:
        await update.message.reply_text("✅ No hay facturas vencidas.")
        return
    reporte = formatear_reporte(facturas)
    print(f"Longitud reporte: {len(reporte)} caracteres")
    if len(reporte) <= 4096:
        await update.message.reply_text(reporte, parse_mode="Markdown")
    else:
        partes = [reporte[i:i+4000] for i in range(0, len(reporte), 4000)]
        for parte in partes:
            await update.message.reply_text(parte, parse_mode="Markdown")
# ── Arrancar ─────────────────────────────────────────────────
def iniciar_scheduler():
    # El lunes a la 1pm envía el reporte de cartera
    schedule.every().monday.at("13:00").do(revisar_cartera)
    # El jueves a la 1pm envía el recordatorio
    schedule.every().thursday.at("13:00").do(recordatorio)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# 3. La función principal al final
def main():
    # Arrancar scheduler en hilo aparte (ahora Python ya sabe qué es esto)
    hilo = threading.Thread(target=iniciar_scheduler, daemon=True)
    hilo.start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reporte", reporte_ahora))
    app.add_handler(CommandHandler("remisiones", remisiones_cmd))
    app.add_handler(get_conciliacion_handler())
    print("🤖 Bot corriendo...")
    print("📅 Reporte automático: todos los lunes a la 1pm")
    print("⏰ Recordatorio: todos los jueves a la 1pm")
    
    app.run_polling()

if __name__ == "__main__":
    main()