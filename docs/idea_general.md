# 💡 Idea General — Autopartes a un Click Automation IA

## Contexto

**Autopartes a un Click SAS** es una empresa familiar colombiana dedicada a la venta de repuestos automotrices, que opera principalmente a través de WhatsApp y correo electrónico, atendiendo talleres, rentadoras y gestores de flotas vehiculares.

Este proyecto nace de la necesidad de modernizar y automatizar los procesos operativos del negocio, reduciendo el tiempo dedicado a tareas repetitivas y minimizando errores humanos, permitiendo que el equipo se enfoque en lo que realmente importa: vender y atender clientes.

---

## 🎯 Objetivo General

Construir un ecosistema de automatización inteligente para **Autopartes a un Click SAS**, integrando APIs modernas, inteligencia artificial y bots conversacionales que operen de forma autónoma y en tiempo real.

---

## ⚙️ Procesos a automatizar

### ✅ Fase 1 — Completada
**Bot de cartera y remisiones**
- Consulta automática de facturas vencidas desde Alegra
- Clasificación por niveles de alerta (leve, medio, urgente)
- Reporte semanal automático por Telegram al gerente
- Informe de remisiones pendientes en Excel profesional
- Comandos `/reporte` y `/remisiones` disponibles 24/7

### 🔄 Fase 2 — En desarrollo
**Envío automático de cotizaciones**
- Lectura de PDF de cotizaciones generadas en Alegra
- Detección automática del cliente y gestor destinatario
- Envío directo al correo del cliente con plantillas personalizadas
- Integración con hilo de correo existente (Reply All)

### 📋 Fase 3 — Planificada
**Automatización de prospección**
- Identificación de nuevos clientes desde Cámara de Comercio
- Cruce con base de datos existente en Alegra
- Envío automatizado de correos de prospección
- Flujo de aprobación manual antes del envío (cumplimiento Ley 1581)

### 📊 Fase 4 — Planificada
**Reportes automáticos de ventas y análisis de datos**
- Dashboard de ventas por cliente, producto y período
- Análisis de tendencias y productos más vendidos
- Alertas de clientes inactivos
- Exportación automática a Excel y Telegram

### 🤖 Fase 5 — Visión a largo plazo
**Chatbot empresarial con IA**
- Atención automática de consultas por WhatsApp
- Consulta de disponibilidad de repuestos en tiempo real
- Seguimiento de pedidos y cotizaciones
- Integración con Alegra para generación de documentos

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| ERP / Facturación | Alegra API |
| Mensajería | Telegram Bot API |
| Reportes | openpyxl, pandas |
| Correo | Gmail API |
| Automatización | schedule, N8N |
| IA | Anthropic Claude API |
| Despliegue | Railway / Local |
| Control de versiones | GitHub |

---

## 🗓️ Hoja de ruta

| Período | Meta |
|---|---|
| 2025 — 2026 | Fases 1 y 2 — Cartera, remisiones y cotizaciones |
| 2026 — 2027 | Fases 3 y 4 — Prospección y análisis de datos |
| 2027 — 2028 | Fase 5 — Chatbot con IA y expansión del sistema |

---

## 👨‍💻 Sobre el autor

**Samuel Neira**  
Estudiante de Ingeniería de Sistemas — Bogotá, Colombia  

Este proyecto representa la intersección entre mi formación académica y la operación real de un negocio familiar. Cada automatización implementada resuelve un problema concreto del día a día de la empresa, y a la vez me permite aplicar y profundizar conocimientos en Python, APIs, bases de datos e inteligencia artificial.

El objetivo a largo plazo es que este sistema sirva como base para un **startup de automatización empresarial** orientado a pequeñas y medianas empresas en Colombia.

---

> *"La mejor forma de aprender a programar es resolviendo problemas reales."*