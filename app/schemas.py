from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SystemConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tolerance_mm: float


class SystemConfigUpdate(BaseModel):
    tolerance_mm: float = Field(gt=0)


class ProductCreate(BaseModel):
    material: str = Field(min_length=1)
    thickness_mm: float = Field(gt=0)
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    stock: int = Field(ge=0)
    reorder_point: int = Field(ge=0)


class ProductUpdate(BaseModel):
    material: str = Field(min_length=1)
    thickness_mm: float = Field(gt=0)
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    stock: int = Field(ge=0)
    reorder_point: int = Field(ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material: str
    thickness_mm: float
    length_mm: float
    width_mm: float
    stock: int
    committed_stock: int
    reorder_point: int


class ExtractedPiece(BaseModel):
    pieza: str
    descripcion: str
    cantidad: int


class ExtractedScrap(BaseModel):
    pieza: str
    largo_mm: float
    ancho_mm: float
    cantidad: int


class ExtractedNest(BaseModel):
    page_index: int
    nombre_nest: str | None
    multiplicidad: int | None
    largo_mm: float | None
    ancho_mm: float | None
    espesor_mm: float | None
    material: str | None
    tiempo_ejecucion_estimado: str | None
    piezas: list[ExtractedPiece]
    recortes: list[ExtractedScrap]


class PdfExtractionResult(BaseModel):
    nests: list[ExtractedNest]


class WorkOrderPieceIn(BaseModel):
    pieza: str
    descripcion: str
    cantidad: int = Field(ge=1)


class WorkOrderScrapIn(BaseModel):
    pieza: str
    largo_mm: float = Field(gt=0)
    ancho_mm: float = Field(gt=0)
    cantidad: int = Field(ge=1)


class WorkOrderCreate(BaseModel):
    nombre_nest: str | None = None
    material: str = Field(min_length=1)
    thickness_mm: float = Field(gt=0)
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    multiplicidad: int = Field(ge=1)
    tiempo_ejecucion_estimado: str | None = None
    piezas: list[WorkOrderPieceIn] = Field(default_factory=list)
    recortes: list[WorkOrderScrapIn] = Field(default_factory=list)
    create_missing_product: bool = False


class WorkOrderPieceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pieza: str
    descripcion: str
    cantidad: int


class WorkOrderScrapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pieza: str
    largo_mm: float
    ancho_mm: float
    cantidad: int


class WorkOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nest_code: str
    status: str
    nombre_nest: str | None
    material: str
    thickness_mm: float
    length_mm: float
    width_mm: float
    multiplicidad: int
    tiempo_ejecucion_estimado: str | None
    low_stock_warning: bool
    piezas: list[WorkOrderPieceOut]
    recortes: list[WorkOrderScrapOut]


class WorkOrderSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nest_code: str
    status: str
    material: str
    thickness_mm: float
    length_mm: float
    width_mm: float
    multiplicidad: int
    created_at: datetime
