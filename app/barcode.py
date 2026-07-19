from io import BytesIO

import barcode as barcode_lib
from barcode.writer import ImageWriter
from PIL import Image
from pyzbar.pyzbar import decode as zbar_decode

# El default de python-barcode (0.2mm) queda por debajo del piso legible a
# resolución de impresión estándar; RNF-06 exige >= 0.3mm.
_MODULE_WIDTH_MM = 0.33
_WRITER_OPTIONS = {
    "module_width": _MODULE_WIDTH_MM,
    "module_height": 15.0,
    "quiet_zone": 6.5,
    "dpi": 300,
    "write_text": True,
}


def generate_barcode_png(nest_code: str) -> bytes:
    code128 = barcode_lib.get("code128", nest_code, writer=ImageWriter())
    buffer = BytesIO()
    code128.write(buffer, options=_WRITER_OPTIONS)
    png_bytes = buffer.getvalue()
    _verify_decodable(png_bytes, nest_code)
    return png_bytes


def _verify_decodable(png_bytes: bytes, expected_value: str) -> None:
    """No alcanza con que la imagen se genere: hay que confirmar que un
    lector independiente (pyzbar/zbar) la decodifica de vuelta al valor
    original, a la resolución de impresión configurada arriba."""
    image = Image.open(BytesIO(png_bytes))
    decoded_values = [result.data.decode("utf-8") for result in zbar_decode(image)]
    if expected_value not in decoded_values:
        raise ValueError(
            f"El código de barras generado para '{expected_value}' no es decodificable "
            f"por un lector independiente (valores leídos: {decoded_values})."
        )
