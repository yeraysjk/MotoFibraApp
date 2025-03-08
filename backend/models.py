# backend/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class PiezaBasica(Base):
    __tablename__ = "piezas_basicas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    marca = Column(String, index=True)
    referencia = Column(String)
    cliente = Column(String)    # Valores permitidos: "MotoFibra", "S2Concept"
    categoria = Column(String)  # Valores permitidos: "guardabarros", "quillas", "depositos", "escopas", "frontal", "laterales", "colin"

    detalles = relationship("PiezaDetalles", back_populates="pieza", uselist=False)

class PiezaDetalles(Base):
    __tablename__ = "piezas_detalles"

    id = Column(Integer, primary_key=True, index=True)
    pieza_id = Column(Integer, ForeignKey("piezas_basicas.id"))
    tiempo_fabricacion = Column(Float)
    tiempo_pintado = Column(Float)
    tiempo_lijado = Column(Float)
    tiempo_masillado = Column(Float)
    costo = Column(Float)
    gasto_resina = Column(Float)

    pieza = relationship("PiezaBasica", back_populates="detalles")
