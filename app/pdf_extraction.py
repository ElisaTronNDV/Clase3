import re
from io import BytesIO

import pdfplumber

_DIMENSIONS_RE = re.compile(r"Dimensiones \[mm\]\s+([\d.]+)\s*x\s*([\d.]+)")
_MULTIPLICITY_RE = re.compile(r"Multiplicidad\s+(\d+)")
_THICKNESS_RE = re.compile(r"Espesor \[mm\]\s+([\d.]+)")
_MATERIAL_RE = re.compile(r"Material\s+(\S+)")
_EXEC_TIME_RE = re.compile(r"Tiempo de ejecución estimado\s+(\d{2}:\d{2}:\d{2})")
_NEST_NAME_RE = re.compile(r"Nombre nest\s+(\S+)")

_PIECE_ROW_RE = re.compile(r"^(\d+)\s+(\d+)\s+(\S+)\s+(.+)$")
_SCRAP_ROW_RE = re.compile(r"^(\d+)\s+(\S+)\s+Saved scrap\s*$", re.IGNORECASE)
_SCRAP_DIMENSIONS_RE = re.compile(r"^(\d+(?:\.\d+)?)[xX](\d+(?:\.\d+)?)")


def _piece_table_rows(text: str) -> list[str]:
    """Isola las líneas de la tabla Ref./Cant./Pieza/Descripción, entre su
    encabezado y el pie de página, evitando el ruido de los números del
    diagrama que pdfplumber intercala en el resto del texto."""
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip().startswith("Ref. Cant.")) + 1
    except StopIteration:
        return []
    end = next(
        (i for i in range(start, len(lines)) if lines[i].strip().startswith("salvagnini")),
        len(lines),
    )
    return [line.strip() for line in lines[start:end] if line.strip()]


def _extract_pieces_and_scraps(text: str) -> tuple[list[dict], list[dict]]:
    piezas = []
    recortes = []
    for row in _piece_table_rows(text):
        piece_match = _PIECE_ROW_RE.match(row)
        if piece_match:
            _ref, cantidad, pieza, descripcion = piece_match.groups()
            piezas.append({"pieza": pieza, "descripcion": descripcion, "cantidad": int(cantidad)})
            continue

        scrap_match = _SCRAP_ROW_RE.match(row)
        if scrap_match:
            cantidad, pieza = scrap_match.groups()
            dims = _SCRAP_DIMENSIONS_RE.match(pieza)
            if dims is not None:
                recortes.append(
                    {
                        "pieza": pieza,
                        "largo_mm": float(dims.group(1)),
                        "ancho_mm": float(dims.group(2)),
                        "cantidad": int(cantidad),
                    }
                )

    return piezas, recortes


def _extract_nest(page_index: int, text: str) -> dict:
    dimensions = _DIMENSIONS_RE.search(text)
    multiplicity = _MULTIPLICITY_RE.search(text)
    thickness = _THICKNESS_RE.search(text)
    material = _MATERIAL_RE.search(text)
    exec_time = _EXEC_TIME_RE.search(text)
    nest_name = _NEST_NAME_RE.search(text)
    piezas, recortes = _extract_pieces_and_scraps(text)

    return {
        "page_index": page_index,
        "nombre_nest": nest_name.group(1) if nest_name else None,
        "multiplicidad": int(multiplicity.group(1)) if multiplicity else None,
        "largo_mm": float(dimensions.group(1)) if dimensions else None,
        "ancho_mm": float(dimensions.group(2)) if dimensions else None,
        "espesor_mm": float(thickness.group(1)) if thickness else None,
        "material": material.group(1) if material else None,
        "tiempo_ejecucion_estimado": exec_time.group(1) if exec_time else None,
        "piezas": piezas,
        "recortes": recortes,
    }


def extract_nests_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """Cada página del PDF de corte es un nest independiente (una chapa física
    distinta), con sus propios datos generales y listado de piezas."""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        return [_extract_nest(index + 1, page.extract_text() or "") for index, page in enumerate(pdf.pages)]
