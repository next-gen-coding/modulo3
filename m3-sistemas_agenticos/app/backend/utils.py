from datetime import date, timedelta
from typing import List


def calcular_proxima_fecha_aniversario(fecha_ingreso: date, anio: int) -> date:
    """Calcula el aniversario en un año, considerando 29 de febrero → 1 de marzo."""
    try:
        return fecha_ingreso.replace(year=anio)
    except ValueError:
        if fecha_ingreso.month == 2 and fecha_ingreso.day == 29:
            return date(anio, 3, 1)
        raise


def obtener_festivos(anio: int) -> List[date]:
    """Retorna lista de festivos del año según art. 74 LFT."""
    festivos = [
        date(anio, 1, 1),
        date(anio, 12, 25),
        date(anio, 5, 1),
        date(anio, 9, 16),
    ]

    if anio in [2024, 2030]:
        festivos.append(date(anio, 10, 1))

    def primer_lunes_de(mes: int) -> date:
        d = date(anio, mes, 1)
        dias_hasta_lunes = (7 - d.weekday()) % 7
        if dias_hasta_lunes == 0 and d.weekday() != 0:
            dias_hasta_lunes = 7
        return d + timedelta(days=dias_hasta_lunes)

    def tercer_lunes_de(mes: int) -> date:
        primer_lunes = primer_lunes_de(mes)
        return primer_lunes + timedelta(days=14)

    festivos.append(primer_lunes_de(2))
    festivos.append(tercer_lunes_de(3))
    festivos.append(tercer_lunes_de(11))

    return sorted([f for f in festivos if f.year == anio])


def calcular_dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula días hábiles (lunes-viernes sin festivos) entre dos fechas inclusive.
    """
    if fecha_inicio > fecha_fin:
        return 0

    festivos_inicio = obtener_festivos(fecha_inicio.year)
    festivos_fin = obtener_festivos(fecha_fin.year)
    festivos = set(festivos_inicio + festivos_fin)

    dias_habiles = 0
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_fin:
        es_lunes_viernes = fecha_actual.weekday() < 5
        no_es_festivo = fecha_actual not in festivos

        if es_lunes_viernes and no_es_festivo:
            dias_habiles += 1

        fecha_actual += timedelta(days=1)

    return dias_habiles
