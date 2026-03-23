import logging
import requests
import pandas as pd
from datetime import datetime, date
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import threading
import asyncio

ALEGRA_TOKEN     = "0d9e3617130df4ec9b11"
ALEGRA_EMAIL     = "autopartesaunclickcol@gmail.com"
TELEGRAM_TOKEN   = "8619419567:AAHS07uaZSrCOhVGjECF3azU1U1XLnaFyV8"
CHAT_ID_PAPA     = 8492722057
EMAIL_EMPRESA    = "autopartesaunclickcol@gmail.com"
PASSWORD_APP     = "vijq vxzb naos ifld"  # Contraseña de aplicación Gmail
NOMBRE_EMPRESA   = "Autopartes a un Click"

# Mensajes según nivel de alerta
MENSAJES = {
    "suave": {
        "asunto": "Recordatorio de pago — Factura vencida",
        "cuerpo": """\
Estimado/a {nombre},

Le informamos que la factura {numero} por valor de {valor} venció hace {dias} día(s).

Le agradecemos gestionar el pago a la mayor brevedad posible.

Quedamos atentos,

Recuerda.. Buscas. clickeas, solucionas.

Equipo {empresa}"""
    },
    "importante": {
        "asunto": "Aviso importante — Factura pendiente de pago",
        "cuerpo": """\
Estimado/a {nombre},

Le recordamos que la factura {numero} por valor de {valor} lleva {dias} días vencida.

Es importante regularizar este pago para evitar inconvenientes.

Quedamos atentos,

Recuerda.. Buscas. clickeas, solucionas.

Equipo {empresa}"""
    },
    "urgente": {
        "asunto": "URGENTE — Factura con mora",
        "cuerpo": """\
Estimado/a {nombre},

La factura {numero} por valor de {valor} lleva {dias} días vencida sin regularizar.

Solicitamos gestionar el pago de inmediato.

Recuerda.. Buscas. clickeas, solucionas.

Equipo {empresa}"""
    }
}
# ============================================================

# Configuración del logging