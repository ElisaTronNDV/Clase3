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
