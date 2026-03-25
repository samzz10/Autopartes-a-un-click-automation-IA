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
def obtener_nivel(dias):
    if dias <= 1:
        return "leve"
    elif 2 <= dias <= 6:
        return "medio"
    else:
        return "urgente"
# ============================================================

# Configuración del logging