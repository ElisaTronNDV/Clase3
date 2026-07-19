from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True)
    tolerance_mm = Column(Float, nullable=False, default=1.0)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    material = Column(String, nullable=False, index=True)
    thickness_mm = Column(Float, nullable=False)
    length_mm = Column(Float, nullable=False)
    width_mm = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    committed_stock = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=0)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    nest_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False, default="vigente")
    nombre_nest = Column(String, nullable=True)
    material = Column(String, nullable=False)
    thickness_mm = Column(Float, nullable=False)
    length_mm = Column(Float, nullable=False)
    width_mm = Column(Float, nullable=False)
    multiplicidad = Column(Integer, nullable=False)
    tiempo_ejecucion_estimado = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    piezas = relationship("WorkOrderPiece", cascade="all, delete-orphan")
    recortes = relationship("WorkOrderScrap", cascade="all, delete-orphan")


class WorkOrderPiece(Base):
    __tablename__ = "work_order_pieces"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    pieza = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)


class WorkOrderScrap(Base):
    __tablename__ = "work_order_scraps"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    pieza = Column(String, nullable=False)
    largo_mm = Column(Float, nullable=False)
    ancho_mm = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
