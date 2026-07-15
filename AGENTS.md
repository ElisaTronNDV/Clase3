# AGENTS.md

## Propósito
DyP LaserCore automatiza la captura de datos del archivo de corte (PDF) para generar
códigos NEST, controlar stock de chapas y dar de alta recortes sobrantes en el inventario.

## Stack
- Python 3.11
- FastAPI (backend/API)
- SQLite (base de datos)
- Angular 18 o superior (frontend)
- pdfplumber (extracción de datos del PDF)
- python-barcode (generación de código de barras)
- ZXing ngx-scanner (escaneo de código de barras)
- passlib[bcrypt] (hash de contraseñas, RNF-05)
- python-jose (JWT / sesión con expiración de 24 h, RNF-05)

## Cómo correr
Backend (puerto 8000)
```
# Configuración del entorno
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```

Frontend (Angular)
```
# Instalación de dependencias y ZXing
cd frontend
npm install

# Iniciar aplicación
ng serve
```

Pruebas
```
pytest
ng test
```

## Qué NO hacer
- No confirmar ni persistir una orden de trabajo sin que el usuario revise y valide/edite
  los datos extraídos del PDF (mitigación del riesgo de captura errónea).
- No almacenar contraseñas en texto plano; utilizar hash seguro (bcrypt/argon2) y asegurar que las API keys se lean solo de variables de entorno.
- No hardcodear el margen de tolerancia dimensional: debe leerse de la configuración (default 1.0 mm, RF-17), no quemarlo en el código.
- No implementar generación de órdenes de compra, proceso de facturacion ni generacon de remitos (fuera de alcance).
- No dar por buena la generación de un código de barras solo porque produce una imagen: verificar que decodifica con un lector independiente (ej. zbar/pyzbar) a resolución de impresión típica (≥150 DPI), no solo a resolución de pantalla. Un `module_width` por debajo de ~0.3mm, o forzar un ancho/alto de imagen que no respete la relación de aspecto real, lo vuelve ilegible aunque se vea bien en pantalla.
- Los componentes de escaneo de código de barras (ej. ZXing/ngx-scanner) traen su propio default de formato soportado (típicamente solo QR) — configurar siempre explícitamente el/los formato(s) esperado(s) (ej. CODE_128 para los códigos NEST), o el scanner nunca va a detectar nada aunque la cámara y los permisos funcionen bien.
