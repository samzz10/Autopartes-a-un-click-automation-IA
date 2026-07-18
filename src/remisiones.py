"""
Informe Automático de Remisiones Pendientes
==============================================
Se ejecuta automáticamente el día 5 de cada mes.
Consulta la API de Alegra, genera el Excel formateado
y lo envía por Telegram.
 
Requisitos:
    pip install requests openpyxl
"""
from os import replace

import requests
import base64   
import io
from datetime import datetime, date 
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from dotenv import load_dotenv
import os

load_dotenv()
ALEGRA_TOKEN     = os.getenv("ALEGRA_TOKEN")
ALEGRA_EMAIL     = os.getenv("ALEGRA_EMAIL")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
NOMBRE_EMPRESA   = os.getenv("NOMBRE_EMPRESA")

def obtener_remisiones_pendientes():
    url = "https://api.alegra.com/api/v1/remissions"
    auth = base64.b64encode(f"{ALEGRA_EMAIL}:{ALEGRA_TOKEN}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json"
    }

    hoy         = date.today()
    fecha_desde = (hoy - relativedelta(months=1)).replace(day=15)
    fecha_hasta = hoy

    print(f"📅 Buscando remisiones desde {fecha_desde.strftime('%d/%m/%Y')} hasta {fecha_hasta.strftime('%d/%m/%Y')}")

    remisiones = []
    start = 0
    batch = 30

    while True:
        params = {
            "start":           start,
            "limit":           batch,
            "order_field":     "date",
            "order_direction": "ASC",
        }
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        for rem in data:
            # Filtrar por fecha manualmente (la API ignora date_start/date_end)
            try:
                fecha_rem = datetime.strptime(rem.get("date", "")[:10], "%Y-%m-%d").date()
            except Exception:
                continue

            if fecha_rem < fecha_desde or fecha_rem > fecha_hasta:
                continue

            # Solo remisiones abiertas (open)
            if rem.get("status") != "open":
                continue

            items = [i.get("name", "") for i in rem.get("items", [])]
            remisiones.append({
                "cliente": rem.get("client", {}).get("name", ""),
                "numero":  rem.get("numberTemplate", {}).get("fullNumber", str(rem.get("id", ""))),
                "fecha":   rem.get("date", ""),
                "items":   items,
                "notas":   rem.get("anotation", "") or "",
                "total":   float(rem.get("total", 0)),
            })

        if len(data) < batch:
            break
        start += batch

    return remisiones
def generar_excel(remisiones):
    """Genera el archivo Excel formateado y retorna los bytes."""
 
    # Ordenar por cliente y luego por número de remisión
    filas = sorted(remisiones, key=lambda x: (x["cliente"], str(x["numero"])))
 
    total_general  = sum(r["total"] for r in filas)
    num_remisiones = len(filas)
    num_clientes   = len(set(r["cliente"] for r in filas))
    periodo        = datetime.now().strftime("%d/%m/%Y")
 
    # ── Estilos ──────────────────────────────────────────────
    C_NAVY   = "1A3A5C"
    C_BLUE   = "2E7DBA"
    C_WHITE  = "FFFFFF"
    C_ALT    = "EAF3FB"
    C_TOTAL  = "D6E8F5"
    C_BORDER = "B8D0E8"
 
    def fill(h): return PatternFill("solid", fgColor=h)
    thin  = Side(style="thin",   color=C_BORDER)
    thick = Side(style="medium", color=C_BLUE)
    b  = Border(left=thin,  right=thin,  top=thin,  bottom=thin)
    bH = Border(left=thick, right=thick, top=thick, bottom=thick)
 
    def sc(row, col, val, font=None, pfill=None, align=None, border=None, nfmt=None):
        c = ws.cell(row=row, column=col, value=val)
        if font:   c.font   = font
        if pfill:  c.fill   = pfill
        if align:  c.alignment = align
        if border: c.border = border
        if nfmt:   c.number_format = nfmt
        return c
 
    def ms(ref, val, font=None, pfill=None, align=None, border=None):
        c = ws[ref]
        c.value = val
        if font:   c.font   = font
        if pfill:  c.fill   = pfill
        if align:  c.alignment = align
        if border: c.border = border
        return c
 
    wb = Workbook()
    ws = wb.active
    ws.title = "Remisiones Pendientes"
 
    # Título
    ws.merge_cells("A1:G1")
    ms("A1", "INFORME DE GESTIÓN — REMISIONES PENDIENTES",
       Font(name="Arial", bold=True, size=14, color=C_WHITE),
       fill(C_NAVY), Alignment(horizontal="center", vertical="center"), bH)
    ws.row_dimensions[1].height = 32
 
    #Subtítulo 
    ws.merge_cells("A2:G2")
    ms("A2", f"Generado el {periodo}   |   Estado: Sin Facturar   |   Desde el dia 15 del mes pasado",
       Font(name="Arial", size=10, italic=True, color=C_WHITE),
       fill(C_BLUE), Alignment(horizontal="center", vertical="center"), b)
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 8
 
    #KPIs
    kpis = [
        ("A4:B4", "A5:B5", "Remisiones pendientes", str(num_remisiones)),
        ("C4:D4", "C5:D5", "Clientes afectados",    str(num_clientes)),
        ("E4:G4", "E5:G5", "Valor total pendiente",
         f"$ {total_general:,.0f}".replace(",", ".")),
    ]
    for lr, vr, label, value in kpis:
        ws.merge_cells(lr)
        ws.merge_cells(vr)
        lref = lr.split(":")[0]
        vref = vr.split(":")[0]
        ms(lref, label, Font(name="Arial", size=9, color="5A7FA0"),
           fill(C_ALT), Alignment(horizontal="center", vertical="bottom"), b)
        ms(vref, value, Font(name="Arial", bold=True, size=13, color=C_NAVY),
           fill(C_ALT), Alignment(horizontal="center", vertical="top"), b)
 
    ws.row_dimensions[4].height = 18
    ws.row_dimensions[5].height = 26
    ws.row_dimensions[6].height = 8
 
    #Encabezados
    headers = ["Cliente", "No. Remisión", "Fecha", "Ítem(s)", "Notas", "Valor Total", "Estado"]
    for col, h in enumerate(headers, 1):
        sc(7, col, h,
           Font(name="Arial", bold=True, size=10, color=C_WHITE),
           fill(C_NAVY), Alignment(horizontal="center", vertical="center", wrap_text=True), b)
    ws.row_dimensions[7].height = 22
 
    #Dropdown Estado
    dv = DataValidation(
        type="list",
        formula1='"Ya se envió correo,Por presionar"',
        allow_blank=True,
        showDropDown=False
    )
    ws.add_data_validation(dv)
 
    #Colores por cliente
    paleta = [
        ("FBEAF0", "993556"), ("E1F5EE", "0F6E56"),
        ("FAEEDA", "854F0B"), ("EAF3FB", "185FA5"),
        ("F3EEFB", "6B3FA0"), ("FEF5E7", "A0522D"),
    ]
    cliente_color = {}
    for idx, cl in enumerate(sorted(set(f["cliente"] for f in filas))):
        cliente_color[cl] = paleta[idx % len(paleta)]
 
    #Filas de datos
    DS = 8
    prev_cliente  = None
    shade_toggle  = False
 
    for i, fila in enumerate(filas):
        r = DS + i
        bg_hex, acc_hex = cliente_color.get(fila["cliente"], ("EAF3FB", "1A3A5C"))
 
        if fila["cliente"] != prev_cliente:
            shade_toggle = False
        else:
            shade_toggle = not shade_toggle
 
        if shade_toggle:
            shade_map = {
                "EAF3FB": "F8FCFF", "E1F5EE": "F5FBF8",
                "FAEEDA": "FEF9F2", "FBEAF0": "FDF5F7",
                "F3EEFB": "FAF5FD", "FEF5E7": "FFFAF3",
            }
            bg_hex = shade_map.get(bg_hex, bg_hex)
 
        prev_cliente = fila["cliente"]
        bg = fill(bg_hex)
 
        items_str = " / ".join(fila["items"]) if fila["items"] else ""
 
        # Detectar remisiones rezagadas (> 30 días)
        try:
            fecha_obj   = datetime.strptime(fila["fecha"][:10], "%Y-%m-%d").date()
            es_rezagada = (date.today() - fecha_obj).days > 30
            fecha_display = fecha_obj.strftime("%d/%m/%Y")
        except Exception:
            es_rezagada   = False
            fecha_display = fila.get("fecha", "")
 
        sc(r, 1, fila["cliente"],
           Font(name="Arial", size=9, bold=True, color=acc_hex),
           bg, Alignment(vertical="center", wrap_text=True), b)
        sc(r, 2, fila["numero"],
           Font(name="Arial", size=9, bold=True, color=C_NAVY),
           bg, Alignment(horizontal="center", vertical="center"), b)
        sc(r, 3, fecha_display,
           Font(name="Arial", size=9, bold=True, color="C05000") if es_rezagada
           else Font(name="Arial", size=9, color="555555"),
           bg, Alignment(horizontal="center", vertical="center"), b)
        sc(r, 4, items_str,
           Font(name="Arial", size=9),
           bg, Alignment(vertical="center", wrap_text=True), b)
        sc(r, 5, fila["notas"],
           Font(name="Arial", size=9, color="555555"),
           bg, Alignment(vertical="center", wrap_text=True), b)
        sc(r, 6, fila["total"],
           Font(name="Arial", size=9, bold=True, color=C_NAVY),
           bg, Alignment(horizontal="right", vertical="center"), b, '"$ "#,##0')
 
        ec = ws.cell(row=r, column=7, value="")
        ec.fill      = bg
        ec.border    = b
        ec.font      = Font(name="Arial", size=9, bold=True)
        ec.alignment = Alignment(horizontal="center", vertical="center")
        dv.add(ec)
        ws.row_dimensions[r].height = 38
 
    #Fila Total
    TR = DS + len(filas)
    ws.merge_cells(f"A{TR}:E{TR}")
    ms(f"A{TR}", "TOTAL GENERAL",
       Font(name="Arial", bold=True, size=10, color=C_NAVY),
       fill(C_TOTAL), Alignment(horizontal="right", vertical="center"), b)
    sc(TR, 6, f"=SUM(F{DS}:F{TR-1})",
       Font(name="Arial", bold=True, size=10, color=C_NAVY),
       fill(C_TOTAL), Alignment(horizontal="right", vertical="center"), b, '"$ "#,##0')
    sc(TR, 7, "",
       Font(name="Arial", size=9), fill(C_TOTAL),
       Alignment(horizontal="center", vertical="center"), b)
    ws.row_dimensions[TR].height = 22
 
    # Anchos de columna
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 13
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 38
    ws.column_dimensions["E"].width = 48
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 22
 
    ws.freeze_panes      = "A8"
    ws.print_title_rows  = "1:7"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage   = True
    ws.page_setup.fitToWidth  = 1
 
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
 
 
def enviar_telegram(excel_bytes, num_remisiones, total):
    """Envía el mensaje de resumen y el Excel adjunto por Telegram."""
    fecha     = datetime.now().strftime("%d/%m/%Y")
    total_fmt = f"${total:,.0f}".replace(",", ".")
 
    mensaje = (
        f"📋 *Informe de Remisiones Pendientes*\n"
        f"📅 Fecha: {fecha}\n\n"
        f"🔢 Remisiones sin facturar: *{num_remisiones}*\n"
        f"💰 Valor total pendiente: *{total_fmt}*\n\n"
        f"Adjunto el archivo Excel con el detalle completo."
    )
 
    url_msg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url_msg, data={
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       mensaje,
        "parse_mode": "Markdown"
    }, timeout=30)
 
    nombre_archivo = f"Remisiones_Pendientes_{datetime.now().strftime('%Y_%m_%d')}.xlsx"
    url_doc = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    requests.post(url_doc, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": "📊 Informe de remisiones pendientes"
    }, files={
        "document": (nombre_archivo, excel_bytes,
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }, timeout=60)
 
    print(f"✅ Informe enviado el {fecha}")
 
 
def main():
    print("🔄 Consultando remisiones en Alegra...")
    remisiones = obtener_remisiones_pendientes()
 
    if not remisiones:
        print("✅ No hay remisiones pendientes.")
        url_msg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url_msg, data={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       "✅ *Informe del día 5*\n\nNo hay remisiones pendientes por facturar.",
            "parse_mode": "Markdown"
        }, timeout=30)
        return
 
    print(f"📦 {len(remisiones)} remisiones encontradas. Generando Excel...")
    excel_bytes = generar_excel(remisiones)
 
    total = sum(r["total"] for r in remisiones)
    num   = len(remisiones)
 
    print("📤 Enviando por Telegram...")
    enviar_telegram(excel_bytes, num, total)
 
 
if __name__ == "__main__":
    main()

                    
                     

