FROM python:3.10.12-slim

WORKDIR /app

COPY registro_ventas/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copiar archivos necesarios
COPY registro_ventas/templates /app/templates
COPY registro_ventas/app.py /app/app.py
COPY registro_ventas/coordenadas.py /app/coordenadas.py
COPY registro_ventas/precios.py /app/precios.py
COPY registro_ventas/preprocesamiento_sheets.py /app/preprocesamiento_sheets.py

RUN apt-get update && apt-get install -y

CMD ["gunicorn", "--bind", "0.0.0.0:5056", "app:app"]