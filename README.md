# ABSL Expenses (Django)

Rails vibes con Django: CRUD de gastos, subida de múltiples recibos, export ZIP (Excel + imágenes) con hipervínculos relativos para ver cada recibo desde el Excel.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrí `http://127.0.0.1:8000/` para cargar gastos. Ver listado en `/gastos/`. Exportar en `/export/zip/`.

### Admin
```bash
python manage.py createsuperuser
```
Admin en `/admin/` para editar.

## Export
- Genera `absl-expenses-export.zip` con:
  - `expenses.xlsx`
  - carpeta `receipts/` con imágenes renombradas: `EXP-<id>-<proveedor>.ext`
- El Excel usa `HYPERLINK("receipts/archivo", "archivo")` (funciona al abrir el ZIP descomprimido).

## Notas
- Producción: configurá `DEBUG=False`, `ALLOWED_HOSTS`, almacenamiento de media (S3/GCS) y base de datos.
- Logo: reemplazá `static/img/absl-logo.png`.
