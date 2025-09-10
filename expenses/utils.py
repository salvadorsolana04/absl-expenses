from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.utils.text import slugify

HEADERS = [
    'ID','Fecha','Categoría','Proveedor','Descripción','Monto','Medio de pago','Código/Obra','Notas','Recibos (links)'
]

COL_WIDTHS = [6,12,18,24,36,12,16,16,24,30]

def build_export(expenses_qs):
    # 1) Excel in-memory
    wb = Workbook()
    ws = wb.active
    ws.title = 'Gastos'

    ws.append(HEADERS)
    for i, w in enumerate(COL_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    rows = []
    for e in expenses_qs.select_related().prefetch_related('receipts').order_by('date','id'):
        links = []
        for r in e.receipts.all():
            fname = r.export_filename()
            links.append(f'=HYPERLINK("receipts/{fname}", "{fname}")')
        link_cell = ", ".join(links) if links else ''
        rows.append([
            e.id, e.date.isoformat(), e.category, e.vendor, e.description,
            float(e.amount), e.payment_method, e.project_code, e.notes, link_cell
        ])

    for row in rows:
        ws.append(row)

    out_xlsx = BytesIO()
    wb.save(out_xlsx)
    out_xlsx.seek(0)

    # 2) ZIP with excel + receipts
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as zf:
        zf.writestr('expenses.xlsx', out_xlsx.getvalue())
        for e in expenses_qs.prefetch_related('receipts'):
            for r in e.receipts.all():
                arcname = f"receipts/{r.export_filename()}"
                with r.image.open('rb') as f:
                    zf.writestr(arcname, f.read())
    zip_buffer.seek(0)
    return zip_buffer
