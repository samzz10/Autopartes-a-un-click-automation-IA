# 🔧 Autopartes a un Click — Sistema de Automatización IA
 
> Sistema de automatización empresarial para **Autopartes a un Click SAS**, construido en Python con integración a Alegra, Telegram y Google APIs.
 
---
 
## 🎯 Objetivo
 
Eliminar tareas manuales y repetitivas del negocio mediante automatizaciones inteligentes que operan en tiempo real, reduciendo errores y aumentando la productividad del equipo.
 
---
 
## ⚙️ Automatizaciones implementadas
 
### 📊 Bot de Cartera (`cartera_bot.py`)
Bot de Telegram que consulta directamente la API de Alegra y genera reportes automáticos de cartera vencida.
 
- Clasificación por niveles de alerta:
  - 🟡 **Leve** — 1 día vencida
  - 🟠 **Medio** — 2 a 6 días vencida
  - 🔴 **Urgente** — más de 7 días vencida
- Reporte automático todos los **lunes a la 1pm**
- Recordatorio de seguimiento los **jueves a la 1pm**
- Comando `/reporte` para consultar en cualquier momento
- Agrupado por cliente con valor por cobrar real (descontando abonos)
### 📦 Bot de Remisiones (`remisiones.py`)
Consulta remisiones pendientes de facturar desde Alegra y genera un informe Excel profesional.
 
- Filtra remisiones abiertas del último mes
- Genera archivo `.xlsx` con formato visual por cliente
- Incluye notas internas (gestor, placa del vehículo)
- Dropdown de estado por remisión (Ya se envió correo / Por presionar)
- Comando `/remisiones` desde Telegram
### ✉️ Envío automático de cotizaciones
Automatización para el envío de cotizaciones PDF generadas en Alegra directamente al correo del cliente.
 
---
 
## 🛠️ Tecnologías
 
| Tecnología | Uso |
|---|---|
| Python 3.12+ | Lenguaje principal |
| Alegra API | Facturación, cartera y remisiones |
| python-telegram-bot | Bot de Telegram |
| openpyxl | Generación de reportes Excel |
| schedule | Automatización de tareas periódicas |
| python-dotenv | Manejo seguro de variables de entorno |
| requests | Consumo de APIs REST |
 
---
 
## 📁 Estructura del proyecto
 
```
Autopartes-a-un-click-automation-IA/
├── src/
│   ├── cartera_bot.py       # Bot principal de cartera y scheduler
│   ├── remisiones.py        # Módulo de remisiones con Excel
│   └── conciliacion.py      # Módulo de conciliación bancaria
├── data/
│   └── data/                # Archivos de datos locales
├── docs/
│   └── idea_general.md      # Documentación del proyecto
├── .env                     # Variables de entorno (no se sube a Git)
├── .gitignore
├── requirements.txt
└── README.md
```
 
---
 
## 🚀 Instalación y uso
 
### 1. Clonar el repositorio
```bash
git clone https://github.com/samzz10/Autopartes-a-un-click-automation-IA.git
cd Autopartes-a-un-click-automation-IA
```
 
### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```
 
### 3. Configurar variables de entorno
Crear un archivo `.env` en la raíz del proyecto:
```
ALEGRA_EMAIL=tu_correo@empresa.com
ALEGRA_TOKEN=tu_token_de_alegra
TELEGRAM_TOKEN=tu_token_de_telegram
CHAT_ID_PAPA=tu_chat_id
```
 
### 4. Ejecutar el bot
```bash
python src/cartera_bot.py
```
 
---
 
## 📱 Comandos disponibles en Telegram
 
| Comando | Descripción |
|---|---|
| `/start` | Ver todos los comandos disponibles |
| `/reporte` | Consultar cartera vencida ahora mismo |
| `/remisiones` | Ver remisiones pendientes de facturar |
 
---
 
## 🗓️ Automatizaciones programadas
 
| Día | Hora | Acción |
|---|---|---|
| Lunes | 1:00 PM | Reporte de cartera vencida |
| Jueves | 1:00 PM | Recordatorio de seguimiento |
 
---
 
## 👨‍💻 Autor
 
**Samuel Neira**  
Estudiante de Ingeniería de Sistemas  
Bogotá, Colombia
 
---
 
> *Este proyecto fue desarrollado para optimizar la gestión operativa y financiera de Autopartes a un Click SAS, automatizando procesos clave del negocio con inteligencia artificial y APIs modernas.*
