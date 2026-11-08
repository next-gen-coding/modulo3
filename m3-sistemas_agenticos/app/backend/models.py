from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True)
    numero_empleado = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String, nullable=False, unique=True, index=True)
    puesto = Column(String(60), nullable=False)
    departamento = Column(String, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    estado = Column(String, default="activo", nullable=False)
    fecha_baja = Column(Date, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    vacaciones = relationship("Vacacion", back_populates="empleado", cascade="all, delete-orphan")


class Vacacion(Base):
    __tablename__ = "vacaciones"

    id = Column(Integer, primary_key=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_habiles = Column(Integer, nullable=False)

    empleado = relationship("Empleado", back_populates="vacaciones")

    __table_args__ = (
        Index("idx_empleado_anio", "empleado_id", "fecha_inicio"),
    )
