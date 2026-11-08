from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import List, Optional
import os

from database import get_db, init_db, engine
from models import Base, Empleado, Vacacion
from schemas import (
    EmpleadoCrear, EmpleadoRespuesta, EmpleadoEditar,
    VacacionSolicitud, VacacionRespuesta, VacacionResumen, VacacionResumenItem
)
from utils import calcular_dias_habiles, obtener_festivos, calcular_proxima_fecha_aniversario

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/salud")
def salud():
    return {"estado": "ok"}


@app.get("/api/departamentos")
def obtener_departamentos():
    return [
        "Tecnología",
        "Ventas",
        "Finanzas",
        "Recursos Humanos",
        "Operaciones"
    ]


@app.post("/api/empleados", response_model=EmpleadoRespuesta, status_code=201)
def crear_empleado(empleado: EmpleadoCrear, db: Session = Depends(get_db)):
    correo_lower = empleado.correo.lower()

    existente = db.query(Empleado).filter(
        Empleado.correo == correo_lower
    ).first()

    if existente:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado"
        )

    siguiente_numero = db.query(Empleado).count() + 1
    numero_empleado = f"EMP-{siguiente_numero:04d}"

    nuevo_empleado = Empleado(
        numero_empleado=numero_empleado,
        nombre=empleado.nombre,
        correo=correo_lower,
        puesto=empleado.puesto,
        departamento=empleado.departamento,
        fecha_ingreso=empleado.fecha_ingreso,
        estado="activo",
        creado_en=datetime.utcnow()
    )

    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)

    return EmpleadoRespuesta(
        id=nuevo_empleado.id,
        numero_empleado=nuevo_empleado.numero_empleado,
        nombre=nuevo_empleado.nombre,
        correo=nuevo_empleado.correo,
        puesto=nuevo_empleado.puesto,
        departamento=nuevo_empleado.departamento,
        fecha_ingreso=nuevo_empleado.fecha_ingreso,
        estado=nuevo_empleado.estado,
        fecha_baja=nuevo_empleado.fecha_baja,
        creado_en=nuevo_empleado.creado_en.isoformat()
    )


@app.get("/api/empleados", response_model=List[EmpleadoRespuesta])
def listar_empleados(db: Session = Depends(get_db)):
    empleados = db.query(Empleado).all()

    return [
        EmpleadoRespuesta(
            id=e.id,
            numero_empleado=e.numero_empleado,
            nombre=e.nombre,
            correo=e.correo,
            puesto=e.puesto,
            departamento=e.departamento,
            fecha_ingreso=e.fecha_ingreso,
            estado=e.estado,
            fecha_baja=e.fecha_baja,
            creado_en=e.creado_en.isoformat()
        )
        for e in empleados
    ]


@app.get("/api/empleados/{empleado_id}", response_model=EmpleadoRespuesta)
def obtener_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    return EmpleadoRespuesta(
        id=empleado.id,
        numero_empleado=empleado.numero_empleado,
        nombre=empleado.nombre,
        correo=empleado.correo,
        puesto=empleado.puesto,
        departamento=empleado.departamento,
        fecha_ingreso=empleado.fecha_ingreso,
        estado=empleado.estado,
        fecha_baja=empleado.fecha_baja,
        creado_en=empleado.creado_en.isoformat()
    )


@app.put("/api/empleados/{empleado_id}", response_model=EmpleadoRespuesta)
def editar_empleado(
    empleado_id: int,
    empleado_edit: EmpleadoEditar,
    db: Session = Depends(get_db)
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se puede editar a un empleado dado de baja"
        )

    empleado.nombre = empleado_edit.nombre
    empleado.puesto = empleado_edit.puesto
    empleado.departamento = empleado_edit.departamento

    db.commit()
    db.refresh(empleado)

    return EmpleadoRespuesta(
        id=empleado.id,
        numero_empleado=empleado.numero_empleado,
        nombre=empleado.nombre,
        correo=empleado.correo,
        puesto=empleado.puesto,
        departamento=empleado.departamento,
        fecha_ingreso=empleado.fecha_ingreso,
        estado=empleado.estado,
        fecha_baja=empleado.fecha_baja,
        creado_en=empleado.creado_en.isoformat()
    )


@app.get("/api/test-debug")
def test_debug():
    return {"status": "ok", "message": "Debug endpoint works"}


@app.post("/api/empleados/{empleado_id}/baja", status_code=200)
def dar_baja_empleado(empleado_id: int, db: Session = Depends(get_db)):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    empleado.estado = "baja"
    empleado.fecha_baja = date.today()

    db.commit()

    return {"mensaje": "Empleado dado de baja"}


@app.post("/api/empleados/{empleado_id}/vacaciones", response_model=VacacionRespuesta, status_code=201)
def solicitar_vacaciones(
    empleado_id: int,
    solicitud: VacacionSolicitud,
    db: Session = Depends(get_db)
):
    try:
        empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()

        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        fecha_inicio = solicitud.fecha_inicio
        fecha_fin = solicitud.fecha_fin

        if fecha_fin < fecha_inicio:
            raise HTTPException(
                status_code=422,
                detail="La fecha de fin no puede ser anterior a la de inicio"
            )

        if fecha_inicio.year != fecha_fin.year:
            raise HTTPException(
                status_code=422,
                detail="Las vacaciones se solicitan dentro de un mismo año"
            )

        fecha_aniversario = calcular_proxima_fecha_aniversario(
            empleado.fecha_ingreso,
            fecha_inicio.year
        )

        if fecha_inicio < fecha_aniversario:
            raise HTTPException(
                status_code=422,
                detail="Necesitas al menos un año de antigüedad para solicitar vacaciones"
            )

        dias_habiles = calcular_dias_habiles(fecha_inicio, fecha_fin)

        if dias_habiles == 0:
            raise HTTPException(
                status_code=422,
                detail="El periodo no incluye días hábiles"
            )

        todas_vacaciones = db.query(Vacacion).filter(
            Vacacion.empleado_id == empleado_id
        ).all()
        anio_str = str(fecha_inicio.year)
        vacaciones_anio = [v for v in todas_vacaciones if str(v.fecha_inicio).startswith(anio_str)]

        dias_usados = sum(v.dias_habiles for v in vacaciones_anio)
        dias_disponibles_antes = 12 - dias_usados

        if dias_habiles > dias_disponibles_antes:
            raise HTTPException(
                status_code=422,
                detail=f"La solicitud excede tus días disponibles: te quedan {dias_disponibles_antes}"
            )

        nueva_vacacion = Vacacion(
            empleado_id=empleado_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias_habiles=dias_habiles
        )

        db.add(nueva_vacacion)
        db.commit()
        db.refresh(nueva_vacacion)

        dias_disponibles_despues = dias_disponibles_antes - dias_habiles

        return VacacionRespuesta(
            id=nueva_vacacion.id,
            empleado_id=nueva_vacacion.empleado_id,
            fecha_inicio=nueva_vacacion.fecha_inicio,
            fecha_fin=nueva_vacacion.fecha_fin,
            dias_habiles=nueva_vacacion.dias_habiles,
            dias_disponibles=dias_disponibles_despues
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en solicitar_vacaciones: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/empleados/{empleado_id}/vacaciones", response_model=VacacionResumen)
def obtener_vacaciones(
    empleado_id: int,
    anio: int = Query(None),
    db: Session = Depends(get_db)
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if anio is None:
        anio = date.today().year

    todas_vacaciones = db.query(Vacacion).filter(
        Vacacion.empleado_id == empleado_id
    ).all()
    anio_str = f"{anio}"
    vacaciones = [v for v in todas_vacaciones if str(v.fecha_inicio).startswith(anio_str)]

    dias_usados = sum(v.dias_habiles for v in vacaciones)
    dias_disponibles = 12 - dias_usados

    solicitudes = [
        VacacionResumenItem(
            id=v.id,
            empleado_id=v.empleado_id,
            fecha_inicio=v.fecha_inicio,
            fecha_fin=v.fecha_fin,
            dias_habiles=v.dias_habiles
        )
        for v in vacaciones
    ]

    return VacacionResumen(
        anio=anio,
        dias_por_anio=12,
        dias_usados=dias_usados,
        dias_disponibles=dias_disponibles,
        solicitudes=solicitudes
    )
