from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.barcode import generate_barcode_png
from app.database import get_db
from app.deps import get_current_user
from app.models import Product, WorkOrder, WorkOrderPiece, WorkOrderScrap
from app.pdf_extraction import extract_nests_from_pdf
from app.schemas import PdfExtractionResult, WorkOrderCreate, WorkOrderOut, WorkOrderSummaryOut
from app.system_config import get_or_create_system_config

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


def _get_order_or_404(db: Session, order_id: int) -> WorkOrder:
    work_order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de trabajo no encontrada")
    return work_order


def _with_low_stock_warning(db: Session, work_order: WorkOrder) -> WorkOrder:
    product = db.query(Product).filter(Product.id == work_order.product_id).first()
    work_order.low_stock_warning = (product.stock - product.committed_stock) <= product.reorder_point
    return work_order


def _find_matching_product(
    db: Session, material: str, thickness_mm: float, length_mm: float, width_mm: float, tolerance_mm: float
) -> Product | None:
    candidates = (
        db.query(Product).filter(Product.material == material, Product.thickness_mm == thickness_mm).all()
    )
    for product in candidates:
        if abs(product.length_mm - length_mm) <= tolerance_mm and abs(product.width_mm - width_mm) <= tolerance_mm:
            return product
    return None


@router.post("", response_model=WorkOrderOut, status_code=status.HTTP_201_CREATED)
def confirm_order(payload: WorkOrderCreate, db: Session = Depends(get_db)):
    config = get_or_create_system_config(db)
    product = _find_matching_product(
        db, payload.material, payload.thickness_mm, payload.length_mm, payload.width_mm, config.tolerance_mm
    )

    if product is None:
        if not payload.create_missing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "product_not_found",
                    "message": "El producto no existe en el maestro.",
                    "material": payload.material,
                    "thickness_mm": payload.thickness_mm,
                    "length_mm": payload.length_mm,
                    "width_mm": payload.width_mm,
                },
            )
        product = Product(
            material=payload.material,
            thickness_mm=payload.thickness_mm,
            length_mm=payload.length_mm,
            width_mm=payload.width_mm,
            stock=0,
            committed_stock=0,
            reorder_point=0,
        )
        db.add(product)
        db.flush()

    product.committed_stock += payload.multiplicidad

    work_order = WorkOrder(
        status="vigente",
        nombre_nest=payload.nombre_nest,
        material=payload.material,
        thickness_mm=payload.thickness_mm,
        length_mm=payload.length_mm,
        width_mm=payload.width_mm,
        multiplicidad=payload.multiplicidad,
        tiempo_ejecucion_estimado=payload.tiempo_ejecucion_estimado,
        product_id=product.id,
        nest_code="",
    )
    db.add(work_order)
    db.flush()
    work_order.nest_code = f"NEST-{work_order.id:06d}"

    for pieza in payload.piezas:
        db.add(WorkOrderPiece(work_order_id=work_order.id, **pieza.model_dump()))
    for recorte in payload.recortes:
        db.add(WorkOrderScrap(work_order_id=work_order.id, **recorte.model_dump()))

    db.commit()
    db.refresh(work_order)

    return _with_low_stock_warning(db, work_order)


@router.get("", response_model=list[WorkOrderSummaryOut])
def list_orders(
    status_filter: str | None = Query(None, alias="status"), db: Session = Depends(get_db)
):
    query = db.query(WorkOrder)
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    return query.order_by(WorkOrder.id.desc()).all()


@router.get("/by-nest-code/{nest_code}", response_model=WorkOrderOut)
def read_order_by_nest_code(nest_code: str, db: Session = Depends(get_db)):
    work_order = db.query(WorkOrder).filter(WorkOrder.nest_code == nest_code).first()
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de trabajo no encontrada")
    return _with_low_stock_warning(db, work_order)


@router.get("/{order_id}", response_model=WorkOrderOut)
def read_order(order_id: int, db: Session = Depends(get_db)):
    work_order = _get_order_or_404(db, order_id)
    return _with_low_stock_warning(db, work_order)


@router.get("/{order_id}/barcode")
def read_order_barcode(order_id: int, db: Session = Depends(get_db)):
    work_order = _get_order_or_404(db, order_id)
    png_bytes = generate_barcode_png(work_order.nest_code)
    return Response(content=png_bytes, media_type="image/png")


@router.post("/{order_id}/close", response_model=WorkOrderOut)
def close_order(order_id: int, db: Session = Depends(get_db)):
    work_order = _get_order_or_404(db, order_id)
    if work_order.status == "cerrada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La orden de trabajo ya se encuentra cerrada.",
        )

    config = get_or_create_system_config(db)
    product = db.query(Product).filter(Product.id == work_order.product_id).first()
    product.stock -= work_order.multiplicidad
    product.committed_stock -= work_order.multiplicidad

    for recorte in work_order.recortes:
        scrap_product = _find_matching_product(
            db, work_order.material, work_order.thickness_mm, recorte.largo_mm, recorte.ancho_mm, config.tolerance_mm
        )
        if scrap_product is None:
            db.add(
                Product(
                    material=work_order.material,
                    thickness_mm=work_order.thickness_mm,
                    length_mm=recorte.largo_mm,
                    width_mm=recorte.ancho_mm,
                    stock=recorte.cantidad,
                    committed_stock=0,
                    reorder_point=0,
                )
            )
        else:
            scrap_product.stock += recorte.cantidad

    work_order.status = "cerrada"
    db.commit()
    db.refresh(work_order)

    return _with_low_stock_warning(db, work_order)
