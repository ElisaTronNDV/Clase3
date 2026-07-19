from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.deps import get_current_user
from app.pdf_extraction import extract_nests_from_pdf
from app.schemas import PdfExtractionResult

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_user)])


@router.post("/extract-pdf", response_model=PdfExtractionResult)
async def extract_pdf(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se admiten archivos PDF.",
        )

    content = await file.read()
    try:
        nests = extract_nests_from_pdf(content)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo leer el archivo PDF.",
        ) from exc

    return PdfExtractionResult(nests=nests)
