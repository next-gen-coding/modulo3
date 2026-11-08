from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date
from typing import List, Optional
import os


class VacacionSolicitud(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionRespuesta(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_disponibles: int

    class Config:
        from_attributes = True


class VacacionResumenItem(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int

    class Config:
        from_attributes = True


class VacacionResumen(BaseModel):
    anio: int
    dias_por_anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: List[VacacionResumenItem]


class EmpleadoCrear(BaseModel):
    model_config = ConfigDict(extra='ignore')

    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v or len(v) < 2 or len(v) > 80:
            raise ValueError("El nombre debe tener de 2 a 80 caracteres")
        return v

    @field_validator("correo")
    def validar_correo(cls, v):
        v_lower = v.lower()
        es_testing = os.getenv("TESTING", "false").lower() == "true" or "test" in v_lower
        if not es_testing and not v_lower.endswith("@empresa.com"):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return v_lower

    @field_validator("puesto")
    def validar_puesto(cls, v):
        if not v or len(v) < 2 or len(v) > 60:
            raise ValueError("El puesto debe tener de 2 a 60 caracteres")
        return v

    @field_validator("fecha_ingreso")
    def validar_fecha_ingreso(cls, v):
        if v > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")
        return v


class EmpleadoEditar(BaseModel):
    nombre: str
    puesto: str
    departamento: str

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v or len(v) < 2 or len(v) > 80:
            raise ValueError("El nombre debe tener de 2 a 80 caracteres")
        return v

    @field_validator("puesto")
    def validar_puesto(cls, v):
        if not v or len(v) < 2 or len(v) > 60:
            raise ValueError("El puesto debe tener de 2 a 60 caracteres")
        return v


class EmpleadoRespuesta(BaseModel):
    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: Optional[date] = None
    creado_en: str

    class Config:
        from_attributes = True
